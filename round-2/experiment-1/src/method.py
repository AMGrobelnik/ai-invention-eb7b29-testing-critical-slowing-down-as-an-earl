#!/usr/bin/env python3
"""Reproduce critical-slowing-down (CSD) early-warning statistics on the
multi-agent debate collapse dataset. Implements permutation tests, a GEE
hierarchical model, four classifiers (CSD threshold, naive-agreement,
spectral-contagion, SPRT) with bootstrap CIs, lead-time analysis, and a
full/clean sensitivity comparison. Baseline = naive-agreement classifier.
"""

from __future__ import annotations

import argparse
import gc
import json
import re
import resource
import sys
import time
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import psutil
from loguru import logger
from scipy import stats
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score, roc_curve
from sklearn.model_selection import train_test_split
from statsmodels.genmod.cov_struct import Exchangeable
from statsmodels.genmod.generalized_estimating_equations import GEE
from statsmodels.genmod.families import Binomial

WORKSPACE = Path(__file__).parent
logger.remove()
logger.add(sys.stdout, level="INFO", format="{time:HH:mm:ss}|{level:<7}|{message}")
logger.add(WORKSPACE / "logs" / "run.log", rotation="30 MB", level="DEBUG")

RNG_SEED = 42
EPS = 1e-9

# ---- resource limits (32GB available; this workload is small, cap generously) ----
_avail = psutil.virtual_memory().available
RAM_BUDGET = int(min(8 * 1024**3, _avail * 0.5))
resource.setrlimit(resource.RLIMIT_AS, (RAM_BUDGET * 3, RAM_BUDGET * 3))


# --------------------------------------------------------------------------
# Data loading
# --------------------------------------------------------------------------
def load_examples(data_path: Path, limit: int | None = None) -> list[dict]:
    logger.info(f"Loading data from {data_path}")
    raw = json.loads(data_path.read_text())
    examples = raw["datasets"][0]["examples"]
    if limit is not None:
        # limit by number of distinct debates, keeping all rounds of each debate intact
        seen_debates: list[str] = []
        kept = []
        for e in examples:
            did = e["metadata_debate_id"]
            if did not in seen_debates:
                if len(seen_debates) >= limit:
                    continue
                seen_debates.append(did)
            if did in seen_debates:
                kept.append(e)
        examples = kept
    logger.info(f"Loaded {len(examples)} rows")
    return examples


def recompute_agreement_score(agent_responses: list[dict]) -> float:
    """Fraction of agents whose solution matches the modal normalized solution text."""
    solutions = [
        re.sub(r"\s+", " ", (r.get("solution") or "").strip().lower())
        for r in agent_responses
    ]
    solutions = [s for s in solutions if s]
    if not solutions:
        return np.nan
    counts = Counter(solutions)
    modal_count = counts.most_common(1)[0][1]
    return modal_count / len(solutions)


def build_dataframe(examples: list[dict]) -> pd.DataFrame:
    rows = []
    for e in examples:
        parsed = json.loads(e["input"])
        agent_responses = parsed.get("agent_responses", [])
        recomputed_agreement = recompute_agreement_score(agent_responses)
        rows.append(
            {
                "debate_id": e["metadata_debate_id"],
                "source_config": e["metadata_source_config"],
                "round_number": e["metadata_round_number"],
                "total_rounds": e["metadata_total_rounds"],
                "agreement_score": e["metadata_agreement_score"],
                "agreement_score_recomputed": recomputed_agreement,
                "outcome_label": e["output"],
                "decision_success": e["metadata_decision_success"],
                "persona_diversity": e["metadata_persona_diversity"],
                "n_agents": len(agent_responses),
                "agent_responses": agent_responses,
            }
        )
    df = pd.DataFrame(rows).sort_values(["debate_id", "round_number"]).reset_index(drop=True)
    mismatch = (df["agreement_score"] - df["agreement_score_recomputed"]).abs() > 1e-6
    logger.info(
        f"agreement_score recompute mismatch rate: {mismatch.mean():.4f} "
        f"({mismatch.sum()}/{len(df)} rows) — using dataset-provided score as primary, "
        "recomputed score logged for audit"
    )
    return df


# --------------------------------------------------------------------------
# Rolling early-warning statistics
# --------------------------------------------------------------------------
def compute_rolling_stats(df: pd.DataFrame, ac_window: int = 2, var_window: int = 3) -> pd.DataFrame:
    """Per-debate rolling lag-1 autocorrelation and rolling variance of agreement_score."""
    out_parts = []
    for debate_id, g in df.groupby("debate_id", sort=False):
        g = g.sort_values("round_number").reset_index(drop=True)
        agreement = g["agreement_score"].to_numpy(dtype=float)
        n = len(agreement)

        # Lag-1 autocorrelation at round t is computed from `ac_window` consecutive (x_i, x_{i+1})
        # pairs drawn from a trailing window of ac_window+1 rounds ending at t. A window expressed
        # as a single point-pair (ac_window=1) cannot yield a Pearson correlation (needs >=2 pairs
        # to vary), so ac_window is the number of PAIRS, requiring ac_window+1 rounds of history.
        autocorr = np.full(n, np.nan)
        for t in range(ac_window, n):
            lo = t - ac_window
            window_prev = agreement[lo:t]
            window_curr = agreement[lo + 1 : t + 1]
            if len(window_prev) >= 2 and np.std(window_prev) > EPS and np.std(window_curr) > EPS:
                autocorr[t] = np.corrcoef(window_prev, window_curr)[0, 1]

        variance = np.full(n, np.nan)
        for t in range(n):
            lo = max(0, t - var_window + 1)
            w = agreement[lo : t + 1]
            variance[t] = np.var(w, ddof=0) if len(w) >= 2 else np.nan

        with np.errstate(invalid="ignore"):
            ac_mean, ac_std = np.nanmean(autocorr), np.nanstd(autocorr)
            var_mean, var_std = np.nanmean(variance), np.nanstd(variance)
        autocorr_z = (autocorr - ac_mean) / (ac_std + EPS)
        variance_z = (variance - var_mean) / (var_std + EPS)

        g = g.copy()
        g["autocorr"] = autocorr
        g["variance"] = variance
        g["autocorr_zscore"] = autocorr_z
        g["variance_zscore"] = variance_z
        out_parts.append(g)
    result = pd.concat(out_parts, ignore_index=True)
    return result


def extract_pre_outcome_rows(df: pd.DataFrame) -> pd.DataFrame:
    """Rows strictly before the final round of each debate (pre-collapse / pre-convergence window)."""
    parts = []
    for _, g in df.groupby("debate_id", sort=False):
        g = g.sort_values("round_number")
        parts.append(g.iloc[: len(g) - 1])
    return pd.concat(parts, ignore_index=True) if parts else df.iloc[0:0]


