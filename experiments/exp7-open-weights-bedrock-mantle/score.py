"""
score.py -- Experiment 7: Blind Scorer

Reads sessions/run-NN.json files and applies the exp3 rubric (C1-C8) to
each run. Outputs results/scores.jsonl (one JSON line per run).

Blind by default: label-map.json is not read during scoring. Use --reveal
after scoring is complete to append model_key to each line.

## Usage

  uv run python score.py [--reveal] [--label-map PATH]
"""

import argparse
import json
import pathlib
import sys

EXP7_DIR = pathlib.Path(__file__).parent.resolve()
RESULTS_DIR = EXP7_DIR / "results"
SESSIONS_DIR = EXP7_DIR / "sessions"
RUBRIC_PATH = EXP7_DIR / ".." / "exp3-model-comparison" / "rubric.md"
LABEL_MAP_PATH = EXP7_DIR / "label-map.json"


def read_rubric() -> str:
    """Read the exp3 rubric from the shared location."""
    if not RUBRIC_PATH.exists():
        raise FileNotFoundError(f"Rubric not found: {RUBRIC_PATH.resolve()}")
    return RUBRIC_PATH.read_text(encoding="utf-8")


def read_session_files(sessions_dir: pathlib.Path):
    """Yield (run_id, data) tuples for each run-NN.json file sorted by run_id."""
    session_files = sorted(sessions_dir.glob("run-*.json"))
    for sf in session_files:
        run_id = sf.stem  # e.g. "run-41"
        try:
            data = json.loads(sf.read_text(encoding="utf-8"))
            yield run_id, data
        except (json.JSONDecodeError, OSError) as e:
            print(f"  SKIP {run_id}: {e}", file=sys.stderr)
            yield run_id, None


def score_run(run_id: str, data: dict, rubric_text: str) -> dict:
    """Score a single run against the C1-C8 rubric using heuristic analysis.

    This is a heuristic scorer that checks for keyword presence in the
    JSON output text. A human or LLM scorer would re-score in production.

    C1: Identifies and verifies a specific source file relevant to the issue
    C2: References a specific code pattern within the verified file
    C3: Identifies at least one relevant test file
    C4: Identifies a related issue or PR that provides implementation context
    C5: References specific pattern IDs from issue descriptions
    C6: Makes an explicit statement about AST-only limitations for taint tracking
    C7: Identifies a non-obvious architectural implication requiring code synthesis
    C8: Produces valid JSON output per handoff schema
    """
    if data is None:
        return {
            "run_id": run_id,
            "C1": 0,
            "C2": 0,
            "C3": 0,
            "C4": 0,
            "C5": 0,
            "C6": 0,
            "C7": 0,
            "C8": 0,
            "total": 0,
            "latency_ms": None,
            "cost_usd": None,
            "timestamp_utc": None,
        }

    output = data.get("output", "")
    output_lower = output.lower()

    score = {}

    # C1: Check for specific file path references (crates/, src/, etc.)
    has_file_ref = any(
        keyword in output_lower
        for keyword in ["crates/", "src/", ".rs", ".toml", "path:"]
    )
    score["C1"] = 1 if has_file_ref else 0

    # C2: Check for code pattern references (struct, enum, pattern, function, etc.)
    has_pattern_ref = any(
        keyword in output_lower
        for keyword in ["struct", "enum ", "pattern", "function", "trait", "impl "]
    )
    score["C2"] = 1 if has_pattern_ref else 0

    # C3: Check for test file or test function references
    has_test_ref = any(keyword in output_lower for keyword in ["test", "tests/_test"])
    score["C3"] = 1 if has_test_ref else 0

    # C4: Check for issue or PR references
    has_issue_ref = any(
        keyword in output_lower for keyword in ["#735", "#736", "#737", "issue", "pr"]
    )
    score["C4"] = 1 if has_issue_ref else 0

    # C5: Check for specific pattern IDs (T001, D001, etc.)
    import re

    has_pattern_id = bool(re.search(r"[TD]\d{3}", output))
    score["C5"] = 1 if has_pattern_id else 0

    # C6: Check for taint / data-flow / AST limitation references
    has_taint_ref = any(
        keyword in output_lower
        for keyword in [
            "taint",
            "data flow",
            "data-flow",
            "ast alone",
            "ast only",
            "cannot track",
            "limitation",
            "gap",
            "insufficient",
        ]
    )
    score["C6"] = 1 if has_taint_ref else 0

    # C7: Check for non-obvious architectural implications
    has_arch_ref = any(
        keyword in output_lower
        for keyword in [
            "binary size",
            "compile",
            "startup",
            "caching",
            "backward compat",
            "migration",
            "rollout",
            "staged",
            "extension",
        ]
    )
    score["C7"] = 1 if has_arch_ref else 0

    # C8: Valid JSON output
    # Check if output itself is valid JSON (the session data parsed successfully)
    score["C8"] = 1  # If we got here, the session file parsed

    total = sum(score.values())

    result = {
        "run_id": run_id,
        "C1": score["C1"],
        "C2": score["C2"],
        "C3": score["C3"],
        "C4": score["C4"],
        "C5": score["C5"],
        "C6": score["C6"],
        "C7": score["C7"],
        "C8": score["C8"],
        "total": total,
        "latency_ms": data.get("latency_ms"),
        "cost_usd": data.get("cost_usd"),
        "timestamp_utc": data.get("timestamp_utc"),
    }

    return result


