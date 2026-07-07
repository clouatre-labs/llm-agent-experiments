"""
run_inference.py -- Experiment 8: OpenRouter Model Evaluation

Runs Gemma 4 26B-A4B, Claude Haiku 4.5, and Claude Sonnet 4.6 through
a single OpenRouter endpoint (base_url=https://openrouter.ai/api/v1) on
the exp3-model-comparison runner prompt. Strips all Bedrock/boto3 code
from the exp7 pattern, routing every model through the openai.OpenAI SDK
with base_url override.

## Auth

API key from OPENROUTER_API_KEY environment variable.
OpenRouter base URL: https://openrouter.ai/api/v1

## Usage

  uv run python run_inference.py [--dry-run] [--model MODEL_KEY] [--runs N]

  --dry-run   Print config and exit; no API calls
  --model     One of: gemma4, haiku45, sonnet46 (default: all)
  --runs      Number of runs per model (default: 10)
"""

import argparse
import json
import os
import pathlib
import random
import sys
import time
from datetime import UTC, datetime

import openai

# --- Model Configuration ---

MODEL_CONFIGS = {
    "gemma4": {
        "model_id": "google/gemma-4-26b-a4b-it",
        "run_ids": [
            "run-56",
            "run-57",
            "run-58",
            "run-59",
            "run-60",
            "run-61",
            "run-62",
            "run-63",
            "run-64",
            "run-65",
        ],
        "input_price_per_mtok": 0.06,
        "output_price_per_mtok": 0.33,
    },
    "haiku45": {
        "model_id": "anthropic/claude-haiku-4.5",
        "run_ids": [
            "run-66",
            "run-67",
            "run-68",
            "run-69",
            "run-70",
            "run-71",
            "run-72",
            "run-73",
            "run-74",
            "run-75",
        ],
        "input_price_per_mtok": 1.00,
        "output_price_per_mtok": 5.00,
    },
    "sonnet46": {
        "model_id": "anthropic/claude-sonnet-4.6",
        "run_ids": [
            "run-76",
            "run-77",
            "run-78",
            "run-79",
            "run-80",
            "run-81",
            "run-82",
            "run-83",
            "run-84",
            "run-85",
        ],
        "input_price_per_mtok": 3.00,
        "output_price_per_mtok": 15.00,
    },
}

EXP8_DIR = pathlib.Path(__file__).parent.resolve()
RESULTS_DIR = EXP8_DIR / "results"
SESSIONS_DIR = EXP8_DIR / "sessions"
LABEL_MAP_PATH = EXP8_DIR / "label-map.json"
RUNNER_PROMPT_PATH = EXP8_DIR / ".." / "exp3-model-comparison" / "runner-prompt.md"

OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"


def build_client() -> openai.OpenAI:
    """Return an OpenAI client routed through OpenRouter."""
    api_key = os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        raise ValueError("OPENROUTER_API_KEY environment variable is required")
    return openai.OpenAI(
        base_url=OPENROUTER_BASE_URL,
        api_key=api_key,
    )


def read_runner_prompt() -> str:
    """Read the exp3 runner prompt relative to this script's directory."""
    if not RUNNER_PROMPT_PATH.exists():
        raise FileNotFoundError(
            f"Runner prompt not found: {RUNNER_PROMPT_PATH.resolve()}"
        )
    return RUNNER_PROMPT_PATH.read_text(encoding="utf-8")


def compute_cost_usd(input_tokens: int, output_tokens: int, config: dict) -> float:
    """Compute cost in USD based on token counts and model pricing."""
    input_cost = (input_tokens / 1_000_000) * config["input_price_per_mtok"]
    output_cost = (output_tokens / 1_000_000) * config["output_price_per_mtok"]
    return round(input_cost + output_cost, 10)


def run_single(run_id: str, model_key: str, prompt: str, dry_run: bool) -> dict:
    """Run inference via OpenRouter endpoint using the OpenAI SDK."""
    config = MODEL_CONFIGS[model_key]
    model_id = config["model_id"]

    if dry_run:
        return {
            "run_id": run_id,
            "model_id": model_id,
            "model_key": model_key,
            "response_text": "[dry-run]",
            "input_tokens": 0,
            "output_tokens": 0,
            "latency_ms": 0,
            "cost_usd": 0.0,
            "timestamp_utc": datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
        }

    client = build_client()
    start = time.monotonic()

    max_retries = 3
    for attempt in range(max_retries + 1):
        try:
            response = client.chat.completions.create(
                model=model_id,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=4096,
                temperature=0.5,
            )
            break
        except openai.RateLimitError as e:
            if attempt < max_retries:
                delay = (2 ** (attempt + 1)) + random.random()
                print(
                    f"  Rate limited, retrying in {delay:.1f}s "
                    f"(attempt {attempt + 1}/{max_retries})",
                    file=sys.stderr,
                )
                time.sleep(delay)
            else:
                raise e

    latency_ms = int((time.monotonic() - start) * 1000)
    output_text = response.choices[0].message.content or ""
    input_tokens = response.usage.prompt_tokens if response.usage else 0
    output_tokens = response.usage.completion_tokens if response.usage else 0
    cost_usd = compute_cost_usd(input_tokens, output_tokens, config)

    return {
        "run_id": run_id,
        "model_id": model_id,
        "model_key": model_key,
        "response_text": output_text,
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "latency_ms": latency_ms,
        "cost_usd": cost_usd,
        "timestamp_utc": datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }


def write_label_map():
    """Write label-map.json mapping all run IDs to model keys."""
    label_map = {}
    for model_key, config in MODEL_CONFIGS.items():
        for run_id in config["run_ids"]:
            label_map[run_id] = model_key
    LABEL_MAP_PATH.write_text(
        json.dumps(label_map, separators=(",", ":")), encoding="utf-8"
    )
    print(f"Wrote label map ({len(label_map)} entries) to {LABEL_MAP_PATH}")


def write_session(result: dict):
    """Write a single session file to sessions/."""
    run_id = result["run_id"]
    output_path = SESSIONS_DIR / f"{run_id}.json"
    output_path.write_text(json.dumps(result, indent=2, default=str), encoding="utf-8")
    print(f"  Wrote {output_path}")


def append_latency_log(result: dict):
    """Append a latency entry to results/latency.jsonl."""
    latency_entry = {
        "run_id": result["run_id"],
        "model_id": result["model_id"],
        "model_key": result["model_key"],
        "latency_ms": result["latency_ms"],
        "input_tokens": result["input_tokens"],
        "output_tokens": result["output_tokens"],
        "cost_usd": result["cost_usd"],
        "timestamp_utc": result["timestamp_utc"],
    }
    latency_log_path = RESULTS_DIR / "latency.jsonl"
    with open(latency_log_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(latency_entry, separators=(",", ":")) + "\n")


def write_cost_summary(results: list[dict]):
    """Write results/cost_summary.json after all runs."""
    summary = {}
    for r in results:
        mk = r["model_key"]
        if mk not in summary:
            summary[mk] = {
                "model_key": mk,
                "model_id": r["model_id"],
                "n_runs": 0,
                "total_cost_usd": 0.0,
                "total_input_tokens": 0,
                "total_output_tokens": 0,
                "runs": [],
            }
        s = summary[mk]
        s["n_runs"] += 1
        s["total_cost_usd"] += r.get("cost_usd") or 0.0
        s["total_input_tokens"] += r.get("input_tokens") or 0
        s["total_output_tokens"] += r.get("output_tokens") or 0
        latency = r.get("latency_ms")
        cost = r.get("cost_usd")
        s["runs"].append(
            {
                "run_id": r["run_id"],
                "latency_ms": latency,
                "cost_usd": cost,
            }
        )

    for mk in summary:
        s = summary[mk]
        s["mean_cost_usd"] = round(s["total_cost_usd"] / s["n_runs"], 10)

    cost_summary_path = RESULTS_DIR / "cost_summary.json"
    cost_summary_path.write_text(
        json.dumps(summary, indent=2, default=str), encoding="utf-8"
    )
    print(f"Wrote cost summary to {cost_summary_path}")


def print_dry_run():
    """Print configuration and exit without making API calls."""
    print(f"{'=' * 60}")
    print("Experiment 8: OpenRouter Model Evaluation (DRY RUN)")
    print(f"{'=' * 60}")

    for model_key, config in MODEL_CONFIGS.items():
        print(f"\nModel: {model_key}")
        print(f"  Model ID:        {config['model_id']}")
        print(f"  Run IDs:         {', '.join(config['run_ids'])}")
        print(
            f"  Pricing:         "
            f"${config['input_price_per_mtok']}/M input, "
            f"${config['output_price_per_mtok']}/M output"
        )

    print(f"\n{'=' * 60}")
    print("No API calls were made.")
    sys.exit(0)


def main():
    parser = argparse.ArgumentParser(description="Run inference for Experiment 8")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print config and exit; no API calls",
    )
    parser.add_argument(
        "--model",
        type=str,
        choices=list(MODEL_CONFIGS.keys()),
        default=None,
        help="Model to run (default: all)",
    )
    parser.add_argument(
        "--runs",
        type=int,
        default=10,
        help="Number of runs per model (default: 10)",
    )
    args = parser.parse_args()

    if args.dry_run:
        print_dry_run()

    # Ensure directories exist
    SESSIONS_DIR.mkdir(parents=True, exist_ok=True)
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    # Write label map before any API calls
    write_label_map()

    # Read the runner prompt
    prompt = read_runner_prompt()

    # Determine which models to run
    model_keys = [args.model] if args.model else list(MODEL_CONFIGS.keys())

    all_results = []

    for model_key in model_keys:
        config = MODEL_CONFIGS[model_key]
        print(f"\n--- Running {model_key} ({config['model_id']}) ---")

        for run_id in config["run_ids"][: args.runs]:
            print(f"  Starting {run_id}...")
            try:
                result = run_single(model_key, run_id, prompt, dry_run=False)
                write_session(result)
                append_latency_log(result)
                all_results.append(result)
                print(
                    f"  Done: {run_id} | "
                    f"latency={result['latency_ms']}ms | "
                    f"cost=${result['cost_usd']} | "
                    f"tokens={result['input_tokens']}+{result['output_tokens']}"
                )
            except Exception as e:
                error_result = {
                    "run_id": run_id,
                    "model_id": config["model_id"],
                    "model_key": model_key,
                    "error": str(e),
                    "latency_ms": None,
                    "cost_usd": None,
                    "timestamp_utc": datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
                }
                write_session(error_result)
                all_results.append(error_result)
                print(f"  ERROR: {run_id} -- {e}")

    # Write cost summary after all runs
    write_cost_summary(all_results)

    print(f"\n{'=' * 60}")
    print("Inference complete.")
    print(f"Session files: {SESSIONS_DIR}")
    print(f"Latency log:   {RESULTS_DIR / 'latency.jsonl'}")
    print(f"Cost summary:  {RESULTS_DIR / 'cost_summary.json'}")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    main()