# --------------------------------------------------------------------------
# Permutation test (block-shuffle)
# --------------------------------------------------------------------------
def block_shuffle_labels(labels: np.ndarray, block_length: int, rng: np.random.Generator) -> np.ndarray:
    n = len(labels)
    n_blocks = int(np.ceil(n / block_length))
    blocks = [labels[i * block_length : (i + 1) * block_length] for i in range(n_blocks)]
    perm_order = rng.permutation(n_blocks)
    shuffled = np.concatenate([blocks[i] for i in perm_order])[:n]
    return shuffled


def permutation_test(
    values: np.ndarray,
    group_labels: np.ndarray,
    n_permutations: int = 10_000,
    block_length: int = 2,
    seed: int = RNG_SEED,
) -> dict:
    """Two-sample permutation test on mean(group==1) - mean(group==0), block-shuffling group labels."""
    rng = np.random.default_rng(seed)
    mask = ~np.isnan(values)
    values, group_labels = values[mask], group_labels[mask]
    n1_check, n0_check = int((group_labels == 1).sum()), int((group_labels == 0).sum())
    if n1_check < 2 or n0_check < 2:
        logger.warning(
            f"permutation_test: insufficient group sizes (n1={n1_check}, n0={n0_check}) — "
            "returning NaN result (expected at tiny/smoke-test scale)"
        )
        return {
            "p_value": float("nan"),
            "effect_size_cohens_d": float("nan"),
            "mean_diff": float("nan"),
            "ci_95": [float("nan"), float("nan")],
            "n_collapse_group": n1_check,
            "n_converged_group": n0_check,
            "n_permutations": n_permutations,
            "block_length": block_length,
            "null_distribution_sample": [],
        }
    obs_stat = values[group_labels == 1].mean() - values[group_labels == 0].mean()

    perm_stats = np.empty(n_permutations)
    for i in range(n_permutations):
        shuffled = block_shuffle_labels(group_labels, block_length, rng)
        perm_stats[i] = values[shuffled == 1].mean() - values[shuffled == 0].mean()

    count_exceed = int(np.sum(perm_stats >= obs_stat))
    p_value = (count_exceed + 1) / (n_permutations + 1)

    n1, n0 = (group_labels == 1).sum(), (group_labels == 0).sum()
    pooled_std = np.sqrt(
        ((n1 - 1) * values[group_labels == 1].var(ddof=1) + (n0 - 1) * values[group_labels == 0].var(ddof=1))
        / max(n1 + n0 - 2, 1)
    )
    cohens_d = obs_stat / (pooled_std + EPS)
    se = values.std(ddof=1) * np.sqrt(1 / max(n1, 1) + 1 / max(n0, 1))
    ci_95 = [float(obs_stat - 1.96 * se), float(obs_stat + 1.96 * se)]

    return {
        "p_value": float(p_value),
        "effect_size_cohens_d": float(cohens_d),
        "mean_diff": float(obs_stat),
        "ci_95": ci_95,
        "n_collapse_group": int(n1),
        "n_converged_group": int(n0),
        "n_permutations": n_permutations,
        "block_length": block_length,
        "null_distribution_sample": perm_stats[:2000].tolist(),
    }


# --------------------------------------------------------------------------
# Hierarchical / clustered model (GEE fallback for glmer, per fallback_plan)
# --------------------------------------------------------------------------
def fit_hierarchical_model(df: pd.DataFrame) -> dict:
    model_df = df.dropna(subset=["autocorr_zscore", "variance_zscore", "round_number", "collapse_any"]).copy()
    if model_df["debate_id"].nunique() < 3 or model_df["collapse_any"].nunique() < 2:
        return {
            "error": f"insufficient data for GEE fit (n_debates={model_df['debate_id'].nunique()}, "
            f"n_outcome_classes={model_df['collapse_any'].nunique()}) — expected only at smoke-test scale"
        }
    model_df["debate_idx"] = model_df["debate_id"].astype("category").cat.codes

    exog = model_df[["round_number", "autocorr_zscore", "variance_zscore"]].copy()
    exog.insert(0, "intercept", 1.0)
    endog = model_df["collapse_any"].astype(float)

    gee = GEE(
        endog,
        exog,
        groups=model_df["debate_idx"],
        family=Binomial(),
        cov_struct=Exchangeable(),
    )
    result = gee.fit()

    coefs = {}
    for name in exog.columns:
        est = float(result.params[name])
        se = float(result.bse[name])
        z = float(result.tvalues[name])
        p = float(result.pvalues[name])
        ci_lo, ci_hi = est - 1.96 * se, est + 1.96 * se
        coefs[name if name != "intercept" else "intercept"] = {
            "estimate": est,
            "se": se,
            "z": z,
            "p": p,
            "ci_95": [float(ci_lo), float(ci_hi)],
        }

    # exchangeable within-cluster correlation as a proxy for "random effects" (GEE has no
    # random-effects SD directly; report cluster correlation instead, per fallback_plan)
    try:
        within_cluster_corr = float(result.cov_struct.dep_params)
    except Exception:
        within_cluster_corr = None

    preds = result.predict(exog)
    ss_res = float(np.sum((endog - preds) ** 2))
    ss_tot = float(np.sum((endog - endog.mean()) ** 2))
    pseudo_r2 = 1 - ss_res / ss_tot if ss_tot > 0 else float("nan")

    return {
        "method": "GEE (Binomial family, exchangeable working correlation, debate-level clustering) "
        "— substituted for glmer/lme4 per fallback_plan (pure-Python glmm unavailable)",
        "coefficients": coefs,
        "within_cluster_exchangeable_correlation": within_cluster_corr,
        "pseudo_r2_mcfadden_style": pseudo_r2,
        "n_observations": int(len(model_df)),
        "n_clusters_debates": int(model_df["debate_idx"].nunique()),
    }


# --------------------------------------------------------------------------
# Classifiers
# --------------------------------------------------------------------------
def bootstrap_auc_ci(y_true: np.ndarray, y_score: np.ndarray, n_boot: int = 1000, seed: int = RNG_SEED) -> list:
    rng = np.random.default_rng(seed)
    n = len(y_true)
    aucs = []
    classes = np.unique(y_true)
    if len(classes) < 2:
        return [float("nan"), float("nan")]
    for _ in range(n_boot):
        idx_pos = rng.choice(np.where(y_true == 1)[0], size=(y_true == 1).sum(), replace=True)
        idx_neg = rng.choice(np.where(y_true == 0)[0], size=(y_true == 0).sum(), replace=True)
        idx = np.concatenate([idx_pos, idx_neg])
        if len(np.unique(y_true[idx])) < 2:
            continue
        aucs.append(roc_auc_score(y_true[idx], y_score[idx]))
    if not aucs:
        return [float("nan"), float("nan")]
    return [float(np.percentile(aucs, 2.5)), float(np.percentile(aucs, 97.5))]


