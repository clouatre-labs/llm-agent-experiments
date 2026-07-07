"""
score.py -- Experiment 9: Blind Scorer

Reads sessions/run-NN.json files and applies the exp9 rubric (C1-C8) to
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

EXP9_DIR = pathlib.Path(__file__).parent.resolve()
RESULTS_DIR = EXP9_DIR / "results"
SESSIONS_DIR = EXP9_DIR / "sessions"
RUBRIC_PATH = EXP9_DIR / "rubric.md"
LABEL_MAP_PATH = EXP9_DIR / "label-map.json"


def read_rubric() -> str:
    """Read the exp9 rubric."""
    if not RUBRIC_PATH.exists():
        raise FileNotFoundError(f"Rubric not found: {RUBRIC_PATH.resolve()}")
    return RUBRIC_PATH.read_text(encoding="utf-8")


def read_session_files(sessions_dir: pathlib.Path):
    """Yield (run_id, data) tuples for each run-NN.json file sorted by run_id."""
    session_files = sorted(sessions_dir.glob("run-*.json"))
    for sf in session_files:
        run_id = sf.stem  # e.g. "run-86"
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

    C1: Identifies and verifies a specific forge module file path
    C2: References a specific provider trait/struct pattern within the codebase
    C3: Identifies at least one relevant test file for forge providers
    C4: References issue #1205 or multi-forge architecture with structural code terms
    C5: Identifies provider-specific differences (at least 2)
    C6: Makes an explicit statement about auth flow differences across providers
    C7: Identifies a non-obvious architectural implication requiring code synthesis
    C8: Produces valid JSON output with all 11 required handoff schema fields
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

    output = data.get("response_text", data.get("output", ""))
    output_lower = output.lower()

    score = {}

    # C1: Check for forge module file path references
    has_file_ref = any(
        keyword in output_lower
        for keyword in ["forge", "crates/", "src/", ".rs", ".toml", "path:"]
    )
    score["C1"] = 1 if has_file_ref else 0

    # C2: Check for provider trait/struct pattern references
    has_pattern_ref = any(
        keyword in output_lower
        for keyword in [
            "struct",
            "enum ",
            "pattern",
            "trait",
            "impl ",
            "provider",
        ]
    )
    score["C2"] = 1 if has_pattern_ref else 0

    # C3: Check for test file or test function references
    has_test_ref = any(
        keyword in output_lower for keyword in ["test", "tests/", "_test"]
    )
    score["C3"] = 1 if has_test_ref else 0

    # C4: Check for issue #1205 or multi-forge domain + structural keywords
    has_issue_ref = "#1205" in output_lower
    has_forge_domain = any(
        kw in output_lower
        for kw in [
            "forge",
            "gitlab",
            "gitea",
            "forgejo",
            "azure devops",
            "azure-devops",
            "multi-forge",
            "codeberg",
        ]
    )
    has_structural = any(
        kw in output_lower
        for kw in ["trait", "aptu-core", "impl ", "backend", "provider"]
    )
    score["C4"] = 1 if (has_issue_ref or (has_forge_domain and has_structural)) else 0

    # C5: Check for provider-specific difference patterns (at least 2)
    provider_keywords = [
        "gitlab",
        "gitea",
        "forgejo",
        "azure devops",
        "azure-devops",
        "github",
        "auth",
        "api",
        "endpoint",
        "token",
    ]
    has_provider_refs = sum(1 for kw in provider_keywords if kw in output_lower)
    score["C5"] = 1 if has_provider_refs >= 2 else 0

    # C6: Check for auth flow difference references
    has_auth_ref = any(
        keyword in output_lower
        for keyword in [
            "auth",
            "token",
            "oauth",
            "pat",
            "authentication",
            "credential",
            "login",
            "access token",
        ]
    )
    score["C6"] = 1 if has_auth_ref else 0

    # C7: Check for non-obvious architectural implications
    has_arch_ref = any(
        keyword in output_lower
        for keyword in [
            "abstraction",
            "trait",
            "dispatch",
            "routing",
            "plugin",
            "rate limit",
            "versioning",
            "compat",
            "migration",
            "webhook",
            "parsing",
            "ssh",
            "https",
        ]
    )
    score["C7"] = 1 if has_arch_ref else 0

    # C8: Valid JSON per handoff schema (11 required fields)
    required_fields = {
        "session_id",
        "lens",
        "relevant_files",
        "conventions",
        "patterns",
        "related_issues",
        "constraints",
        "test_coverage",
        "library_findings",
        "approaches",
        "recommendation",
    }
    try:
        response_json = json.loads(output)
        score["C8"] = 1 if required_fields.issubset(set(response_json.keys())) else 0
    except (json.JSONDecodeError, TypeError, AttributeError):
        score["C8"] = 0

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
    parser = argparse.ArgumentParser(description="Blind scorer for Experiment 9")
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
