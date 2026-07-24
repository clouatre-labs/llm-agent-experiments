"""Thin CLI orchestrator for the context isolation experiment.

Loads GSM8K tasks, builds context per condition, calls the provider,
and writes session JSON files.
"""

import argparse
import json
import logging
import time
from datetime import UTC, datetime
from pathlib import Path

from conditions import build_context, estimate_tokens
from gsm8k import extract_gold_answer, load_gsm8k_sample
from providers import call_bedrock, call_openrouter

EXP10_DIR = Path(__file__).parent

# Mock distractor transcript for the contaminated condition.
# This simulates irrelevant planner/executor history that contaminates the context
# without leaking the gold answer. Contains no numeric patterns matching GSM8K answers.
_MOCK_DISTRACTOR = """Planner: We need to schedule the team standup for next week. What time works best?

Executor: I checked everyone's availability. Monday at 10 AM works for the whole team.

Planner: Let's also block out time for the quarterly review on Thursday.

Executor: The conference room is available from 1 PM to 3 PM on Thursday.

Planner: Should we invite the stakeholders to the review session?

Executor: Yes, I'll send out calendar invites to the product team and engineering leads.

Planner: Make sure to include the agenda in the invite so everyone can prepare.

Executor: Good idea. I'll draft the agenda and share it for feedback before sending."""

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

MODEL_CONFIGS = {
    "gemma4": {
        "provider": "openrouter",
        "model_id": "google/gemma-4-26b-it",
        "max_tokens": 4096,
        "temperature": 0.5,
        "json_mode": False,
    },
    "haiku45": {
        "provider": "bedrock",
        "model_id": "anthropic.claude-haiku-4-5-20251001-v1:0",
        "max_tokens": 4096,
        "temperature": 0.5,
        "json_mode": False,
    },
}


def _compute_target_tokens(tasks: list[dict], seed: int) -> int:
    """Compute the target token count for length-matching.

    Builds the contaminated context for each task and returns the max
    token count across all tasks (to ensure all conditions fit).
    """
    max_tokens = 0
    for task in tasks:
        ctx = build_context(
            task["question"], "contaminated", history=_MOCK_DISTRACTOR, seed=seed
        )
        tokens = estimate_tokens(ctx)
        max_tokens = max(max_tokens, tokens)
    return max_tokens


def run_single(
    run_id: str,
    condition: str,
    model_key: str,
    task: dict,
    target_tokens: int,
    config: dict,
    seed: int,
) -> dict:
    """Run a single inference and return the result dict."""
    context = build_context(
        task=task["question"],
        condition=condition,
        history=_MOCK_DISTRACTOR,
        target_token_count=target_tokens,
        seed=seed,
    )

    system_prompt = "You are a helpful assistant. Solve the math problem step by step and provide the final answer."

    if config["provider"] == "openrouter":
        result = call_openrouter(context, system_prompt, config["model_id"], config)
    else:
        result = call_bedrock(context, system_prompt, config["model_id"], config)

    gold_answer = extract_gold_answer(task["answer"])

    return {
        "run_id": run_id,
        "condition": condition,
        "model_key": model_key,
        "model_id": config["model_id"],
        "response_text": result.content,
        "gold_answer": gold_answer,
        "input_tokens": result.input_tokens,
        "output_tokens": result.output_tokens,
        "stop_reason": result.stop_reason,
        "success": result.success,
        "latency_ms": 0,
        "cost_usd": 0.0,
        "timestamp_utc": datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }


def write_session(result: dict, sessions_dir: Path) -> None:
    """Write a single session JSON file."""
    run_id = result["run_id"]
    condition = result["condition"]
    cond_dir = sessions_dir / condition
    cond_dir.mkdir(parents=True, exist_ok=True)
    path = cond_dir / f"{run_id}.json"
    with open(path, "w") as f:
        json.dump(result, f, indent=2)