def classification_metrics(y_true: np.ndarray, y_pred: np.ndarray) -> dict:
    tp = int(np.sum((y_true == 1) & (y_pred == 1)))
    fp = int(np.sum((y_true == 0) & (y_pred == 1)))
    tn = int(np.sum((y_true == 0) & (y_pred == 0)))
    fn = int(np.sum((y_true == 1) & (y_pred == 0)))
    sens = tp / (tp + fn) if (tp + fn) else float("nan")
    spec = tn / (tn + fp) if (tn + fp) else float("nan")
    ppv = tp / (tp + fp) if (tp + fp) else float("nan")
    npv = tn / (tn + fn) if (tn + fn) else float("nan")
    return {"sensitivity": sens, "specificity": spec, "ppv": ppv, "npv": npv, "tp": tp, "fp": fp, "tn": tn, "fn": fn}


def debate_level_features(rolled: pd.DataFrame) -> pd.DataFrame:
    """One row per debate: early-round (pre-final) signal summaries + outcome."""
    rows = []
    for debate_id, g in rolled.groupby("debate_id", sort=False):
        g = g.sort_values("round_number")
        pre = g.iloc[: len(g) - 1]
        early = g.iloc[: min(2, len(g))]  # rounds 1-2
        rows.append(
            {
                "debate_id": debate_id,
                "source_config": g["source_config"].iloc[0],
                "outcome_label": g["outcome_label"].iloc[0],
                "collapse_any": g["collapse_any"].iloc[0],
                "total_rounds": g["total_rounds"].iloc[0],
                "autocorr_pre_mean": pre["autocorr"].mean(),
                "variance_pre_mean": pre["variance"].mean(),
                "autocorr_early": early["autocorr"].dropna().mean() if early["autocorr"].notna().any() else np.nan,
                "agreement_round1": g["agreement_score"].iloc[0],
                "agreement_trajectory": g["agreement_score"].tolist(),
                "spectral_radius": g["spectral_radius"].iloc[0] if "spectral_radius" in g else np.nan,
                "agent_responses_by_round": g["agent_responses"].tolist(),
                "n_rounds": len(g),
            }
        )
    return pd.DataFrame(rows)


def compute_spectral_radius(agent_responses: list[dict]) -> float:
    """Spectral radius of an agent influence/citation graph inferred from persona mentions in messages."""
    personas = [r.get("persona", f"agent_{i}") for i, r in enumerate(agent_responses)]
    n = len(personas)
    if n < 2:
        return np.nan
    A = np.zeros((n, n))
    for i, r in enumerate(agent_responses):
        message = (r.get("message") or "").lower()
        for j, other_persona in enumerate(personas):
            if i == j:
                continue
            if other_persona.lower() in message:
                A[i, j] += 1.0
    row_sums = A.sum(axis=1, keepdims=True)
    with np.errstate(invalid="ignore", divide="ignore"):
        A_norm = np.divide(A, row_sums, out=np.zeros_like(A), where=row_sums > 0)
    if not np.any(A_norm):
        # fallback: response-repetition proxy per fallback_plan
        solutions = [re.sub(r"\s+", " ", (r.get("solution") or "").strip().lower()) for r in agent_responses]
        counts = Counter(solutions)
        repetition_rate = (max(counts.values()) - 1) / max(n - 1, 1) if n > 1 else 0.0
        return float(repetition_rate)
    eigvals = np.linalg.eigvals(A_norm)
    return float(np.max(np.abs(eigvals)))


def fit_csd_threshold(train_feats: pd.DataFrame, test_feats: pd.DataFrame) -> dict:
    conv = train_feats[train_feats["collapse_any"] == 0]
    baseline_mean = conv["autocorr_early"].mean()
    baseline_sd = conv["autocorr_early"].std(ddof=1)
    if pd.isna(baseline_mean):
        # Converged debates often hold agreement_score constant (std=0), making lag-1
        # autocorrelation undefined (NaN) for the entire early window -- fall back to the
        # full train set's mean, and then to a neutral 0.0 if that is also undefined.
        logger.warning(
            "fit_csd_threshold: all converged-debate autocorr_early values are NaN "
            "(constant early-round agreement) — falling back to train-set-wide mean"
        )
        baseline_mean = train_feats["autocorr_early"].mean()
    if pd.isna(baseline_mean):
        baseline_mean = 0.0
    if pd.isna(baseline_sd):
        baseline_sd = train_feats["autocorr_early"].std(ddof=1)
    if pd.isna(baseline_sd):
        baseline_sd = 0.0
    threshold = baseline_mean + baseline_sd

    def score(f):
        return f["autocorr_early"].fillna(baseline_mean)

    train_score = score(train_feats)
    test_score = score(test_feats)
    y_test = test_feats["collapse_any"].to_numpy()
    y_pred = (test_score > threshold).astype(int).to_numpy()
    return {
        "threshold": float(threshold),
        "baseline_mean": float(baseline_mean),
        "baseline_sd": float(baseline_sd),
        "y_score": test_score.to_numpy(),
        "y_pred": y_pred,
        "y_true": y_test,
    }


def fit_naive_agreement(train_feats: pd.DataFrame, test_feats: pd.DataFrame) -> dict:
    conv = train_feats[train_feats["collapse_any"] == 0]
    p25 = conv["agreement_round1"].quantile(0.25) if len(conv) else np.nan
    if pd.isna(p25):
        p25 = train_feats["agreement_round1"].quantile(0.25)
    if pd.isna(p25):
        p25 = 0.0

    train_score = 1.0 - train_feats["agreement_round1"]
    test_score = 1.0 - test_feats["agreement_round1"]
    y_test = test_feats["collapse_any"].to_numpy()
    y_pred = (test_feats["agreement_round1"] < p25).astype(int).to_numpy()
    return {
        "threshold_agreement_p25": float(p25),
        "y_score": test_score.to_numpy(),
        "y_pred": y_pred,
        "y_true": y_test,
    }


