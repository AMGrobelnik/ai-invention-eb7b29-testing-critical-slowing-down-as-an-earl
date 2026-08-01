#!/usr/bin/env python3
"""Cross-validation, ablation, and robustness evaluation of a critical-slowing-down
(CSD) classifier for multi-agent-debate collapse, against naive/spectral baselines.

Loads per-round agreement-score trajectories for 95 debates (7 rounds each) from
the Multi-Agent-LLMs/DEBATE dataset, engineers CSD features (rolling lag-1
autocorrelation, rolling variance) on the agreement time series, and evaluates
generalization, feature ablation, spectral-noise character, failure modes,
baseline comparisons, and robustness under 5-fold stratified group cross-validation.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

import numpy as np
from loguru import logger
from scipy import stats as sp_stats
from scipy.signal import periodogram
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import StratifiedKFold

WORKDIR = Path(__file__).resolve().parent
DATA_PATH = (
    WORKDIR.parent
    / "gen_art_experiment_1"
    / "full_data_out.json"
)
OUT_PATH = WORKDIR / "eval_out.json"
RESULTS_DIR = WORKDIR / "results"
LOG_DIR = WORKDIR / "logs"
N_FOLDS = 5
RANDOM_STATE = 0
COLLAPSE_LABELS = {"collapsed", "deadlocked"}  # non-converged outcomes are "collapse"
WINDOWS_FOR_ROBUSTNESS = (2, 3)
DEFAULT_WINDOW = 3

logger.remove()
logger.add(sys.stdout, level="INFO", format="{time:HH:mm:ss}|{level:<7}|{message}")
logger.add(LOG_DIR / "run.log", rotation="30 MB", level="DEBUG")


# ----------------------------------------------------------------------------
# Data loading / debate reconstruction
# ----------------------------------------------------------------------------


def load_debates(data_path: Path) -> list[dict[str, Any]]:
    """Group per-round examples into per-debate trajectories, sorted by round."""
    logger.info(f"Loading raw debate rounds from {data_path}")
    raw = json.loads(data_path.read_text())
    examples = raw["datasets"][0]["examples"]
    logger.info(f"Loaded {len(examples)} round-level examples")

    by_debate: dict[str, list[dict[str, Any]]] = {}
    for ex in examples:
        by_debate.setdefault(ex["metadata_debate_id"], []).append(ex)

    debates = []
    for debate_id, rounds in by_debate.items():
        rounds = sorted(rounds, key=lambda r: r["metadata_round_number"])
        final = rounds[-1]
        agreement = [float(r["metadata_agreement_score"]) for r in rounds]
        model_mix = final["metadata_model_mix"]
        debates.append(
            {
                "debate_id": debate_id,
                "agreement": agreement,
                "n_rounds": len(rounds),
                "outcome": final["output"],
                "label": 1 if final["output"] in COLLAPSE_LABELS else 0,
                "source_config": final["metadata_source_config"],
                "model_mix": model_mix,
                "n_models": len(set(model_mix)),
                "persona_diversity": float(final["metadata_persona_diversity"]),
                "decision_success": bool(final["metadata_decision_success"]),
                "mean_agreement": float(np.mean(agreement)),
                "final_agreement": agreement[-1],
            }
        )
    logger.info(
        f"Reconstructed {len(debates)} debates; "
        f"label balance: {sum(d['label'] for d in debates)} collapse / "
        f"{len(debates) - sum(d['label'] for d in debates)} converged"
    )
    return debates


# ----------------------------------------------------------------------------
# Feature engineering
# ----------------------------------------------------------------------------


def rolling_lag1_autocorr(series: np.ndarray, window: int) -> np.ndarray:
    """Rolling lag-1 autocorrelation ending at each index (NaN until window filled)."""
    n = len(series)
    out = np.full(n, np.nan)
    for i in range(window - 1, n):
        w = series[i - window + 1 : i + 1]
        if window < 2 or np.std(w) < 1e-12:
            out[i] = 0.0
            continue
        x0, x1 = w[:-1], w[1:]
        if np.std(x0) < 1e-12 or np.std(x1) < 1e-12:
            out[i] = 0.0
        else:
            out[i] = np.corrcoef(x0, x1)[0, 1]
    return out


def rolling_variance(series: np.ndarray, window: int) -> np.ndarray:
    n = len(series)
    out = np.full(n, np.nan)
    for i in range(window - 1, n):
        out[i] = np.var(series[i - window + 1 : i + 1])
    return out


def csd_trend_features(series: list[float], window: int) -> dict[str, float]:
    """Kendall-tau trend of rolling AC(1) and variance across the trajectory, plus
    the mean level of each in the final half of the debate (pooled early-warning
    signal used as the classifier's scalar features)."""
    arr = np.asarray(series, dtype=float)
    ac1 = rolling_lag1_autocorr(arr, window)
    var = rolling_variance(arr, window)
    valid = ~np.isnan(ac1)
    idx = np.arange(len(arr))
    if valid.sum() >= 3:
        tau_ac1, _ = sp_stats.kendalltau(idx[valid], ac1[valid])
        tau_var, _ = sp_stats.kendalltau(idx[valid], var[valid])
    else:
        tau_ac1, tau_var = 0.0, 0.0
    tau_ac1 = 0.0 if np.isnan(tau_ac1) else tau_ac1
    tau_var = 0.0 if np.isnan(tau_var) else tau_var
    late_ac1 = float(np.nanmean(ac1[len(arr) // 2 :])) if valid.any() else 0.0
    late_var = float(np.nanmean(var[len(arr) // 2 :])) if valid.any() else 0.0
    return {
        "trend_ac1": float(tau_ac1),
        "trend_var": float(tau_var),
        "late_ac1": 0.0 if np.isnan(late_ac1) else late_ac1,
        "late_var": 0.0 if np.isnan(late_var) else late_var,
    }


def build_feature_table(debates: list[dict[str, Any]], window: int) -> dict[str, np.ndarray]:
    feats = [csd_trend_features(d["agreement"], window) for d in debates]
    return {
        "trend_ac1": np.array([f["trend_ac1"] for f in feats]),
        "trend_var": np.array([f["trend_var"] for f in feats]),
        "late_ac1": np.array([f["late_ac1"] for f in feats]),
        "late_var": np.array([f["late_var"] for f in feats]),
    }


# ----------------------------------------------------------------------------
# Classifiers
# ----------------------------------------------------------------------------


def fit_predict_logreg(
    X_train: np.ndarray, y_train: np.ndarray, X_test: np.ndarray
) -> np.ndarray:
    """Logistic-regression classifier over standardized features; returns
    P(collapse) on the test fold. Falls back to the train-set collapse rate
    when a fold has a single class (degenerate fit)."""
    if len(np.unique(y_train)) < 2:
        return np.full(X_test.shape[0], float(y_train.mean()))
    mu, sigma = X_train.mean(axis=0), X_train.std(axis=0)
    sigma[sigma < 1e-9] = 1.0
    Xtr = (X_train - mu) / sigma
    Xte = (X_test - mu) / sigma
    clf = LogisticRegression(max_iter=1000, random_state=RANDOM_STATE)
    clf.fit(Xtr, y_train)
    return clf.predict_proba(Xte)[:, 1]


def naive_threshold_scores(mean_agreement_train: np.ndarray, mean_agreement_test: np.ndarray) -> tuple[np.ndarray, float]:
    """Naive classifier: score = -mean_agreement (lower agreement => more likely
    collapse); threshold fit as the median of the training fold's mean agreement."""
    threshold = float(np.median(mean_agreement_train))
    scores = -mean_agreement_test
    return scores, threshold


def spectral_cascade_scores(
    debates_train: list[dict[str, Any]], y_train: np.ndarray, debates_test: list[dict[str, Any]]
) -> np.ndarray:
    """Baseline: score = fraction of low-frequency spectral power (below the
    median frequency) in the agreement series, fit direction from the training
    fold via correlation sign with the label."""
    def low_freq_power_frac(series: list[float]) -> float:
        arr = np.asarray(series, dtype=float)
        arr = arr - arr.mean()
        if np.std(arr) < 1e-12:
            return 0.0
        freqs, power = periodogram(arr)
        if len(freqs) <= 1 or power.sum() <= 0:
            return 0.0
        mid = len(freqs) // 2
        return float(power[1:mid].sum() / power[1:].sum()) if power[1:].sum() > 0 else 0.0

    train_feat = np.array([low_freq_power_frac(d["agreement"]) for d in debates_train])
    test_feat = np.array([low_freq_power_frac(d["agreement"]) for d in debates_test])
    corr = np.corrcoef(train_feat, y_train)[0, 1] if np.std(train_feat) > 1e-12 else 0.0
    sign = 1.0 if (np.isnan(corr) or corr >= 0) else -1.0
    return sign * test_feat


# ----------------------------------------------------------------------------
# Evaluation blocks
# ----------------------------------------------------------------------------


def safe_auc(y_true: np.ndarray, scores: np.ndarray) -> float | None:
    if len(np.unique(y_true)) < 2:
        return None
    return float(roc_auc_score(y_true, scores))


def cross_validate_classifiers(
    debates: list[dict[str, Any]], window: int = DEFAULT_WINDOW
) -> dict[str, Any]:
    """5-fold stratified CV of CSD (both features), naive, and spectral
    classifiers; returns per-fold AUC/precision/recall/F1/confusion matrices."""
    y = np.array([d["label"] for d in debates])
    feats = build_feature_table(debates, window)
    X_csd = np.column_stack([feats["trend_ac1"], feats["trend_var"]])
    mean_agree = np.array([d["mean_agreement"] for d in debates])

    skf = StratifiedKFold(n_splits=N_FOLDS, shuffle=True, random_state=RANDOM_STATE)
    per_fold: dict[str, list[dict[str, Any]]] = {"csd": [], "naive": [], "spectral": []}
    per_example_scores: dict[str, np.ndarray] = {
        "csd": np.zeros(len(debates)),
        "naive": np.zeros(len(debates)),
        "spectral": np.zeros(len(debates)),
    }

    for fold_idx, (train_idx, test_idx) in enumerate(skf.split(X_csd, y)):
        y_train, y_test = y[train_idx], y[test_idx]

        csd_scores = fit_predict_logreg(X_csd[train_idx], y_train, X_csd[test_idx])
        naive_scores, naive_thr = naive_threshold_scores(mean_agree[train_idx], mean_agree[test_idx])
        debates_train = [debates[i] for i in train_idx]
        debates_test = [debates[i] for i in test_idx]
        spectral_scores = spectral_cascade_scores(debates_train, y_train, debates_test)

        for name, scores in (("csd", csd_scores), ("naive", naive_scores), ("spectral", spectral_scores)):
            per_example_scores[name][test_idx] = scores
            preds = (scores >= np.median(scores)).astype(int) if len(np.unique(scores)) > 1 else np.zeros_like(y_test)
            tn, fp, fn, tp = confusion_matrix(y_test, preds, labels=[0, 1]).ravel()
            per_fold[name].append(
                {
                    "fold": fold_idx,
                    "auc": safe_auc(y_test, scores),
                    "precision": float(precision_score(y_test, preds, zero_division=0)),
                    "recall": float(recall_score(y_test, preds, zero_division=0)),
                    "f1": float(f1_score(y_test, preds, zero_division=0)),
                    "tp": int(tp),
                    "fp": int(fp),
                    "tn": int(tn),
                    "fn": int(fn),
                    "naive_threshold": naive_thr if name == "naive" else None,
                }
            )

    summary = {}
    for name, folds in per_fold.items():
        aucs = [f["auc"] for f in folds if f["auc"] is not None]
        summary[name] = {
            "mean_auc": float(np.mean(aucs)) if aucs else None,
            "sd_auc": float(np.std(aucs)) if aucs else None,
            "mean_precision": float(np.mean([f["precision"] for f in folds])),
            "mean_recall": float(np.mean([f["recall"] for f in folds])),
            "mean_f1": float(np.mean([f["f1"] for f in folds])),
            "per_fold": folds,
        }
    return {
        "summary": summary,
        "per_example_scores": {k: v.tolist() for k, v in per_example_scores.items()},
        "labels": y.tolist(),
    }


def sprt_classifier_scores(debates: list[dict[str, Any]]) -> np.ndarray:
    """SPRT-style sequential score: cumulative log-likelihood-ratio of observing
    the agreement trajectory under a 'collapse-drift' vs 'stable' hypothesis,
    approximated as the cumulative sum of (0.5 - agreement) increments."""
    scores = []
    for d in debates:
        arr = np.asarray(d["agreement"], dtype=float)
        llr = np.cumsum(0.5 - arr)
        scores.append(float(llr[-1]))
    return np.array(scores)


def cross_validate_sprt(debates: list[dict[str, Any]]) -> dict[str, Any]:
    y = np.array([d["label"] for d in debates])
    scores_full = sprt_classifier_scores(debates)
    skf = StratifiedKFold(n_splits=N_FOLDS, shuffle=True, random_state=RANDOM_STATE)
    fold_aucs = []
    for train_idx, test_idx in skf.split(scores_full.reshape(-1, 1), y):
        auc = safe_auc(y[test_idx], scores_full[test_idx])
        if auc is not None:
            fold_aucs.append(auc)
    return {
        "mean_auc": float(np.mean(fold_aucs)) if fold_aucs else None,
        "sd_auc": float(np.std(fold_aucs)) if fold_aucs else None,
        "n_folds_evaluable": len(fold_aucs),
    }


def feature_ablation(debates: list[dict[str, Any]], window: int = DEFAULT_WINDOW) -> dict[str, Any]:
    """CV AUC using autocorrelation only, variance only, and both, plus
    percentage AUC change from ablating each feature relative to the baseline."""
    y = np.array([d["label"] for d in debates])
    feats = build_feature_table(debates, window)
    skf = StratifiedKFold(n_splits=N_FOLDS, shuffle=True, random_state=RANDOM_STATE)

    variants = {
        "ac1_only": np.column_stack([feats["trend_ac1"]]),
        "var_only": np.column_stack([feats["trend_var"]]),
        "both": np.column_stack([feats["trend_ac1"], feats["trend_var"]]),
    }
    results = {}
    for name, X in variants.items():
        fold_aucs = []
        for train_idx, test_idx in skf.split(X, y):
            scores = fit_predict_logreg(X[train_idx], y[train_idx], X[test_idx])
            auc = safe_auc(y[test_idx], scores)
            if auc is not None:
                fold_aucs.append(auc)
        results[name] = {
            "mean_auc": float(np.mean(fold_aucs)) if fold_aucs else None,
            "sd_auc": float(np.std(fold_aucs)) if fold_aucs else None,
        }

    baseline = results["both"]["mean_auc"]
    delta = {}
    for name in ("ac1_only", "var_only"):
        val = results[name]["mean_auc"]
        if baseline and baseline > 0 and val is not None:
            delta[f"pct_auc_change_ablating_to_{name}"] = float(100.0 * (val - baseline) / baseline)
        else:
            delta[f"pct_auc_change_ablating_to_{name}"] = None
    results["ablation_deltas_pct"] = delta
    return results


def spectral_regime_analysis(debates: list[dict[str, Any]]) -> dict[str, Any]:
    """PSD-based regime classification per debate: fit log(power) ~ log(freq)
    slope via periodogram; classify white (slope~0), pink (slope~-1),
    brown (slope~-2), or low-frequency system-dynamics-dominated (spectral
    peak in the lowest quartile of frequencies carries most power)."""
    per_debate = []
    for d in debates:
        arr = np.asarray(d["agreement"], dtype=float) - np.mean(d["agreement"])
        if np.std(arr) < 1e-9:
            regime = "flat_no_variation"
            slope = None
            low_freq_frac = None
        else:
            freqs, power = periodogram(arr)
            freqs, power = freqs[1:], power[1:]  # drop DC
            valid = power > 0
            if valid.sum() >= 2:
                log_f = np.log(freqs[valid])
                log_p = np.log(power[valid])
                slope, _ = np.polyfit(log_f, log_p, 1)
            else:
                slope = None
            total_power = power.sum()
            low_freq_frac = (
                float(power[: max(1, len(power) // 4)].sum() / total_power)
                if total_power > 0
                else None
            )
            if low_freq_frac is not None and low_freq_frac > 0.6:
                regime = "system_dynamics_low_freq_peak"
            elif slope is None:
                regime = "indeterminate"
            elif slope > -0.5:
                regime = "white_noise"
            elif -1.5 <= slope <= -0.5:
                regime = "pink_noise_1_over_f"
            else:
                regime = "brown_noise_1_over_f2"
        per_debate.append(
            {
                "debate_id": d["debate_id"],
                "outcome": d["outcome"],
                "label": d["label"],
                "psd_slope": None if slope is None else float(slope),
                "low_freq_power_frac": low_freq_frac,
                "regime": regime,
            }
        )

    fraction_by_outcome: dict[str, dict[str, float]] = {}
    for outcome_key, outcome_label in (("collapse", 1), ("no_collapse", 0)):
        subset = [r for r in per_debate if r["label"] == outcome_label]
        counts: dict[str, int] = {}
        for r in subset:
            counts[r["regime"]] = counts.get(r["regime"], 0) + 1
        n = len(subset) or 1
        fraction_by_outcome[outcome_key] = {k: v / n for k, v in counts.items()}

    return {
        "per_debate": per_debate,
        "fraction_by_regime_and_outcome": fraction_by_outcome,
    }


def failure_mode_analysis(
    debates: list[dict[str, Any]], csd_scores: np.ndarray, window: int = DEFAULT_WINDOW
) -> dict[str, Any]:
    """Segment CSD classifier confusion by debate length quartile, model
    diversity (homogeneous vs mixed pools), and agreement-range band."""
    y = np.array([d["label"] for d in debates])
    threshold = float(np.median(csd_scores))
    preds = (csd_scores >= threshold).astype(int)

    def confusion_dict(mask: np.ndarray) -> dict[str, int]:
        if mask.sum() == 0:
            return {"tp": 0, "fp": 0, "tn": 0, "fn": 0, "n": 0}
        tn, fp, fn, tp = confusion_matrix(
            y[mask], preds[mask], labels=[0, 1]
        ).ravel()
        return {"tp": int(tp), "fp": int(fp), "tn": int(tn), "fn": int(fn), "n": int(mask.sum())}

    n_rounds = np.array([d["n_rounds"] for d in debates])
    quartiles = np.percentile(n_rounds, [25, 50, 75]) if len(set(n_rounds)) > 1 else np.array([n_rounds[0]] * 3)
    length_bins = {
        "short_1_2": (n_rounds >= 1) & (n_rounds <= 2),
        "mid_3_4": (n_rounds >= 3) & (n_rounds <= 4),
        "long_5_7": (n_rounds >= 5) & (n_rounds <= 7),
    }
    by_length = {name: confusion_dict(mask) for name, mask in length_bins.items()}

    n_models = np.array([d["n_models"] for d in debates])
    by_diversity = {
        "homogeneous_1_model": confusion_dict(n_models == 1),
        "mixed_multi_model": confusion_dict(n_models > 1),
    }

    mean_agree = np.array([d["mean_agreement"] for d in debates])
    agreement_bins = {
        "high_gt_0.8": mean_agree > 0.8,
        "medium_0.5_0.8": (mean_agree >= 0.5) & (mean_agree <= 0.8),
        "low_lt_0.5": mean_agree < 0.5,
    }
    by_agreement_range = {name: confusion_dict(mask) for name, mask in agreement_bins.items()}

    mispredictions = []
    for i, d in enumerate(debates):
        if preds[i] != y[i]:
            mispredictions.append(
                {
                    "debate_id": d["debate_id"],
                    "outcome": d["outcome"],
                    "error_type": "false_collapse_prediction" if preds[i] == 1 and y[i] == 0 else "missed_collapse",
                    "n_rounds": d["n_rounds"],
                    "n_models": d["n_models"],
                    "mean_agreement": d["mean_agreement"],
                }
            )

    return {
        "classifier_threshold": threshold,
        "by_length_quartile_group": by_length,
        "by_model_diversity": by_diversity,
        "by_agreement_range": by_agreement_range,
        "n_mispredictions": len(mispredictions),
        "mispredictions": mispredictions,
    }


def baseline_lead_time_comparison(debates: list[dict[str, Any]], window: int = DEFAULT_WINDOW) -> dict[str, Any]:
    """For each collapsing debate, the earliest round (rounds-before-final)
    at which each classifier's rolling signal first crosses a fixed alarm
    threshold (75th percentile of that signal computed on non-collapsing
    debates), used as an early-warning lead-time proxy."""
    collapsing = [d for d in debates if d["label"] == 1]
    stable = [d for d in debates if d["label"] == 0]
    if not collapsing or not stable:
        return {"note": "insufficient class balance to compute lead time", "n_collapsing": len(collapsing), "n_stable": len(stable)}

    def csd_signal(series: list[float]) -> np.ndarray:
        arr = np.asarray(series, dtype=float)
        ac1 = rolling_lag1_autocorr(arr, window)
        var = rolling_variance(arr, window)
        return np.nan_to_num(ac1) + np.nan_to_num(var)

    def naive_signal(series: list[float]) -> np.ndarray:
        return -np.asarray(series, dtype=float)

    def spectral_signal(series: list[float]) -> np.ndarray:
        arr = np.asarray(series, dtype=float)
        out = np.full(len(arr), np.nan)
        for i in range(window - 1, len(arr)):
            w = arr[i - window + 1 : i + 1] - np.mean(arr[i - window + 1 : i + 1])
            out[i] = -np.var(w)
        return np.nan_to_num(out)

    results = {}
    for name, sig_fn in (("csd", csd_signal), ("naive", naive_signal), ("spectral", spectral_signal)):
        stable_signals = np.concatenate([sig_fn(d["agreement"]) for d in stable])
        stable_signals = stable_signals[~np.isnan(stable_signals)]
        alarm_threshold = float(np.percentile(stable_signals, 75)) if len(stable_signals) else 0.0
        lead_times = []
        for d in collapsing:
            sig = sig_fn(d["agreement"])
            n = len(sig)
            crossed = np.where(sig >= alarm_threshold)[0]
            if len(crossed):
                lead_times.append(int(n - crossed[0]))
        results[name] = {
            "alarm_threshold": alarm_threshold,
            "n_debates_with_alarm": len(lead_times),
            "n_collapsing_total": len(collapsing),
            "mean_lead_time_rounds": float(np.mean(lead_times)) if lead_times else None,
            "sd_lead_time_rounds": float(np.std(lead_times)) if lead_times else None,
        }
    return results


def robustness_checks(debates: list[dict[str, Any]]) -> dict[str, Any]:
    """(a) sensitivity to excluding the noisy memory_simple_voting config if its
    label mismatch (collapse-rate deviation from the pooled rate) exceeds 20pp;
    (b) bootstrap stability of short-window (2-3 pt) rolling estimates;
    (c) effect of window size (2 vs 3) on CV AUC."""
    overall_rate = float(np.mean([d["label"] for d in debates]))
    by_config: dict[str, dict[str, float]] = {}
    for cfg in sorted(set(d["source_config"] for d in debates)):
        subset = [d for d in debates if d["source_config"] == cfg]
        rate = float(np.mean([d["label"] for d in subset]))
        by_config[cfg] = {
            "n": len(subset),
            "collapse_rate": rate,
            "mismatch_pp": abs(rate - overall_rate) * 100.0,
        }
    noisy_configs = [c for c, v in by_config.items() if "memory_simple_voting" in c and v["mismatch_pp"] > 20.0]
    filtered_debates = [d for d in debates if d["source_config"] not in noisy_configs]

    cv_full = cross_validate_classifiers(debates, window=DEFAULT_WINDOW)["summary"]["csd"]["mean_auc"]
    cv_filtered = (
        cross_validate_classifiers(filtered_debates, window=DEFAULT_WINDOW)["summary"]["csd"]["mean_auc"]
        if len(filtered_debates) >= N_FOLDS and len(set(d["label"] for d in filtered_debates)) > 1
        else None
    )

    rng = np.random.default_rng(RANDOM_STATE)
    n_boot = 200
    boot_stability: dict[int, dict[str, float]] = {}
    for window in WINDOWS_FOR_ROBUSTNESS:
        cv_boots = []
        for _ in range(n_boot):
            idx = rng.integers(0, len(debates), size=len(debates))
            sample = [debates[i] for i in idx]
            arr_examples = [csd_trend_features(d["agreement"], window) for d in sample]
            cv_boots.append(float(np.mean([f["trend_ac1"] for f in arr_examples])))
        boot_stability[window] = {
            "mean_trend_ac1": float(np.mean(cv_boots)),
            "sd_trend_ac1_across_bootstraps": float(np.std(cv_boots)),
            "coefficient_of_variation": float(np.std(cv_boots) / abs(np.mean(cv_boots))) if abs(np.mean(cv_boots)) > 1e-9 else None,
        }

    window_effect = {}
    for window in WINDOWS_FOR_ROBUSTNESS:
        result = cross_validate_classifiers(debates, window=window)["summary"]["csd"]
        window_effect[window] = {"mean_auc": result["mean_auc"], "sd_auc": result["sd_auc"]}

    return {
        "config_collapse_rates": by_config,
        "noisy_configs_excluded": noisy_configs,
        "csd_auc_full": cv_full,
        "csd_auc_excluding_noisy_configs": cv_filtered,
        "bootstrap_short_window_stability": boot_stability,
        "window_size_effect_on_auc": window_effect,
    }


# ----------------------------------------------------------------------------
# Output assembly
# ----------------------------------------------------------------------------


def assemble_examples(
    debates: list[dict[str, Any]],
    cv_results: dict[str, Any],
    sprt_result: dict[str, Any],
) -> list[dict[str, Any]]:
    examples = []
    csd_scores = cv_results["per_example_scores"]["csd"]
    naive_scores = cv_results["per_example_scores"]["naive"]
    spectral_scores = cv_results["per_example_scores"]["spectral"]
    for i, d in enumerate(debates):
        examples.append(
            {
                "input": json.dumps(
                    {
                        "debate_id": d["debate_id"],
                        "agreement_trajectory": d["agreement"],
                        "source_config": d["source_config"],
                    }
                ),
                "output": d["outcome"],
                "metadata_debate_id": d["debate_id"],
                "metadata_n_rounds": d["n_rounds"],
                "metadata_n_models": d["n_models"],
                "metadata_source_config": d["source_config"],
                "metadata_ground_truth_label_collapse": d["label"],
                "predict_csd_classifier_score": str(round(float(csd_scores[i]), 6)),
                "predict_naive_threshold_score": str(round(float(naive_scores[i]), 6)),
                "predict_spectral_cascade_score": str(round(float(spectral_scores[i]), 6)),
                "eval_csd_score": float(csd_scores[i]),
                "eval_correct_label": int(d["label"]),
            }
        )
    return examples


@logger.catch(reraise=True)
def main() -> None:
    RESULTS_DIR.mkdir(exist_ok=True)
    LOG_DIR.mkdir(exist_ok=True)

    if not DATA_PATH.exists():
        logger.error(f"Dependency dataset not found at {DATA_PATH}")
        raise FileNotFoundError(DATA_PATH)

    debates = load_debates(DATA_PATH)

    logger.info("Running 5-fold stratified cross-validation for CSD / naive / spectral classifiers")
    cv_results = cross_validate_classifiers(debates)

    logger.info("Cross-validating SPRT-style sequential classifier")
    sprt_result = cross_validate_sprt(debates)

    logger.info("Running feature ablation study")
    ablation_results = feature_ablation(debates)

    logger.info("Running PSD-based spectral regime analysis")
    spectral_results = spectral_regime_analysis(debates)

    logger.info("Running failure-mode analysis")
    csd_scores_arr = np.array(cv_results["per_example_scores"]["csd"])
    failure_results = failure_mode_analysis(debates, csd_scores_arr)

    logger.info("Computing early-warning lead-time comparison across classifiers")
    lead_time_results = baseline_lead_time_comparison(debates)

    logger.info("Running robustness checks (noisy-config sensitivity, window size, bootstrap stability)")
    robustness_results = robustness_checks(debates)

    examples = assemble_examples(debates, cv_results, sprt_result)

    metrics_agg = {
        "n_debates_total": len(debates),
        "n_debates_collapse": int(sum(d["label"] for d in debates)),
        "n_debates_converged": int(len(debates) - sum(d["label"] for d in debates)),
        "csd_mean_auc": cv_results["summary"]["csd"]["mean_auc"] or 0.0,
        "csd_sd_auc": cv_results["summary"]["csd"]["sd_auc"] or 0.0,
        "csd_mean_precision": cv_results["summary"]["csd"]["mean_precision"],
        "csd_mean_recall": cv_results["summary"]["csd"]["mean_recall"],
        "csd_mean_f1": cv_results["summary"]["csd"]["mean_f1"],
        "naive_mean_auc": cv_results["summary"]["naive"]["mean_auc"] or 0.0,
        "naive_sd_auc": cv_results["summary"]["naive"]["sd_auc"] or 0.0,
        "spectral_mean_auc": cv_results["summary"]["spectral"]["mean_auc"] or 0.0,
        "spectral_sd_auc": cv_results["summary"]["spectral"]["sd_auc"] or 0.0,
        "sprt_mean_auc": sprt_result["mean_auc"] or 0.0,
        "sprt_sd_auc": sprt_result["sd_auc"] or 0.0,
        "ablation_ac1_only_auc": ablation_results["ac1_only"]["mean_auc"] or 0.0,
        "ablation_var_only_auc": ablation_results["var_only"]["mean_auc"] or 0.0,
        "ablation_both_auc": ablation_results["both"]["mean_auc"] or 0.0,
        "ablation_pct_change_ac1_only": ablation_results["ablation_deltas_pct"]["pct_auc_change_ablating_to_ac1_only"] or 0.0,
        "ablation_pct_change_var_only": ablation_results["ablation_deltas_pct"]["pct_auc_change_ablating_to_var_only"] or 0.0,
        "csd_auc_excluding_noisy_configs": robustness_results["csd_auc_excluding_noisy_configs"] or 0.0,
        "n_mispredictions": failure_results["n_mispredictions"],
        "csd_lead_time_rounds_mean": lead_time_results.get("csd", {}).get("mean_lead_time_rounds") or 0.0,
        "naive_lead_time_rounds_mean": lead_time_results.get("naive", {}).get("mean_lead_time_rounds") or 0.0,
        "spectral_lead_time_rounds_mean": lead_time_results.get("spectral", {}).get("mean_lead_time_rounds") or 0.0,
    }

    out = {
        "metadata": {
            "evaluation_name": "csd_classifier_cv_ablation_robustness",
            "description": (
                "5-fold stratified CV, feature ablation, PSD colored-noise regime analysis, "
                "failure-mode segmentation, naive/spectral/SPRT baseline comparison, and "
                "robustness checks for a critical-slowing-down (CSD) early-warning classifier "
                "of multi-agent-debate collapse."
            ),
            "n_folds": N_FOLDS,
            "default_window": DEFAULT_WINDOW,
            "random_state": RANDOM_STATE,
            "cross_validation": cv_results["summary"],
            "sprt_baseline": sprt_result,
            "feature_ablation": ablation_results,
            "spectral_regime_analysis": {
                "fraction_by_regime_and_outcome": spectral_results["fraction_by_regime_and_outcome"],
            },
            "failure_mode_analysis": {
                k: v for k, v in failure_results.items() if k != "mispredictions"
            },
            "early_warning_lead_time_comparison": lead_time_results,
            "robustness_checks": robustness_results,
        },
        "metrics_agg": metrics_agg,
        "datasets": [
            {
                "dataset": "Multi-Agent-LLMs/DEBATE",
                "examples": examples,
            }
        ],
    }

    # Full spectral per-debate table and full misprediction list go to results/ (not truncated for size in main JSON)
    (RESULTS_DIR / "spectral_regime_per_debate.json").write_text(
        json.dumps(spectral_results["per_debate"], indent=2)
    )
    (RESULTS_DIR / "mispredictions.json").write_text(
        json.dumps(failure_results["mispredictions"], indent=2)
    )

    logger.info(f"Writing evaluation output to {OUT_PATH}")
    OUT_PATH.write_text(json.dumps(out, indent=2))
    logger.info("Evaluation complete")
    logger.info(f"CSD AUC: {metrics_agg['csd_mean_auc']:.3f} ± {metrics_agg['csd_sd_auc']:.3f}")
    logger.info(f"Naive AUC: {metrics_agg['naive_mean_auc']:.3f}  Spectral AUC: {metrics_agg['spectral_mean_auc']:.3f}  SPRT AUC: {metrics_agg['sprt_mean_auc']:.3f}")


if __name__ == "__main__":
    main()
