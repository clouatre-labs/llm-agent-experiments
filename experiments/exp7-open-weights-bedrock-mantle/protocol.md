# Experiment 7: Open-Weights Models on Bedrock Mantle -- Protocol

## Pre-registration

Pre-registration date: 2026-06-25

## Hypothesis

Gemma 4 26B-A4B on Bedrock Mantle achieves rubric mean >= 5.3 (exp3 gate threshold) at 7-23x lower cost per quality-point than Claude Haiku 4.5 / Sonnet 4.6.

## Models Tested

| Model key | Model ID | Endpoint | Input price / 1M | Output price / 1M |
|-----------|----------|----------|-------------------|--------------------|
| gemma4 | google.gemma-4-26b-a4b | Bedrock Mantle (us-east-1) | $0.13 | $0.40 |
| haiku45 | anthropic.claude-haiku-4-5-20251001-v1:0 | Bedrock Runtime (us-east-1) | $1.00 | $5.00 |
| sonnet46 | anthropic.claude-sonnet-4-6 | Bedrock Runtime (us-east-1) | $3.00 | $15.00 |

## Prompt Set Source

`experiments/exp3-model-comparison/runner-prompt.md` -- verbatim, no modifications.

## Scoring Rubric Source

`experiments/exp3-model-comparison/rubric.md` -- verbatim, no modifications.

Criterion summary (8 criteria, each scored 0 or 1):

- **C1**: Identifies and verifies a specific source file relevant to the issue
- **C2**: References a specific code pattern within the verified file
- **C3**: Identifies at least one relevant test file
- **C4**: Identifies a related issue or PR that provides implementation context
- **C5**: References specific pattern IDs from issue descriptions (e.g., "T001", "D001")
- **C6**: Makes an explicit statement about AST-only limitations for taint tracking
- **C7**: Identifies a non-obvious architectural implication requiring code synthesis
- **C8**: Produces valid JSON output per handoff schema

## Run Configuration

n = 5 per model, runs 41-55 (continuing exp4 numbering).

| Runs | Model | Label |
|------|-------|-------|
| 41-45 | google.gemma-4-26b-a4b | gemma4 |
| 46-50 | anthropic.claude-haiku-4-5-20251001-v1:0 | haiku45 |
| 51-55 | anthropic.claude-sonnet-4-6 | sonnet46 |

## Blind Scoring Procedure

1. Scorer receives run files, rubric, and no other metadata
2. `label-map.json` is sealed before spawning any delegates
3. Scoring produces `results/scores.jsonl` without model_key values
4. After `scores.jsonl` is complete, label-map is revealed and model_key appended

## Gate Criteria

Same as exp3:

- **Mean >= 5.3**: Mean rubric score across valid runs >= 5.3
- **Min score >= 5**: No single run scores below 5 (lower bound of baseline range)
- **Error rate <= 0.2**: At most 1 invalid run out of 5
- **Mann-Whitney U p >= 0.05**: No statistically significant difference from Haiku 4.5 baseline

Verdict: **pass** if all four criteria met; **fail** if any criterion not met.

## Invalid Run Policy

- Up to 5 total attempts per run
- Execution failures (infrastructure, API errors): re-run
- Scoring failures (invalid JSON, missing output): signal -- do not retry
- If a model exceeds 5 failed attempts, it is excluded from comparison

## Infrastructure

- **Bedrock Mantle endpoint**: `https://bedrock-mantle.us-east-1.api.aws/openai/v1/` (SigV4 auth)
- **Bedrock Runtime**: boto3 `bedrock-runtime` Converse API (IAM auth)
- **Cloudflare AI Gateway**: All requests proxy through `https://gateway.ai.cloudflare.com/v1/{ACCOUNT_ID}/{GATEWAY_SLUG}/`
- **Scoring**: Local heuristic scorer (no LLM calls during scoring)

## Stated Limitations

1. **Bedrock Mantle is a preview endpoint.** GA timeline not public. Pricing and availability may change at GA.
2. **Gemma 4 cannot be used as a Bedrock Knowledge Base generator.** `RetrieveAndGenerate` dispatches via `bedrock-runtime`; Gemma 4 is `bedrock-mantle`-only.
3. **Cross-region inference not yet confirmed for Mantle endpoint.** All runs use us-east-1.
4. **exp3 rubric (C1-C8) is task-specific to the aptu/tree-sitter SCOUT task.** Results measure performance on this task class, not general capability.
5. **n=5 per model is underpowered.** Mann-Whitney U at this n has low power for effect sizes below ~1.5 points.