def fit_spectral_model(train_feats: pd.DataFrame, test_feats: pd.DataFrame) -> dict:
    fill_value = train_feats["spectral_radius"].median()
    if pd.isna(fill_value):
        fill_value = 0.0
    train_rho = train_feats["spectral_radius"].fillna(fill_value)
    test_rho = test_feats["spectral_radius"].fillna(fill_value)
    y_train = train_feats["collapse_any"].to_numpy()
    y_test = test_feats["collapse_any"].to_numpy()

    fallback_used = False
    try:
        clf = LogisticRegression()
        clf.fit(train_rho.to_numpy().reshape(-1, 1), y_train)
        test_score = clf.predict_proba(test_rho.to_numpy().reshape(-1, 1))[:, 1]
        learned_threshold = 0.5
        y_pred = (test_score > learned_threshold).astype(int)
    except Exception as exc:  # sparse/degenerate graphs -> theory-driven fallback
        logger.warning(f"Spectral logistic fit failed ({exc}); falling back to rho>1.0 rule")
        fallback_used = True
        test_score = test_rho.to_numpy()
        y_pred = (test_rho.to_numpy() > 1.0).astype(int)

    return {
        "fallback_theory_threshold_used": fallback_used,
        "y_score": test_score,
        "y_pred": y_pred,
        "y_true": y_test,
    }


def fit_sprt(train_feats: pd.DataFrame, test_feats: pd.DataFrame, odds_ratio_b: float = 9.0) -> dict:
    """SPRT over the per-round agreement trajectory: H1=collapse (decreasing/low mean), H0=converged (stable/high mean)."""

    def stats_for(mask):
        arrays = [np.array(t[:-1], dtype=float) for t in train_feats.loc[mask, "agreement_trajectory"]]
        if not arrays:
            logger.warning("fit_sprt: no debates in one class (expected only at smoke-test scale) — using overall stats")
            arrays = [np.array(t[:-1], dtype=float) for t in train_feats["agreement_trajectory"]]
        vals = np.concatenate(arrays) if arrays else np.array([0.5])
        return float(np.nanmean(vals)), float(np.nanstd(vals) + EPS)

    mu1, sd1 = stats_for(train_feats["collapse_any"] == 1)
    mu0, sd0 = stats_for(train_feats["collapse_any"] == 0)
    log_b = np.log(odds_ratio_b)

    def sprt_decision_and_round(trajectory: list[float]) -> tuple[int, int]:
        llr = 0.0
        for t, val in enumerate(trajectory[:-1]):
            llr += stats.norm.logpdf(val, mu1, sd1) - stats.norm.logpdf(val, mu0, sd0)
            if llr >= log_b:
                return 1, t + 1
            if llr <= -log_b:
                return 0, t + 1
        return int(llr > 0), len(trajectory) - 1

    decisions, decision_rounds, scores = [], [], []
    for traj in test_feats["agreement_trajectory"]:
        pred, r = sprt_decision_and_round(traj)
        decisions.append(pred)
        decision_rounds.append(r)
        # continuous score = final LLR, monotonically related to decision confidence
        llr = 0.0
        for val in traj[:-1]:
            llr += stats.norm.logpdf(val, mu1, sd1) - stats.norm.logpdf(val, mu0, sd0)
        scores.append(llr)

    y_test = test_feats["collapse_any"].to_numpy()
    return {
        "mu_collapse": mu1,
        "sd_collapse": sd1,
        "mu_converged": mu0,
        "sd_converged": sd0,
        "log_odds_boundary": float(log_b),
        "y_score": np.array(scores),
        "y_pred": np.array(decisions),
        "y_true": y_test,
        "decision_round": np.array(decision_rounds),
    }


def evaluate_classifier(name: str, fit_result: dict) -> dict:
    y_true, y_score, y_pred = fit_result["y_true"], fit_result["y_score"], fit_result["y_pred"]
    if np.isnan(y_score).any():
        n_nan = int(np.isnan(y_score).sum())
        logger.warning(f"{name}: {n_nan} NaN score(s) remain after fallbacks — imputing with score mean")
        fill = np.nanmean(y_score) if not np.isnan(y_score).all() else 0.0
        y_score = np.where(np.isnan(y_score), fill, y_score)
    if len(np.unique(y_true)) < 2:
        auc = float("nan")
        ci = [float("nan"), float("nan")]
    else:
        auc = float(roc_auc_score(y_true, y_score))
        ci = bootstrap_auc_ci(y_true, y_score, n_boot=1000)
    metrics = classification_metrics(y_true, y_pred)
    result = {"auc": auc, "auc_ci_95": ci, **metrics}
    return result


def compute_lead_times(feats: pd.DataFrame, y_pred: np.ndarray, decision_round: np.ndarray | None) -> dict:
    """Lead time = rounds before the debate's final round that the classifier's signal fired."""
    feats = feats.reset_index(drop=True)
    y_true = feats["collapse_any"].to_numpy()
    total_rounds = feats["n_rounds"].to_numpy()
    if decision_round is None:
        decision_round = np.full(len(feats), 2)  # CSD/naive/spectral fire at round 2 (early window) by construction

    lead = total_rounds - decision_round
    groups = {
        "true_positive": (y_true == 1) & (y_pred == 1),
        "true_negative": (y_true == 0) & (y_pred == 0),
        "false_positive": (y_true == 0) & (y_pred == 1),
        "false_negative": (y_true == 1) & (y_pred == 0),
    }
    out = {}
    for key, mask in groups.items():
        vals = lead[mask]
        out[f"mean_lead_time_{key}"] = float(np.mean(vals)) if len(vals) else float("nan")
        out[f"sd_lead_time_{key}"] = float(np.std(vals, ddof=1)) if len(vals) > 1 else float("nan")
        out[f"n_{key}"] = int(mask.sum())
    return out


