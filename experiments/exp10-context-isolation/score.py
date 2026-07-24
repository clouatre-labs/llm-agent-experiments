"""Scoring and analysis for the context isolation experiment.

Reads session files, compares predicted answers to gold answers,
computes per-condition accuracy with Wilson confidence intervals,
and runs McNemar paired tests with Bonferroni correction.
"""

import argparse
import json
import math
from pathlib import Path

from gsm8k import extract_predicted_answer

EXP10_DIR = Path(__file__).parent


def _wilson_ci(correct: int, total: int, z: float = 1.96) -> tuple[float, float, float]:
    """Compute Wilson score confidence interval for a proportion.

    Returns (proportion, lower_bound, upper_bound).
    """
    if total == 0:
        return 0.0, 0.0, 0.0
    p = correct / total
    denominator = 1 + z**2 / total
    centre = p + z**2 / (2 * total)
    margin = z * math.sqrt(p * (1 - p) / total + z**2 / (4 * total**2)) / denominator
    centre = centre / denominator
    lower = max(0.0, centre - margin)
    upper = min(1.0, centre + margin)
    return p, lower, upper


def read_session_files(sessions_dir: Path) -> list[dict]:
    """Read all session JSON files from condition subdirectories."""
    records = []
    for cond_dir in sorted(sessions_dir.iterdir()):
        if not cond_dir.is_dir():
            continue
        condition = cond_dir.name
        for json_path in sorted(cond_dir.glob("*.json")):
            with open(json_path) as f:
                data = json.load(f)
            data["_condition"] = condition
            records.append(data)
    return records


def compute_scores(records: list[dict]) -> list[dict]:
    """Compute predicted vs gold answer for each record."""
    scores = []
    for r in records:
        predicted = extract_predicted_answer(r.get("response_text", ""))
        gold = r.get("gold_answer", "")
        correct = 1 if predicted == gold else 0
        scores.append(
            {
                "run_id": r["run_id"] if "run_id" in r else r.get("task_id", ""),
                "condition": r["_condition"],
                "task_id": r.get("run_id", ""),
                "gold": gold,
                "predicted": predicted,
                "correct": correct,
            }
        )
    return scores


def _mcnemar_test(
    scoped_correct: list[int],
    other_correct: list[int],
) -> tuple[float, float]:
    """Run McNemar test on paired binary outcomes.

    Returns (statistic, p_value).
    """
    b = 0  # scoped correct, other incorrect
    c = 0  # scoped incorrect, other correct
    for s, o in zip(scoped_correct, other_correct):
        if s == 1 and o == 0:
            b += 1
        if s == 0 and o == 1:
            c += 1

    if b + c == 0:
        return 0.0, 1.0

    stat = (b - c) ** 2 / (b + c)
    # p-value from chi-squared distribution with 1 df
    from scipy.stats import chi2

    p_value = 1.0 - chi2.cdf(stat, 1)
    return stat, p_value


