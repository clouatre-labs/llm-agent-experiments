"""Thin CLI orchestrator for the adversarial QA experiment.

Loads TriviaQA tasks, builds context per condition, calls the provider,
and writes session JSON files. Supports --pilot mode with gate logic.
"""

import argparse
import json
import logging
import random
import time
from datetime import UTC, datetime
from pathlib import Path

from conditions import Condition, build_context, estimate_tokens
from providers import call_bedrock, call_openrouter
from triviaqa import is_correct, load_triviaqa_sample
from wrong_answer import generate_wrong_answer

EXP11_DIR = Path(__file__).parent

# Mock distractor transcript for the contaminated condition.
# This simulates irrelevant prior-session turns that contaminate the context
# without leaking the gold answer.
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

    Uses the contaminated condition with mock distractor as the reference.
    """
    contaminated_lengths = []
    for task in tasks:
        ctx = build_context(
            task=task["question"],
            condition="contaminated",
            history=_MOCK_DISTRACTOR,
            seed=seed,
        )
        contaminated_lengths.append(estimate_tokens(ctx))
    return max(contaminated_lengths) if contaminated_lengths else 0


def run_single(
    run_id: str,
    condition: Condition,
    model_key: str,
    task: dict,
    target_tokens: int,
    config: dict,
    seed: int,
) -> dict:
    """Run a single inference task.

    For the contaminated condition, builds synthetic prior-session turns
    with wrong answers from the same category.
    """
    question = task["question"]
    gold_answer = task["gold_answer"]
    answer_dict = task["answer"]

    if condition == "contaminated":
        # Build synthetic history with wrong answers
        rng = random.Random(seed + int(run_id.split("-")[-1]))
        wrong = generate_wrong_answer(
            gold_answer=gold_answer,
            answer_type=answer_dict.get("type"),
            dataset=[task],
            rng=rng,
        )
        # If no wrong answer found from dataset, use a generic one
        if wrong == "unknown":
            wrong = "unknown"
        synthetic_turns = [
            "Q: What is the capital of France?\nA: Paris",
            "Q: Who wrote Romeo and Juliet?\nA: William Shakespeare",
            f"Q: {question}\nA: {wrong}",
        ]
        history = "\n\n".join(synthetic_turns)
    else:
        history = _MOCK_DISTRACTOR

    context = build_context(
        task=question,
        condition=condition,
        history=history,
        target_token_count=target_tokens,
        seed=seed,
    )

    system_prompt = "Answer the following question concisely. Provide only the answer, no explanation."

    provider = config["provider"]
    model_id = config["model_id"]

    if provider == "openrouter":
        result = call_openrouter(
            prompt=context,
            system=system_prompt,
            model_id=model_id,
            config=config,
        )
    elif provider == "bedrock":
        result = call_bedrock(
            prompt=context,
            system=system_prompt,
            model_id=model_id,
            config=config,
        )
    else:
        raise ValueError(f"Unknown provider: {provider}")

    response_text = result.content
    correct = is_correct(response_text, answer_dict)

    return {
        "run_id": run_id,
        "condition": condition,
        "model": model_key,
        "task_id": task["task_id"],
        "question": question,
        "gold_answer": gold_answer,
        "answer": answer_dict,
        "response_text": response_text,
        "correct": correct,
        "input_tokens": result.input_tokens,
        "output_tokens": result.output_tokens,
        "stop_reason": result.stop_reason,
        "success": result.success,
    }


def write_session(result: dict, sessions_dir: Path) -> None:
    """Write a single session result to a JSON file."""
    cond_dir = sessions_dir / result["condition"]
    cond_dir.mkdir(parents=True, exist_ok=True)
    path = cond_dir / f"{result['run_id']}.json"
    with open(path, "w") as f:
        json.dump(result, f, indent=2)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run adversarial QA experiment")
    parser.add_argument(
        "--condition",
        choices=["scoped", "contaminated", "full-history"],
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
        "--pilot",
        action="store_true",
        help="Run 30 tasks instead of full set; after contaminated run, compute gap and gate",
    )
    parser.add_argument(
        "--skip-existing",
        action="store_true",
        help="Skip runs that already have session files",
    )
    args = parser.parse_args()

    sessions_dir = EXP11_DIR / "sessions"
    results_dir = EXP11_DIR / "results"
    sessions_dir.mkdir(parents=True, exist_ok=True)
    results_dir.mkdir(parents=True, exist_ok=True)

    # Load tasks
    n_runs = 30 if args.pilot else args.runs
    tasks = load_triviaqa_sample(seed=args.seed, n=n_runs)
    logger.info("Loaded %d TriviaQA tasks (seed=%d)", len(tasks), n_runs)

    # Compute target token count for length-matching
    target_tokens = _compute_target_tokens(tasks, args.seed)
    logger.info("Target token count for length-matching: %d", target_tokens)

    if args.dry_run:
        for i, task in enumerate(tasks):
            for cond in ["scoped", "contaminated", "full-history"]:
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

    # Pilot gate: after contaminated run, compute gap and print STOP/PROCEED
    if args.pilot and args.condition == "contaminated":
        # Load scoped sessions for comparison
        scoped_dir = sessions_dir / "scoped"
        contaminated_dir = sessions_dir / "contaminated"
        scoped_records = []
        contaminated_records = []
        if scoped_dir.exists():
            for p in sorted(scoped_dir.glob("*.json")):
                with open(p) as f:
                    scoped_records.append(json.load(f))
        if contaminated_dir.exists():
            for p in sorted(contaminated_dir.glob("*.json")):
                with open(p) as f:
                    contaminated_records.append(json.load(f))

        if scoped_records and contaminated_records:
            scoped_correct = sum(1 for r in scoped_records if r.get("correct", False))
            contaminated_correct = sum(
                1 for r in contaminated_records if r.get("correct", False)
            )
            scoped_acc = scoped_correct / len(scoped_records)
            contaminated_acc = contaminated_correct / len(contaminated_records)
            gap = (scoped_acc - contaminated_acc) * 100

            print("\n=== Pilot Gate Results ===")
            print(
                f"Scoped accuracy:       {scoped_acc:.4f} ({scoped_correct}/{len(scoped_records)})"
            )
            print(
                f"Contaminated accuracy: {contaminated_acc:.4f} ({contaminated_correct}/{len(contaminated_records)})"
            )
            print(f"Gap:                   {gap:.2f} pp")
            if gap < 8.0:
                print("STOP: Gap < 8pp. Contamination effect insufficient to proceed.")
            else:
                print("PROCEED: Gap >= 8pp. Contamination effect confirmed.")


if __name__ == "__main__":
    main()