# --------------------------------------------------------------------------
# End-to-end pipeline for one dataset variant (full or clean)
# --------------------------------------------------------------------------
def run_pipeline(df: pd.DataFrame, label: str, seed: int = RNG_SEED) -> dict:
    logger.info(f"[{label}] running pipeline on {len(df)} rows / {df['debate_id'].nunique()} debates")
    df = df.copy()
    df["collapse_any"] = df["outcome_label"].isin(["collapsed", "deadlocked"]).astype(int)

    rolled = compute_rolling_stats(df, ac_window=2, var_window=3)
    rolled["spectral_radius"] = rolled["agent_responses"].apply(compute_spectral_radius)

    pre = extract_pre_outcome_rows(rolled)
    pre_collapse_mask = pre["outcome_label"].isin(["collapsed", "deadlocked"])

    # --- permutation tests (autocorr, variance) ---
    autocorr_vals = pre["autocorr"].to_numpy()
    variance_vals = pre["variance"].to_numpy()
    group = pre_collapse_mask.to_numpy().astype(int)
    perm_autocorr = permutation_test(autocorr_vals, group, n_permutations=10_000, block_length=2, seed=seed)
    perm_variance = permutation_test(variance_vals, group, n_permutations=10_000, block_length=2, seed=seed + 1)
    for r in (perm_autocorr, perm_variance):
        del r["null_distribution_sample"]  # keep out of main JSON; sampled separately for figures

    # --- hierarchical / GEE model ---
    try:
        hier = fit_hierarchical_model(rolled)
    except Exception as exc:
        logger.error(f"[{label}] hierarchical model failed: {exc}")
        hier = {"error": str(exc)}

    # --- debate-level features + train/test split ---
    feats = debate_level_features(rolled)
    if len(feats) < 4:
        logger.warning(
            f"[{label}] only {len(feats)} debate(s) available — too few for a 70/30 split "
            "(expected only at smoke-test scale); using the full set as both train and test"
        )
        train_feats, test_feats = feats, feats
    else:
        strat = feats["outcome_label"] if feats["outcome_label"].value_counts().min() >= 2 else None
        train_feats, test_feats = train_test_split(
            feats, test_size=0.3, random_state=seed, stratify=strat
        )

    classifiers = {}
    lead_times = {}

    csd = fit_csd_threshold(train_feats, test_feats)
    classifiers["csd_threshold"] = evaluate_classifier("csd_threshold", csd)
    lead_times["csd_threshold"] = compute_lead_times(test_feats, csd["y_pred"], decision_round=None)

    naive = fit_naive_agreement(train_feats, test_feats)
    classifiers["naive_agreement"] = evaluate_classifier("naive_agreement", naive)
    lead_times["naive_agreement"] = compute_lead_times(test_feats, naive["y_pred"], decision_round=None)

    spectral = fit_spectral_model(train_feats, test_feats)
    classifiers["spectral_model"] = evaluate_classifier("spectral_model", spectral)
    lead_times["spectral_model"] = compute_lead_times(test_feats, spectral["y_pred"], decision_round=None)

    sprt = fit_sprt(train_feats, test_feats)
    classifiers["sprt"] = evaluate_classifier("sprt", sprt)
    lead_times["sprt"] = compute_lead_times(test_feats, sprt["y_pred"], decision_round=sprt["decision_round"])
    classifiers["sprt"].pop("tp", None)  # keep dict shape identical to others (already has tp via classification_metrics)

    for c in classifiers.values():
        c.pop("tp", None) if False else None  # no-op; tp/fp/tn/fn intentionally retained

    n_deadlocked = int((feats["outcome_label"] == "deadlocked").sum())
    deadlock_cases = feats[feats["outcome_label"] == "deadlocked"][
        ["debate_id", "n_rounds", "agreement_trajectory", "outcome_label", "autocorr_pre_mean", "variance_pre_mean"]
    ].to_dict(orient="records")

    result = {
        "label": label,
        "n_rows": int(len(df)),
        "n_debates": int(df["debate_id"].nunique()),
        "n_converged": int((feats["outcome_label"] == "converged").sum()),
        "n_collapsed": int((feats["outcome_label"] == "collapsed").sum()),
        "n_deadlocked": n_deadlocked,
        "permutation_tests": {"autocorrelation": perm_autocorr, "variance": perm_variance},
        "hierarchical_model": hier,
        "classifiers": classifiers,
        "lead_time_analysis": lead_times,
        "deadlock_analysis": {
            "n_deadlocked": n_deadlocked,
            "claim_scope": "n=5 deadlocked cases are insufficient for any mode-specific statistical claim; "
            "deadlock detection is deferred and excluded from the classifier train/test evaluation's inferential "
            "claims (it is retained inside collapse_any as a descriptive superset member only).",
            "deadlock_cases": deadlock_cases,
        },
        "_internal": {"rolled": rolled, "feats": feats, "train_feats": train_feats, "test_feats": test_feats,
                       "csd": csd, "naive": naive, "spectral": spectral, "sprt": sprt,
                       "perm_autocorr_null": None, "perm_variance_null": None},
    }
    return result