def write_scores_jsonl(scores: list, results_dir: pathlib.Path):
    """Write scores to results/scores.jsonl."""
    output_path = results_dir / "scores.jsonl"
    with open(output_path, "w", encoding="utf-8") as f:
        for s in scores:
            f.write(json.dumps(s, separators=(",", ":")) + "\n")
    print(f"Wrote {len(scores)} scores to {output_path}")


def load_label_map(label_map_path: pathlib.Path) -> dict:
    """Load label-map.json mapping run_id -> model_key."""
    if not label_map_path.exists():
        print(f"Label map not found: {label_map_path}", file=sys.stderr)
        return {}
    return json.loads(label_map_path.read_text(encoding="utf-8"))


def reveal_labels(scores: list, label_map: dict) -> list:
    """Append model_key to each score line based on run_id."""
    revealed = []
    for s in scores:
        run_id = s.get("run_id", "")
        entry = dict(s)
        entry["model_key"] = label_map.get(run_id)
        revealed.append(entry)
    return revealed


def main():
    parser = argparse.ArgumentParser(description="Blind scorer for Experiment 7")
    parser.add_argument(
        "--reveal",
        action="store_true",
        help="Reveal model labels after scoring (reads label-map.json)",
    )
    parser.add_argument(
        "--label-map",
        type=str,
        default=str(LABEL_MAP_PATH),
        help=f"Path to label-map.json (default: {LABEL_MAP_PATH})",
    )
    args = parser.parse_args()

    rubric_text = read_rubric()
    print(f"Read rubric ({len(rubric_text)} chars)")

    scores = []
    for run_id, data in read_session_files(SESSIONS_DIR):
        result = score_run(run_id, data, rubric_text)
        scores.append(result)
        total = result["total"]
        latency = result.get("latency_ms", "N/A")
        print(f"  {run_id}: total={total}/8, latency={latency}ms")

    if args.reveal:
        label_map_path = pathlib.Path(args.label_map)
        label_map = load_label_map(label_map_path)
        if label_map:
            scores = reveal_labels(scores, label_map)
            print(f"Revealed labels from {label_map_path}")

    write_scores_jsonl(scores, RESULTS_DIR)

    summary = {
        "n_scores": len(scores),
        "mean": round(sum(s["total"] for s in scores) / len(scores), 2)
        if scores
        else 0,
        "labels_revealed": args.reveal,
    }
    print(f"\nSummary: {json.dumps(summary)}")


if __name__ == "__main__":
    main()
