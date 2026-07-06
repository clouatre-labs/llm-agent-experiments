"""
run_inference.py -- Experiment 7: Open-Weights Models on Bedrock Mantle

Runs Gemma 4 26B-A4B (Bedrock Mantle) and Claude Haiku 4.5 / Sonnet 4.6
(Bedrock Runtime) on the exp3-model-comparison runner prompt. Routes all
inference calls through Cloudflare AI Gateway for observability.

## Auth

Gemma 4 via Bedrock Mantle endpoint:
  Endpoint: https://bedrock-mantle.us-east-1.api.aws/openai/v1/
  Auth: SigV4 signed requests using botocore credentials
  SDK: OpenAI client with custom httpx transport that adds Authorization header

Claude models via Bedrock Runtime (us-east-1):
  Auth: Standard boto3 credentials (IAM role / environment)
  SDK: boto3 bedrock-runtime converse API

## Cloudflare AI Gateway

All requests proxy through:
  https://gateway.ai.cloudflare.com/v1/{CLOUDFLARE_ACCOUNT_ID}/{GATEWAY_SLUG}/

Required env vars:
  CLOUDFLARE_ACCOUNT_ID  -- Cloudflare account ID
  CLOUDFLARE_API_TOKEN   -- Cloudflare API token
  AWS_DEFAULT_REGION     -- must be us-east-1
  AWS_ACCESS_KEY_ID      -- or use IAM role
  AWS_SECRET_ACCESS_KEY  -- or use IAM role

## Usage

  uv run python run_inference.py [--dry-run] [--model MODEL_KEY] [--runs N]

  --dry-run   Print config and exit; no API calls
  --model     One of: gemma4, haiku45, sonnet46 (default: all)
  --runs      Number of runs per model (default: 5)
"""

import argparse
import json
import os
import pathlib
import sys
import time
from datetime import UTC, datetime

import boto3
import httpx

# --- Model Configuration ---

MODEL_CONFIGS = {
    "gemma4": {
        "model_id": "google.gemma-4-26b-a4b",
        "endpoint": "bedrock-mantle",
        "run_ids": ["run-41", "run-42", "run-43", "run-44", "run-45"],
        "input_price_per_mtok": 0.13,
        "output_price_per_mtok": 0.40,
    },
    "haiku45": {
        "model_id": "global.anthropic.claude-haiku-4-5-20251001-v1:0",
        "endpoint": "bedrock-runtime",
        "run_ids": ["run-46", "run-47", "run-48", "run-49", "run-50"],
        "input_price_per_mtok": 1.00,
        "output_price_per_mtok": 5.00,
    },
    "sonnet46": {
        "model_id": "global.anthropic.claude-sonnet-4-6",
        "endpoint": "bedrock-runtime",
        "run_ids": ["run-51", "run-52", "run-53", "run-54", "run-55"],
        "input_price_per_mtok": 3.00,
        "output_price_per_mtok": 15.00,
    },
}

EXP7_DIR = pathlib.Path(__file__).parent.resolve()
RESULTS_DIR = EXP7_DIR / "results"
SESSIONS_DIR = EXP7_DIR / "sessions"
RUNNER_PROMPT_PATH = EXP7_DIR / ".." / "exp3-model-comparison" / "runner-prompt.md"

CLOUDFLARE_GATEWAY_URL = (
    "https://gateway.ai.cloudflare.com/v1/{account_id}/{gateway_slug}/"
)

MANTLE_BASE_URL = "https://bedrock-mantle.us-east-1.api.aws/openai/v1/"


def build_sigv4_client(model_key: str):
    """Return an OpenAI-compatible client for Bedrock Mantle with SigV4 auth.

    Uses AWS SigV4 signing via botocore/auth and httpx transport layer.
    """
    import openai

    region = os.environ.get("AWS_DEFAULT_REGION", "us-east-1")

    # Build a custom httpx transport that signs each request with SigV4.
    # Uses botocore directly (stdlib-stable, no third-party aws_requests_auth
    # dependency on the signing hot path).
    import botocore.auth
    import botocore.awsrequest
    import botocore.credentials
    import botocore.session as bc_session

    bc = bc_session.get_session()
    credentials = bc.get_credentials().get_frozen_credentials()
    signer = botocore.auth.SigV4Auth(credentials, "bedrock", region)

    class SigV4Transport(httpx.BaseTransport):
        """httpx transport that signs each request with botocore SigV4."""

        def __init__(self):
            self._transport = httpx.HTTPTransport()

        def handle_request(self, request: httpx.Request) -> httpx.Response:
            body = request.read()
            aws_request = botocore.awsrequest.AWSRequest(
                method=request.method,
                url=str(request.url),
                data=body,
                headers=dict(request.headers),
            )
            signer.add_auth(aws_request)
            # Transfer signed headers back onto the httpx request
            for key, value in aws_request.headers.items():
                request.headers[key] = value
            # Restore the request body for the underlying transport
            request._content = body
            return self._transport.handle_request(request)

        def close(self) -> None:
            self._transport.close()

    client = openai.OpenAI(
        base_url=MANTLE_BASE_URL,
        api_key="placeholder",  # replaced by SigV4 Authorization header
        http_client=httpx.Client(transport=SigV4Transport()),
    )
    return client


def build_boto_client():
    """Return a boto3 bedrock-runtime client."""
    region = os.environ.get("AWS_DEFAULT_REGION", "us-east-1")
    return boto3.Session(region_name=region).client("bedrock-runtime")


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