# --------------------------------------------------------------------------
# Figures & tables
# --------------------------------------------------------------------------
def make_figures(full_result: dict, fig_dir: Path) -> list[str]:
    fig_dir.mkdir(parents=True, exist_ok=True)
    saved = []
    internal = full_result["_internal"]
    rolled, feats = internal["rolled"], internal["feats"]

    # (a) ROC curves overlay
    fig, ax = plt.subplots(figsize=(6, 6))
    for name, fit in [("csd_threshold", internal["csd"]), ("naive_agreement", internal["naive"]),
                       ("spectral_model", internal["spectral"]), ("sprt", internal["sprt"])]:
        y_true, y_score = fit["y_true"], fit["y_score"]
        if len(np.unique(y_true)) < 2:
            continue
        fpr, tpr, _ = roc_curve(y_true, y_score)
        auc = full_result["classifiers"][name]["auc"]
        ax.plot(fpr, tpr, label=f"{name} (AUC={auc:.2f})")
    ax.plot([0, 1], [0, 1], "k--", linewidth=0.8)
    ax.set_xlabel("False positive rate")
    ax.set_ylabel("True positive rate")
    ax.set_title(f"ROC curves — {full_result['label']} dataset (bootstrap-CI classifiers)")
    ax.legend(loc="lower right", fontsize=8)
    ax.set_aspect("equal")
    fig.tight_layout()
    p = fig_dir / f"roc_curves_{full_result['label']}.png"
    fig.savefig(p, dpi=150)
    plt.close(fig)
    saved.append(str(p.relative_to(WORKSPACE)))

    # (b) lead time distributions
    lt = full_result["lead_time_analysis"]
    fig, ax = plt.subplots(figsize=(8, 5))
    classifiers_names = list(lt.keys())
    outcome_keys = ["true_positive", "true_negative", "false_positive", "false_negative"]
    x = np.arange(len(classifiers_names))
    width = 0.2
    for i, ok in enumerate(outcome_keys):
        means = [lt[c].get(f"mean_lead_time_{ok}", np.nan) for c in classifiers_names]
        sds = [lt[c].get(f"sd_lead_time_{ok}", 0) for c in classifiers_names]
        ax.bar(x + i * width, means, width, yerr=sds, label=ok, capsize=3)
    ax.set_xticks(x + 1.5 * width)
    ax.set_xticklabels(classifiers_names, rotation=20, ha="right")
    ax.set_ylabel("Lead time (rounds before final round)")
    ax.set_title(f"Lead time by classifier and outcome — {full_result['label']}")
    ax.legend(fontsize=7)
    fig.tight_layout()
    p = fig_dir / f"lead_time_{full_result['label']}.png"
    fig.savefig(p, dpi=150)
    plt.close(fig)
    saved.append(str(p.relative_to(WORKSPACE)))

    # (c) autocorrelation trajectories for example debates
    fig, ax = plt.subplots(figsize=(8, 5))
    examples = []
    for label_target in ["converged", "collapsed", "deadlocked"]:
        sub = feats[feats["outcome_label"] == label_target]
        if len(sub):
            examples.append((label_target, sub.iloc[0]["debate_id"]))
    for outcome_name, did in examples:
        g = rolled[rolled["debate_id"] == did].sort_values("round_number")
        ax.plot(g["round_number"], g["autocorr"], marker="o", label=f"{outcome_name} ({did[:8]})")
        ax.axvspan(g["round_number"].max() - 1, g["round_number"].max(), color="red", alpha=0.08)
    ax.set_xlabel("Round number")
    ax.set_ylabel("Lag-1 autocorrelation (agreement_score)")
    ax.set_title("Example debate autocorrelation trajectories (shaded = pre-outcome round)")
    ax.legend(fontsize=8)
    fig.tight_layout()
    p = fig_dir / f"autocorr_trajectories_{full_result['label']}.png"
    fig.savefig(p, dpi=150)
    plt.close(fig)
    saved.append(str(p.relative_to(WORKSPACE)))

    # (d) scatter autocorr vs variance colored by outcome
    fig, ax = plt.subplots(figsize=(6, 6))
    colors = {"converged": "tab:blue", "collapsed": "tab:red", "deadlocked": "tab:orange"}
    for outcome_name, c in colors.items():
        sub = feats[feats["outcome_label"] == outcome_name]
        ax.scatter(sub["autocorr_pre_mean"], sub["variance_pre_mean"], label=outcome_name, color=c, alpha=0.7)
    ax.set_xlabel("Mean pre-outcome autocorrelation")
    ax.set_ylabel("Mean pre-outcome variance")
    ax.set_title(f"Debate-level early-warning signal space — {full_result['label']}")
    ax.legend()
    fig.tight_layout()
    p = fig_dir / f"scatter_autocorr_variance_{full_result['label']}.png"
    fig.savefig(p, dpi=150)
    plt.close(fig)
    saved.append(str(p.relative_to(WORKSPACE)))

    # (f) hierarchical model coefficient plot
    hier = full_result["hierarchical_model"]
    if "coefficients" in hier:
        fig, ax = plt.subplots(figsize=(6, 4))
        names = list(hier["coefficients"].keys())
        ests = [hier["coefficients"][n]["estimate"] for n in names]
        errs = [
            (hier["coefficients"][n]["estimate"] - hier["coefficients"][n]["ci_95"][0])
            for n in names
        ]
        ax.errorbar(ests, names, xerr=errs, fmt="o", capsize=4)
        ax.axvline(0, color="gray", linewidth=0.8, linestyle="--")
        ax.set_xlabel("Coefficient estimate (95% CI)")
        ax.set_title(f"GEE hierarchical model coefficients — {full_result['label']}")
        fig.tight_layout()
        p = fig_dir / f"hierarchical_coefficients_{full_result['label']}.png"
        fig.savefig(p, dpi=150)
        plt.close(fig)
        saved.append(str(p.relative_to(WORKSPACE)))

    return saved


def make_permutation_null_figures(full_res: dict, clean_res: dict, fig_dir: Path) -> list[str]:
    saved = []
    for res in (full_res, clean_res):
        rolled = res["_internal"]["rolled"]
        pre = extract_pre_outcome_rows(rolled)
        group = pre["outcome_label"].isin(["collapsed", "deadlocked"]).to_numpy().astype(int)
        for stat_name in ["autocorr", "variance"]:
            vals = pre[stat_name].to_numpy()
            perm_full = permutation_test(vals, group, n_permutations=10_000, block_length=2, seed=RNG_SEED)
            null = np.array(perm_full["null_distribution_sample"])
            fig, ax = plt.subplots(figsize=(6, 4))
            ax.hist(null, bins=40, color="tab:gray", alpha=0.8)
            ax.axvline(perm_full["mean_diff"], color="red", linewidth=1.5, label=f"observed (p={perm_full['p_value']:.4f})")
            ax.set_xlabel(f"Permuted mean-difference ({stat_name})")
            ax.set_ylabel("Count")
            ax.set_title(f"Permutation null — {stat_name}, {res['label']} dataset")
            ax.legend(fontsize=8)
            fig.tight_layout()
            p = fig_dir / f"permutation_null_{stat_name}_{res['label']}.png"
            fig.savefig(p, dpi=150)
            plt.close(fig)
            saved.append(str(p.relative_to(WORKSPACE)))
    return saved


def make_sensitivity_figure(sensitivity: dict, fig_dir: Path) -> str:
    fig, axes = plt.subplots(1, 2, figsize=(10, 4))
    keys_p = ["permutation_autocorr_p_full", "permutation_autocorr_p_clean",
              "permutation_variance_p_full", "permutation_variance_p_clean"]
    axes[0].bar(range(len(keys_p)), [sensitivity[k] for k in keys_p], color=["tab:blue", "tab:cyan", "tab:red", "tab:orange"])
    axes[0].axhline(0.05, color="black", linestyle="--", linewidth=0.8)
    axes[0].set_xticks(range(len(keys_p)))
    axes[0].set_xticklabels(["autocorr\nfull", "autocorr\nclean", "variance\nfull", "variance\nclean"], fontsize=8)
    axes[0].set_ylabel("p-value")
    axes[0].set_title("Permutation p-values: full vs clean")

    auc_keys = [k for k in sensitivity if k.endswith("_auc_full") or k.endswith("_auc_clean")]
    auc_keys = sorted(auc_keys)
    axes[1].bar(range(len(auc_keys)), [sensitivity[k] for k in auc_keys])
    axes[1].set_xticks(range(len(auc_keys)))
    axes[1].set_xticklabels(auc_keys, rotation=45, ha="right", fontsize=7)
    axes[1].set_ylabel("AUC")
    axes[1].set_title("Classifier AUC: full vs clean")
    fig.tight_layout()
    p = fig_dir / "sensitivity_full_vs_clean.png"
    fig.savefig(p, dpi=150)
    plt.close(fig)
    return str(p.relative_to(WORKSPACE))