def write_label_map(label_map: dict, path: Path) -> None:
    """Write the label map JSON file."""
    with open(path, "w") as f:
        json.dump(label_map, f, indent=2)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run context isolation experiment")
    parser.add_argument(
        "--condition",
        choices=["scoped", "full-history", "contaminated"],
        default="scoped",
    )
    parser.add_argument("--model", choices=list(MODEL_CONFIGS.keys()), default="gemma4")
    parser.add_argument("--runs", type=int, default=300)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print context lengths without calling API",
    )
    parser.add_argument(
        "--pilot", action="store_true", help="Run 5 tasks instead of full set"
    )
    parser.add_argument(
        "--skip-existing",
        action="store_true",
        help="Skip runs that already have session files",
    )
    args = parser.parse_args()

    sessions_dir = EXP10_DIR / "sessions"
    results_dir = EXP10_DIR / "results"
    sessions_dir.mkdir(parents=True, exist_ok=True)
    results_dir.mkdir(parents=True, exist_ok=True)

    # Load tasks
    n_runs = 5 if args.pilot else args.runs
    tasks = load_gsm8k_sample(seed=args.seed, n=n_runs)
    logger.info("Loaded %d GSM8K tasks (seed=%d)", len(tasks), n_runs)

    # Compute target token count for length-matching
    target_tokens = _compute_target_tokens(tasks, args.seed)
    logger.info("Target token count for length-matching: %d", target_tokens)

    if args.dry_run:
        for i, task in enumerate(tasks):
            for cond in ["scoped", "full-history", "contaminated"]:
                ctx = build_context(
                    task=task["question"],
                    condition=cond,
                    history=_MOCK_DISTRACTOR,
                    target_token_count=target_tokens,
                    seed=args.seed,
                )
                tokens = estimate_tokens(ctx)
                print(f"Task {i:03d} | {cond:15s} | {tokens:5d} tokens")
        return

    # Load or create label map
    label_map_path = EXP10_DIR / "label-map.json"
    if label_map_path.exists():
        with open(label_map_path) as f:
            label_map = json.load(f)
    else:
        label_map = {}

    config = MODEL_CONFIGS[args.model]
    results_list: list[dict] = []

    for i, task in enumerate(tasks):
        run_id = f"run-{i:03d}"
        cond_dir = sessions_dir / args.condition

        if args.skip_existing and (cond_dir / f"{run_id}.json").exists():
            logger.info("Skipping existing run: %s/%s", args.condition, run_id)
            continue

        logger.info(
            "Run %s/%s (%s, %s)", args.condition, run_id, args.model, args.condition
        )

        start = time.time()
        result = run_single(
            run_id=run_id,
            condition=args.condition,
            model_key=args.model,
            task=task,
            target_tokens=target_tokens,
            config=config,
            seed=args.seed,
        )
        result["latency_ms"] = int((time.time() - start) * 1000)

        write_session(result, sessions_dir)
        results_list.append(result)

        # Update label map
        label_map[run_id] = args.model
        write_label_map(label_map, label_map_path)

        logger.info(
            "  Done: %d tokens in %dms", result["output_tokens"], result["latency_ms"]
        )

    # Write latency log
    latency_path = results_dir / "latency_log.jsonl"
    with open(latency_path, "a") as f:
        f.writelines(
            json.dumps(
                {
                    "run_id": r["run_id"],
                    "condition": r["condition"],
                    "latency_ms": r["latency_ms"],
                    "input_tokens": r["input_tokens"],
                    "output_tokens": r["output_tokens"],
                }
            )
            + "\n"
            for r in results_list
        )

    # Write cost summary
    total_cost = sum(
        r.get("input_tokens", 0) * 0.000001 + r.get("output_tokens", 0) * 0.000003
        for r in results_list
    )
    cost_summary = {
        "condition": args.condition,
        "model": args.model,
        "runs_completed": len(results_list),
        "total_input_tokens": sum(r.get("input_tokens", 0) for r in results_list),
        "total_output_tokens": sum(r.get("output_tokens", 0) for r in results_list),
        "total_cost_usd": round(total_cost, 6),
        "timestamp_utc": datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }
    cost_path = results_dir / "cost_summary.json"
    with open(cost_path, "w") as f:
        json.dump(cost_summary, f, indent=2)

    logger.info(
        "Completed %d runs. Cost summary written to %s", len(results_list), cost_path
    )


if __name__ == "__main__":
    main()
