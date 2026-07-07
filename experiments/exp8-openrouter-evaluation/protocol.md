# Experiment 8: OpenRouter Model Evaluation -- Protocol

## Pre-registration

Pre-registration date: 2026-07-07

## Research Question

How does Gemma 4 26B-A4B compare to Claude Haiku 4.5 and Claude Sonnet 4.6 on prompt-only structured reasoning when the API endpoint is held constant?

## Motivation

Experiment 7 (Bedrock Mantle vs. Bedrock Runtime) showed promising cost efficiency for Gemma 4 but fell short of the 5.3 gate threshold. However, exp7 had a confound: Gemma 4 was served via Bedrock Mantle (OpenAI-compatible endpoint) while Claude models used Bedrock Runtime (Converse API). This experiment controls for endpoint by routing all three models through a single endpoint (OpenRouter), testing whether the exp7 quality gap was due to model capability differences or infrastructure artifacts.

## Models Tested

| Model key | Model ID | Endpoint | Input price / 1M | Output price / 1M |
|-----------|----------|----------|-------------------|--------------------|
| gemma4 | google/gemma-4-26b-a4b-it | OpenRouter | $0.06 | $0.33 |
| haiku45 | anthropic/claude-haiku-4.5 | OpenRouter | $1.00 | $5.00 |
| sonnet46 | anthropic/claude-sonnet-4.6 | OpenRouter | $3.00 | $15.00 |

## Prompt Set Source

`experiments/exp3-model-comparison/runner-prompt.md` -- verbatim, no modifications.

## Scoring Rubric Source

`experiments/exp3-model-comparison/rubric.md` -- verbatim, no modifications.

Criterion summary (8 criteria, each scored 0 or 1):

- C1: File path reference
- C2: Code pattern reference
- C3: Test file reference
- C4: Issue/PR reference
- C5: Specific pattern IDs
- C6: Taint/AST limitation gap
- C7: Non-obvious architectural implication
- C8: Valid JSON output

## Run Configuration

n = 10 per model, runs 56-85 (continuing exp7 numbering which ended at run-55).

| Runs | Model | Label |
|------|-------|-------|
| 56-65 | google/gemma-4-26b-a4b-it | gemma4 |
| 66-75 | anthropic/claude-haiku-4.5 | haiku45 |
| 76-85 | anthropic/claude-sonnet-4.6 | sonnet46 |

## Blind Scoring Procedure

1. Scorer receives run files, rubric, and no other metadata.
2. `label-map.json` is sealed before spawning any delegates.
3. Scoring produces `results/scores.jsonl` without model_key values.
4. After `scores.jsonl` is complete, label-map is revealed and model_key appended via --reveal flag.

## Gate Criteria

Same as exp3:

- **Mean >= 5.3** (aggregate rubric score across 8 criteria)
- **Min >= 5** (lowest single run score)
- **Error rate <= 0.2** (fraction of invalid/non-JSON outputs)
- **Mann-Whitney p >= 0.05** (against baseline, if applicable)

Verdict: **pass** if all four criteria met; **fail** if any criterion not met.

## Relationship to Experiment 7

Exp7 compared Gemma 4 (Bedrock Mantle) against Claude Haiku 4.5 and Sonnet 4.6 (Bedrock Runtime). That comparison had a confound: different endpoints with different auth mechanisms, latency profiles, and potential quality-of-service differences. Exp8 controls for this by routing all models through OpenRouter with a single OpenAI SDK client. Pricing also differs (OpenRouter lists $0.06/$0.33 per 1M for Gemma 4 vs. Bedrock Mantle's $0.13/$0.40), which affects cost-per-quality-point analysis.

## Stated Limitations

1. **OpenRouter is a proxy gateway, not a direct provider API.** Latency and reliability may differ from direct provider endpoints.
2. **Gemma 4 26B-A4B is a preview model on OpenRouter.** Availability and pricing may change.
3. **exp3 rubric (C1-C8) is task-specific to the aptu/tree-sitter SCOUT task.** Results measure performance on this task class, not general capability.
4. **n=10 per model is moderately underpowered.** Mann-Whitney U at this n has low power for effect sizes below ~1.0 points.
5. **The exp8 prompt ID is "runner-v1".** Matches exp7 prompt source and version.