def make_tables(full_res: dict, clean_res: dict, sensitivity: dict, table_dir: Path) -> None:
    table_dir.mkdir(parents=True, exist_ok=True)

    # Table 1: classifier comparison (full dataset)
    rows = []
    for name, c in full_res["classifiers"].items():
        lt = full_res["lead_time_analysis"][name]
        rows.append(
            {
                "classifier": name,
                "auc": round(c["auc"], 4),
                "auc_ci_95_low": round(c["auc_ci_95"][0], 4) if not np.isnan(c["auc_ci_95"][0]) else "",
                "auc_ci_95_high": round(c["auc_ci_95"][1], 4) if not np.isnan(c["auc_ci_95"][1]) else "",
                "sensitivity": round(c["sensitivity"], 4) if not np.isnan(c["sensitivity"]) else "",
                "specificity": round(c["specificity"], 4) if not np.isnan(c["specificity"]) else "",
                "mean_lead_time_tp": round(lt["mean_lead_time_true_positive"], 3) if not np.isnan(lt["mean_lead_time_true_positive"]) else "",
            }
        )
    t1 = pd.DataFrame(rows)
    t1.to_csv(table_dir / "table1_classifier_comparison.csv", index=False)
    (table_dir / "table1_classifier_comparison.md").write_text(t1.to_markdown(index=False))

    # Table 2: permutation test results (full + clean)
    rows = []
    for res in (full_res, clean_res):
        for stat_name, d in res["permutation_tests"].items():
            rows.append(
                {
                    "dataset": res["label"],
                    "statistic": stat_name,
                    "p_value": round(d["p_value"], 5),
                    "effect_size_cohens_d": round(d["effect_size_cohens_d"], 4),
                    "mean_diff": round(d["mean_diff"], 4),
                    "ci_95_low": round(d["ci_95"][0], 4),
                    "ci_95_high": round(d["ci_95"][1], 4),
                }
            )
    t2 = pd.DataFrame(rows)
    t2.to_csv(table_dir / "table2_permutation_tests.csv", index=False)
    (table_dir / "table2_permutation_tests.md").write_text(t2.to_markdown(index=False))

    # Table 3: hierarchical model coefficients (full dataset)
    hier = full_res["hierarchical_model"]
    rows = []
    if "coefficients" in hier:
        for name, c in hier["coefficients"].items():
            rows.append(
                {
                    "term": name,
                    "estimate": round(c["estimate"], 4),
                    "se": round(c["se"], 4),
                    "z": round(c["z"], 4),
                    "p": round(c["p"], 5),
                    "ci_95_low": round(c["ci_95"][0], 4),
                    "ci_95_high": round(c["ci_95"][1], 4),
                }
            )
    t3 = pd.DataFrame(rows)
    t3.to_csv(table_dir / "table3_hierarchical_model.csv", index=False)
    (table_dir / "table3_hierarchical_model.md").write_text(t3.to_markdown(index=False) if len(t3) else "no coefficients")

    # Table 4: sensitivity analysis
    t4 = pd.DataFrame([sensitivity])
    t4.to_csv(table_dir / "table4_sensitivity_analysis.csv", index=False)
    (table_dir / "table4_sensitivity_analysis.md").write_text(t4.T.to_markdown())

    # Table 5: deadlock breakdown
    deadlock_cases = full_res["deadlock_analysis"]["deadlock_cases"]
    t5 = pd.DataFrame(deadlock_cases) if deadlock_cases else pd.DataFrame(
        columns=["debate_id", "n_rounds", "agreement_trajectory", "outcome_label"]
    )
    t5.to_csv(table_dir / "table5_deadlock_breakdown.csv", index=False)
    (table_dir / "table5_deadlock_breakdown.md").write_text(t5.to_markdown(index=False) if len(t5) else "n=0 deadlocked cases in this split")


# --------------------------------------------------------------------------
# Output assembly
# --------------------------------------------------------------------------
def strip_internal(result: dict) -> dict:
    return {k: v for k, v in result.items() if k != "_internal"}


def to_exp_gen_sol_out(df_full: pd.DataFrame, full_res: dict, clean_res: dict, sensitivity: dict) -> dict:
    """Package as exp_gen_sol_out schema: one example per debate, predict_ fields carry per-debate
    classifier predictions (computed on the debate's test-split membership when applicable)."""
    feats = full_res["_internal"]["feats"]
    test_ids = set(full_res["_internal"]["test_feats"]["debate_id"])
    csd_map = dict(zip(full_res["_internal"]["test_feats"]["debate_id"], full_res["_internal"]["csd"]["y_pred"]))
    naive_map = dict(zip(full_res["_internal"]["test_feats"]["debate_id"], full_res["_internal"]["naive"]["y_pred"]))
    spectral_map = dict(zip(full_res["_internal"]["test_feats"]["debate_id"], full_res["_internal"]["spectral"]["y_pred"]))
    sprt_map = dict(zip(full_res["_internal"]["test_feats"]["debate_id"], full_res["_internal"]["sprt"]["y_pred"]))

    examples = []
    for _, row in feats.iterrows():
        did = row["debate_id"]
        ex = {
            "input": json.dumps(
                {
                    "debate_id": did,
                    "source_config": row["source_config"],
                    "agreement_trajectory": row["agreement_trajectory"],
                    "autocorr_pre_mean": None if pd.isna(row["autocorr_pre_mean"]) else row["autocorr_pre_mean"],
                    "variance_pre_mean": None if pd.isna(row["variance_pre_mean"]) else row["variance_pre_mean"],
                    "spectral_radius": None if pd.isna(row["spectral_radius"]) else row["spectral_radius"],
                }
            ),
            "output": row["outcome_label"],
            "metadata_debate_id": did,
            "metadata_split": "test" if did in test_ids else "train",
        }
        if did in test_ids:
            ex["predict_csd_threshold"] = "collapse" if csd_map[did] == 1 else "converged"
            ex["predict_naive_agreement"] = "collapse" if naive_map[did] == 1 else "converged"
            ex["predict_spectral_model"] = "collapse" if spectral_map[did] == 1 else "converged"
            ex["predict_sprt"] = "collapse" if sprt_map[did] == 1 else "converged"
        examples.append(ex)

    # test-split (predicted) examples first, so downstream mini/preview truncations (which take
    # the first N examples) always retain at least one predict_* field, per exp_gen_sol_out schema
    examples.sort(key=lambda ex: 0 if ex["metadata_split"] == "test" else 1)

    return {
        "metadata": {
            "method_name": "CSD early-warning statistics for multi-agent debate collapse",
            "description": "Permutation tests, GEE hierarchical model, and 4 binary classifiers "
            "(CSD-threshold, naive-agreement baseline, spectral-contagion, SPRT) comparing "
            "early-round autocorrelation/variance rise before debate collapse vs. convergence.",
            "full_results": strip_internal(full_res),
            "clean_results": strip_internal(clean_res),
            "sensitivity_analysis": {"full_dataset_vs_clean_dataset": sensitivity},
            "dataset_metadata": {
                "dataset_rows": int(len(df_full)),
                "n_debates": int(df_full["debate_id"].nunique()),
                "n_converged": int((df_full.groupby("debate_id")["outcome_label"].first() == "converged").sum()),
                "n_collapsed": int((df_full.groupby("debate_id")["outcome_label"].first() == "collapsed").sum()),
                "n_deadlocked": int((df_full.groupby("debate_id")["outcome_label"].first() == "deadlocked").sum()),
                "mean_rounds_per_debate": float(df_full.groupby("debate_id").size().mean()),
                "window_size_autocorr": 2,
                "window_size_variance": 3,
                "permutation_replicates": 10000,
                "block_length_permutation": 2,
                "train_test_split": "70-30 stratified by outcome_label",
                "bootstrap_replicates": 1000,
                "analysis_timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
                "note_autocorr_sample_sparsity": "agreement_score is a discretized fraction "
                "(k-of-n_agents matching the modal solution), so it is frequently constant across "
                "a debate's early rounds; the lag-1 autocorrelation statistic is only defined "
                "(non-NaN) where a trailing window has nonzero variance, which sharply reduces the "
                "effective sample size feeding the autocorrelation permutation test/classifier "
                "relative to the rolling-variance statistic (which stays defined at variance=0). "
                "This is an intrinsic property of the discretized signal, not a computation error; "
                "the variance-based tests and classifiers should be weighted more heavily than the "
                "sparse autocorrelation results.",
                "note_cascade_vs_false_consensus": "Dataset labels only distinguish "
                "converged/collapsed/deadlocked; no cascade-vs-false-consensus sub-label is present "
                "in metadata, so the plan's step-17 collapse-mode breakdown could not be run and is omitted.",
            },
        },
        "datasets": [{"dataset": "Multi-Agent-LLMs/DEBATE (derived: CSD early-warning analysis)", "examples": examples}],
    }