def run_mantle(run_id: str, model_key: str, prompt: str, dry_run: bool) -> dict:
    """Run inference via Bedrock Mantle endpoint with SigV4 auth."""
    config = MODEL_CONFIGS[model_key]
    model_id = config["model_id"]

    if dry_run:
        return {
            "run_id": run_id,
            "model_id": model_id,
            "model_key": model_key,
            "output": "[dry-run]",
            "input_tokens": 0,
            "output_tokens": 0,
            "latency_ms": 0,
            "cost_usd": 0.0,
            "timestamp_utc": datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
        }

    client = build_sigv4_client(model_key)
    start = time.monotonic()

    response = client.chat.completions.create(
        model=model_id,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=4096,
        temperature=0.5,
    )

    latency_ms = int((time.monotonic() - start) * 1000)
    output_text = response.choices[0].message.content or ""
    input_tokens = response.usage.prompt_tokens if response.usage else 0
    output_tokens = response.usage.completion_tokens if response.usage else 0
    cost_usd = compute_cost_usd(input_tokens, output_tokens, config)

    return {
        "run_id": run_id,
        "model_id": model_id,
        "model_key": model_key,
        "output": output_text,
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "latency_ms": latency_ms,
        "cost_usd": cost_usd,
        "timestamp_utc": datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }


def run_bedrock_runtime(
    run_id: str, model_key: str, prompt: str, dry_run: bool
) -> dict:
    """Run inference via Bedrock Runtime Converse API."""
    config = MODEL_CONFIGS[model_key]
    model_id = config["model_id"]

    if dry_run:
        return {
            "run_id": run_id,
            "model_id": model_id,
            "model_key": model_key,
            "output": "[dry-run]",
            "input_tokens": 0,
            "output_tokens": 0,
            "latency_ms": 0,
            "cost_usd": 0.0,
            "timestamp_utc": datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
        }

    client = build_boto_client()
    start = time.monotonic()

    response = client.converse(
        modelId=model_id,
        messages=[{"role": "user", "content": [{"text": prompt}]}],
        inferenceConfig={
            "maxTokens": 4096,
            "temperature": 0.5,
        },
    )

    latency_ms = int((time.monotonic() - start) * 1000)
    output_text = response["output"]["message"]["content"][0]["text"]

    usage = response.get("usage", {})
    input_tokens = usage.get("inputTokens", 0)
    output_tokens = usage.get("outputTokens", 0)
    cost_usd = compute_cost_usd(input_tokens, output_tokens, config)

    return {
        "run_id": run_id,
        "model_id": model_id,
        "model_key": model_key,
        "output": output_text,
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "latency_ms": latency_ms,
        "cost_usd": cost_usd,
        "timestamp_utc": datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }


def run_single(model_key: str, run_id: str, prompt: str, dry_run: bool) -> dict:
    """Dispatch a single inference run based on endpoint type."""
    config = MODEL_CONFIGS[model_key]
    if config["endpoint"] == "bedrock-mantle":
        return run_mantle(run_id, model_key, prompt, dry_run)
    elif config["endpoint"] == "bedrock-runtime":
        return run_bedrock_runtime(run_id, model_key, prompt, dry_run)
    else:
        raise ValueError(f"Unknown endpoint: {config['endpoint']}")


def write_session(result: dict):
    """Write a single session file to sessions/."""
    run_id = result["run_id"]
    output_path = SESSIONS_DIR / f"{run_id}.json"
    output_path.write_text(json.dumps(result, indent=2, default=str), encoding="utf-8")
    print(f"  Wrote {output_path}")


def append_latency_log(result: dict):
    """Append a latency entry to results/latency-log.jsonl."""
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
    latency_log_path = RESULTS_DIR / "latency-log.jsonl"
    with open(latency_log_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(latency_entry, separators=(",", ":")) + "\n")


def print_dry_run():
    """Print model configurations for dry-run mode."""
    print("=" * 60)
    print("DRY RUN: Model Configurations")
    print("=" * 60)
    for key, config in MODEL_CONFIGS.items():
        print(f"\nModel key: {key}")
        print(f"  Model ID:        {config['model_id']}")
        print(f"  Endpoint:        {config['endpoint']}")
        print(f"  Input price/M:   ${config['input_price_per_mtok']}")
        print(f"  Output price/M:  ${config['output_price_per_mtok']}")
        print(f"  Run IDs:         {', '.join(config['run_ids'])}")

    print(f"\n{'=' * 60}")
    print("No API calls were made.")
    sys.exit(0)


def main():
    parser = argparse.ArgumentParser(description="Run inference for Experiment 7")
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
        default=5,
        help="Number of runs per model (default: 5)",
    )
    args = parser.parse_args()

    if args.dry_run:
        print_dry_run()

    # Ensure directories exist
    SESSIONS_DIR.mkdir(parents=True, exist_ok=True)
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    # Read the runner prompt
    prompt = read_runner_prompt()

    # Determine which models to run
    model_keys = [args.model] if args.model else list(MODEL_CONFIGS.keys())

    for model_key in model_keys:
        config = MODEL_CONFIGS[model_key]
        print(f"\n--- Running {model_key} ({config['model_id']}) ---")

        for run_id in config["run_ids"][: args.runs]:
            print(f"  Starting {run_id}...")
            try:
                result = run_single(model_key, run_id, prompt, dry_run=False)
                write_session(result)
                append_latency_log(result)
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
                print(f"  ERROR: {run_id} -- {e}")

    print(f"\n{'=' * 60}")
    print("Inference complete.")
    print(f"Session files: {SESSIONS_DIR}")
    print(f"Latency log:   {RESULTS_DIR / 'latency-log.jsonl'}")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    main()
