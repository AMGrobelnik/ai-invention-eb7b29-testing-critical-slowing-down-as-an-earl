#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = ["loguru"]
# ///
"""Standardize the Multi-Agent-LLMs/DEBATE dataset to exp_sel_data_out.json schema."""

import json
import random
import re
import sys
from collections import defaultdict
from pathlib import Path

from loguru import logger

logger.remove()
logger.add(sys.stdout, level="INFO", format="{time:HH:mm:ss}|{level:<7}|{message}")
logger.add("logs/run.log", rotation="30 MB", level="DEBUG")

WORKSPACE = Path(__file__).parent
DATASETS_DIR = WORKSPACE / "temp" / "datasets"
RANDOM_SEED = 42
MAX_PER_CLASS = 45  # cap ~40-50/class per ideal_dataset_criteria (90-150 debates total)

# Three DEBATE configs w/ very different decisionSuccess mixes, combined for a balanced label set:
# memory_simple_voting is ~99% decisionSuccess=True (feeds "converged"); the other two are
# ~0-4% True (feed "collapsed"/"deadlocked"). Verified empirically before writing this script.
DEBATE_CONFIGS = [
    "critical_expert_memory_simple_voting",
    "critical_expert_debate_majority_consensus",
    "critical_expert_relay_approval_voting",
]


def normalize_solution(solution: str) -> str:
    return re.sub(r"\s+", " ", solution.strip().lower())[:50]


def classify_outcome(final_round_agreement: float, decision_success: bool) -> str:
    """Agreement here = fraction of agents sharing the modal (normalized) final-round solution
    text -- NOT the dataset's per-message `agreement` flag, which we verified is a noisy
    pairwise-critique signal (often False even when all agents' solutions already match).
    Converged=correct consensus w/ high final agreement; Collapsed=agents unanimously converge
    on a WRONG consensus; Deadlocked=never reached majority agreement by the last round."""
    if decision_success and final_round_agreement >= 0.66:
        return "converged"
    if final_round_agreement >= 0.66:
        return "collapsed"
    return "deadlocked"


def load_debates_for_config(config: str) -> list[dict]:
    src = DATASETS_DIR / f"raw_full_Multi-Agent-LLMs_DEBATE_{config}_train.json"
    logger.info(f"Loading DEBATE config '{config}' from {src}")
    debates = json.loads(src.read_text())
    for d in debates:
        d["_source_config"] = config
    logger.info(f"Loaded {len(debates)} debate transcripts for {config}")
    return debates


def label_debate(debate: dict) -> tuple[str, dict[int, float], list[int]]:
    by_round: dict[int, list[dict]] = defaultdict(list)
    for msg in debate["globalMemory"]:
        by_round[msg["turn"]].append(msg)
    round_numbers = sorted(by_round)

    round_agreement: dict[int, float] = {}
    for rnd, msgs in by_round.items():
        norm_solutions = [normalize_solution(m["solution"]) for m in msgs]
        modal_count = max((norm_solutions.count(s) for s in set(norm_solutions)), default=0)
        round_agreement[rnd] = modal_count / len(norm_solutions) if norm_solutions else 0.0

    final_round = round_numbers[-1]
    outcome_label = classify_outcome(round_agreement[final_round], bool(debate["decisionSuccess"]))
    return outcome_label, round_agreement, round_numbers


def build_debate_examples() -> list[dict]:
    all_debates = [d for cfg in DEBATE_CONFIGS for d in load_debates_for_config(cfg)]
    logger.info(f"Loaded {len(all_debates)} debates total across {len(DEBATE_CONFIGS)} configs")

    by_label: dict[str, list[dict]] = defaultdict(list)
    for debate in all_debates:
        outcome_label, round_agreement, round_numbers = label_debate(debate)
        debate["_outcome_label"] = outcome_label
        debate["_round_agreement"] = round_agreement
        debate["_round_numbers"] = round_numbers
        by_label[outcome_label].append(debate)

    logger.info(f"Raw label distribution: { {k: len(v) for k, v in by_label.items()} }")

    rng = random.Random(RANDOM_SEED)
    selected_debates = []
    for label, debates in by_label.items():
        rng.shuffle(debates)
        kept = debates[:MAX_PER_CLASS]
        if len(kept) < MAX_PER_CLASS:
            logger.warning(f"Only {len(kept)} debates available for label '{label}' (< cap {MAX_PER_CLASS})")
        selected_debates.extend(kept)
    logger.info(f"Selected {len(selected_debates)} debates after class-balanced sampling (cap={MAX_PER_CLASS}/class)")

    examples = []
    for debate in selected_debates:
        debate_id = debate["exampleId"]
        question_text = debate["input"][0]
        ground_truth = debate["references"][0]
        decision_success = bool(debate["decisionSuccess"])
        model_mix = sorted({p["model"] for p in debate["personas"]})
        persona_mix = sorted({p["persona"] for p in debate["personas"]})
        outcome_label = debate["_outcome_label"]
        round_agreement = debate["_round_agreement"]
        round_numbers = debate["_round_numbers"]

        by_round: dict[int, list[dict]] = defaultdict(list)
        for msg in debate["globalMemory"]:
            by_round[msg["turn"]].append(msg)
        final_round = round_numbers[-1]
        final_solution = by_round[final_round][-1]["solution"]

        for rnd in round_numbers:
            msgs = by_round[rnd]
            agent_responses = [
                {"persona": m["persona"], "message": m["message"], "solution": m["solution"]}
                for m in msgs
            ]
            input_payload = {
                "question_text": question_text,
                "round_number": rnd,
                "agent_responses": agent_responses,
            }
            examples.append(
                {
                    "input": json.dumps(input_payload, ensure_ascii=False),
                    "output": outcome_label,
                    "metadata_debate_id": debate_id,
                    "metadata_source_config": debate["_source_config"],
                    "metadata_round_number": rnd,
                    "metadata_total_rounds": len(round_numbers),
                    "metadata_agreement_score": round(round_agreement[rnd], 4),
                    "metadata_model_mix": model_mix,
                    "metadata_persona_mix": persona_mix,
                    "metadata_ground_truth_answer": ground_truth,
                    "metadata_final_consensus_answer": final_solution,
                    "metadata_decision_success": decision_success,
                    "metadata_persona_diversity": debate.get("persona_diversity"),
                    "metadata_task_type": "multi_agent_debate_collapse_detection",
                }
            )
    logger.info(f"Built {len(examples)} round-level examples from {len(selected_debates)} debates")
    return examples


def main() -> None:
    debate_examples = build_debate_examples()

    output = {
        "datasets": [
            {"dataset": "Multi-Agent-LLMs/DEBATE", "examples": debate_examples},
        ]
    }

    out_path = WORKSPACE / "full_data_out.json"
    out_path.write_text(json.dumps(output, ensure_ascii=False, indent=2))
    logger.info(f"Saved {out_path} ({out_path.stat().st_size / 1e6:.2f} MB)")


if __name__ == "__main__":
    main()