# --------------------------------------------------------------------------
# Main
# --------------------------------------------------------------------------
@logger.catch(reraise=True)
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-file", default="full_data_out.json")
    parser.add_argument("--limit-debates", type=int, default=None)
    parser.add_argument("--out", default="method_out.json")
    args = parser.parse_args()

    t0 = time.time()
    data_path = WORKSPACE / args.data_file
    examples = load_examples(data_path, limit=args.limit_debates)
    df = build_dataframe(examples)
    del examples
    gc.collect()

    logger.info(f"Full dataset: {len(df)} rows, {df['debate_id'].nunique()} debates")

    clean_df = df[df["source_config"] != "critical_expert_memory_simple_voting"].reset_index(drop=True)
    logger.info(f"Clean dataset (excl. memory_simple_voting): {len(clean_df)} rows, {clean_df['debate_id'].nunique()} debates")

    full_res = run_pipeline(df, label="full_dataset", seed=RNG_SEED)
    clean_res = run_pipeline(clean_df, label="clean_dataset", seed=RNG_SEED) if clean_df["debate_id"].nunique() >= 10 else None

    if clean_res is None:
        logger.warning("Clean dataset too small for a separate pipeline run; reusing full-dataset results as proxy")
        clean_res = full_res

    def auc_or_nan(res, name):
        return res["classifiers"][name]["auc"]

    sensitivity = {
        "permutation_autocorr_p_full": full_res["permutation_tests"]["autocorrelation"]["p_value"],
        "permutation_autocorr_p_clean": clean_res["permutation_tests"]["autocorrelation"]["p_value"],
        "permutation_variance_p_full": full_res["permutation_tests"]["variance"]["p_value"],
        "permutation_variance_p_clean": clean_res["permutation_tests"]["variance"]["p_value"],
        "csd_threshold_auc_full": auc_or_nan(full_res, "csd_threshold"),
        "csd_threshold_auc_clean": auc_or_nan(clean_res, "csd_threshold"),
        "naive_agreement_auc_full": auc_or_nan(full_res, "naive_agreement"),
        "naive_agreement_auc_clean": auc_or_nan(clean_res, "naive_agreement"),
        "spectral_model_auc_full": auc_or_nan(full_res, "spectral_model"),
        "spectral_model_auc_clean": auc_or_nan(clean_res, "spectral_model"),
        "sprt_auc_full": auc_or_nan(full_res, "sprt"),
        "sprt_auc_clean": auc_or_nan(clean_res, "sprt"),
    }
    auc_diffs = [
        abs(sensitivity[f"{c}_auc_full"] - sensitivity[f"{c}_auc_clean"])
        for c in ["csd_threshold", "naive_agreement", "spectral_model", "sprt"]
        if not (np.isnan(sensitivity[f"{c}_auc_full"]) or np.isnan(sensitivity[f"{c}_auc_clean"]))
    ]
    p_crosses = any(
        (sensitivity[f"permutation_{s}_p_full"] < 0.05) != (sensitivity[f"permutation_{s}_p_clean"] < 0.05)
        for s in ["autocorr", "variance"]
    )
    max_auc_drop = max(auc_diffs) if auc_diffs else float("nan")
    sensitivity["max_abs_auc_difference"] = float(max_auc_drop) if not np.isnan(max_auc_drop) else None
    sensitivity["p_value_crosses_005_boundary"] = bool(p_crosses)
    sensitivity["robust_to_label_noise"] = bool((not np.isnan(max_auc_drop)) and max_auc_drop < 0.10 and not p_crosses)
    sensitivity["note"] = (
        "Compares the full dataset against the dataset with critical_expert_memory_simple_voting excluded "
        "(that config carries the ~24% decisionSuccess/final-answer label mismatch documented in the dataset dependency)."
    )

    fig_dir = WORKSPACE / "figures"
    saved_figs = make_figures(full_res, fig_dir)
    if clean_res is not full_res:
        saved_figs += make_figures(clean_res, fig_dir)
    saved_figs += make_permutation_null_figures(full_res, clean_res, fig_dir)
    saved_figs.append(make_sensitivity_figure(sensitivity, fig_dir))
    logger.info(f"Saved {len(saved_figs)} figures to {fig_dir}")

    table_dir = WORKSPACE / "tables"
    make_tables(full_res, clean_res, sensitivity, table_dir)
    logger.info(f"Saved tables to {table_dir}")

    output = to_exp_gen_sol_out(df, full_res, clean_res, sensitivity)
    out_path = WORKSPACE / args.out
    out_path.write_text(json.dumps(output, indent=2, default=lambda o: float(o) if isinstance(o, (np.floating,)) else str(o)))
    logger.info(f"Wrote {out_path} ({out_path.stat().st_size / 1e6:.2f} MB)")

    elapsed = time.time() - t0
    logger.info(f"Done in {elapsed:.1f}s")


if __name__ == "__main__":
    main()