def main() -> None:
    parser = argparse.ArgumentParser(description="Score context isolation experiment")
    parser.add_argument(
        "--reveal",
        action="store_true",
        help="Reveal label map (not used in binary scoring)",
    )
    parser.parse_args()

    sessions_dir = EXP10_DIR / "sessions"
    results_dir = EXP10_DIR / "results"
    results_dir.mkdir(parents=True, exist_ok=True)

    records = read_session_files(sessions_dir)
    if not records:
        print("No session files found in %s", sessions_dir)
        return

    scores = compute_scores(records)

    # Write scores.jsonl
    scores_path = results_dir / "scores.jsonl"
    with open(scores_path, "w") as f:
        f.writelines(json.dumps(s) + "\n" for s in scores)

    # Per-condition accuracy
    conditions = sorted({s["condition"] for s in scores})
    print("\nPer-condition accuracy (with Wilson 95% CI):")
    print(
        f"{'Condition':20s} {'n':>5s} {'Correct':>8s} {'Accuracy':>10s} {'CI lower':>10s} {'CI upper':>10s}"
    )
    print("-" * 65)

    condition_scores: dict[str, list[dict]] = {}
    for cond in conditions:
        cond_scores = [s for s in scores if s["condition"] == cond]
        condition_scores[cond] = cond_scores
        n = len(cond_scores)
        correct = sum(s["correct"] for s in cond_scores)
        p, lower, upper = _wilson_ci(correct, n)
        print(f"{cond:20s} {n:5d} {correct:8d} {p:10.4f} {lower:10.4f} {upper:10.4f}")

    # McNemar paired tests (scoped vs full-history, scoped vs contaminated)
    if "scoped" in conditions and "full-history" in conditions:
        paired = []
        for s_score, fh_score in zip(
            condition_scores["scoped"], condition_scores["full-history"]
        ):
            if s_score["task_id"] == fh_score["task_id"]:
                paired.append((s_score["correct"], fh_score["correct"]))
        if paired:
            scoped_correct = [p[0] for p in paired]
            fh_correct = [p[1] for p in paired]
            stat, p_val = _mcnemar_test(scoped_correct, fh_correct)
            bonferroni_alpha = 0.025
            significant = p_val < bonferroni_alpha
            print("\nMcNemar test: scoped vs full-history")
            print(f"  Statistic: {stat:.4f}")
            print(f"  p-value: {p_val:.6f}")
            print(f"  Bonferroni alpha: {bonferroni_alpha}")
            print(f"  Significant: {significant}")

    if "scoped" in conditions and "contaminated" in conditions:
        paired = []
        for s_score, c_score in zip(
            condition_scores["scoped"], condition_scores["contaminated"]
        ):
            if s_score["task_id"] == c_score["task_id"]:
                paired.append((s_score["correct"], c_score["correct"]))
        if paired:
            scoped_correct = [p[0] for p in paired]
            cont_correct = [p[1] for p in paired]
            stat, p_val = _mcnemar_test(scoped_correct, cont_correct)
            bonferroni_alpha = 0.025
            significant = p_val < bonferroni_alpha
            print("\nMcNemar test: scoped vs contaminated")
            print(f"  Statistic: {stat:.4f}")
            print(f"  p-value: {p_val:.6f}")
            print(f"  Bonferroni alpha: {bonferroni_alpha}")
            print(f"  Significant: {significant}")

    # Write McNemar summary
    mcnemar_summary = {}
    if "scoped" in conditions and "full-history" in conditions:
        paired = []
        for s_score, fh_score in zip(
            condition_scores["scoped"], condition_scores["full-history"]
        ):
            if s_score["task_id"] == fh_score["task_id"]:
                paired.append((s_score["correct"], fh_score["correct"]))
        if paired:
            scoped_correct = [p[0] for p in paired]
            fh_correct = [p[1] for p in paired]
            stat, p_val = _mcnemar_test(scoped_correct, fh_correct)
            mcnemar_summary["scoped_vs_full_history"] = {
                "statistic": stat,
                "p_value": p_val,
                "bonferroni_alpha": 0.025,
                "significant": p_val < 0.025,
            }

    if "scoped" in conditions and "contaminated" in conditions:
        paired = []
        for s_score, c_score in zip(
            condition_scores["scoped"], condition_scores["contaminated"]
        ):
            if s_score["task_id"] == c_score["task_id"]:
                paired.append((s_score["correct"], c_score["correct"]))
        if paired:
            scoped_correct = [p[0] for p in paired]
            cont_correct = [p[1] for p in paired]
            stat, p_val = _mcnemar_test(scoped_correct, cont_correct)
            mcnemar_summary["scoped_vs_contaminated"] = {
                "statistic": stat,
                "p_value": p_val,
                "bonferroni_alpha": 0.025,
                "significant": p_val < 0.025,
            }

    mcnemar_path = results_dir / "mcnemar_summary.json"
    with open(mcnemar_path, "w") as f:
        json.dump(mcnemar_summary, f, indent=2)

    print(f"\nScores written to {scores_path}")
    print(f"McNemar summary written to {mcnemar_path}")


if __name__ == "__main__":
    main()
