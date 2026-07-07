# Experiment 8: OpenRouter Model Evaluation

## Research Question

How does Gemma 4 26B-A4B compare to Claude Haiku 4.5 and Claude Sonnet 4.6 on prompt-only structured reasoning when the API endpoint is held constant?

## Context

This experiment evaluates Gemma 4 26B-A4B, Claude Haiku 4.5, and Claude Sonnet 4.6 through a single endpoint (OpenRouter) using the OpenAI SDK. It controls for the endpoint confound present in Experiment 7, where Gemma 4 used Bedrock Mantle while the Claude models used Bedrock Runtime. By routing all models through OpenRouter with identical client code, any performance differences can be attributed to model capability rather than infrastructure.

Cost motivation: Gemma 4 on OpenRouter is priced at $0.06/$0.33 per 1M tokens (input/output) vs. Claude Haiku 4.5 at $1.00/$5.00 and Sonnet 4.6 at $3.00/$15.00 -- a 16-50x price gap at the input tier.

## Models Tested

| Model | Provider | Endpoint | Price (input/output per 1M) |
|-------|----------|----------|----------------------------|
| Gemma 4 26B-A4B | Google (via OpenRouter) | OpenRouter | $0.06 / $0.33 |
| Claude Haiku 4.5 | Anthropic (via OpenRouter) | OpenRouter | $1.00 / $5.00 |
| Claude Sonnet 4.6 | Anthropic (via OpenRouter) | OpenRouter | $3.00 / $15.00 |

## Results

| Model | n valid | Mean | P50 latency | Error rate | Verdict |
|-------|---------|------|-------------|------------|---------|
| Gemma 4 26B-A4B | -- | -- | -- | -- | pending |
| Claude Haiku 4.5 | -- | -- | -- | -- | pending |
| Claude Sonnet 4.6 | -- | -- | -- | -- | pending |

*Results table to be filled after inference and scoring.*

## Run Configuration

| Field | Value |
|-------|-------|
| Runs per model | 10 |
| Total runs | 30 |
| Run IDs | run-56 to run-85 |
| Prompt | exp3 runner-prompt.md (runner-v1) |
| Rubric | exp3 rubric.md (C1-C8) |
| Temperature | 0.5 |
| Max tokens | 4096 |

## Outputs

- `sessions/run-NN.json` -- Per-run session records (30 files)
- `label-map.json` -- Run ID to model key mapping (sealed before scoring)
- `results/latency.jsonl` -- Latency and cost log
- `results/cost_summary.json` -- Aggregated cost per model
- `results/scores.jsonl` -- Blind rubric scores

## Gate Criteria

Same as exp3: mean >= 5.3, min >= 5, error rate <= 0.2, Mann-Whitney p >= 0.05.

## Methodology

See [parent repository README](../../README.md) for full methodology and architectural overview.

## Relationship to Blog Post

This experiment tests whether Gemma 4 can match proprietary model quality on a structured reasoning task when served through an identical API surface. If Gemma 4 passes the gate, it supports the thesis that open-weight models are viable replacements for proprietary delegates in agentic workflows at 16-50x lower cost. If it fails, the confound-controlled result strengthens the evidence that the quality gap is intrinsic to model capability rather than endpoint choice.