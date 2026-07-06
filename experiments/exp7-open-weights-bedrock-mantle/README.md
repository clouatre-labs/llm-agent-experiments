# Experiment 7: Open-Weights Models on Bedrock Mantle

## Research Question

Can Gemma 4 26B-A4B on Bedrock Mantle replace Claude Haiku 4.5 / Sonnet 4.6 as SCOUT delegates at 7-23x lower cost per quality-point?

## Context

This experiment evaluates Gemma 4 26B-A4B (Apache 2.0) via the Bedrock Mantle preview endpoint against Claude Haiku 4.5 and Claude Sonnet 4.6 via Bedrock Runtime. The cost motivation is driven by the 10-50x price gap between open-weight and proprietary models at scale. Bedrock Mantle provides an OpenAI-compatible endpoint with SigV4 auth, enabling drop-in client compatibility. Apache 2.0 licensing unlocks unrestricted deployment, fine-tuning, and distribution -- a compliance advantage over proprietary models.

## Models Tested

| Model | Provider | Endpoint | Price (input/output per 1M) | Approx. cost/run |
|-------|----------|----------|----------------------------|-------------------|
| Gemma 4 26B-A4B | Bedrock Mantle | bedrock-mantle | $0.13 / $0.40 | ~$0.00023 |
| Claude Haiku 4.5 | Bedrock Runtime | bedrock-runtime | $1.00 / $5.00 | ~$0.00091 |
| Claude Sonnet 4.6 | Bedrock Runtime | bedrock-runtime | $3.00 / $15.00 | ~$0.00347 |

## Results

| Model | n valid | Mean | P50 latency | Error rate | Verdict |
|-------|---------|------|-------------|------------|---------|
| Gemma 4 26B-A4B | 5 | 5.0 | 4320ms | 0.0 | fail (mean gate: 5.0 < 5.3) |
| Claude Haiku 4.5 | 5 | 5.8 | 2100ms | 0.0 | baseline |
| Claude Sonnet 4.6 | 5 | 6.6 | 3810ms | 0.0 | pass |

## Key Finding

Gemma 4 achieves comparable C3/C4/C8 criterion scores to Haiku 4.5 but falls short of the 5.3 gate threshold primarily on C5 (pattern ID specificity) and C6 (taint-tracking gap articulation). At $0.13/$0.40 per 1M tokens, it delivers the lowest cost per run; the quality-gate failure suggests the exp3 SCOUT task is too aptu-specific for this model to match proprietary baseline performance without fine-tuning on this domain.

## Documentation

- **Protocol**: [protocol.md](protocol.md) -- test setup, run configuration, gate criteria, and invalid-run policy
- **Rubric**: [rubric.md](../exp3-model-comparison/rubric.md) -- 8-criterion evaluation framework (shared with exp3)
- **Runner Prompt**: [runner-prompt.md](../exp3-model-comparison/runner-prompt.md) -- prompt template for delegate agent execution (shared with exp3)
- **Scorer Prompt**: [scorer-prompt.md](../exp3-model-comparison/scorer-prompt.md) -- prompt template for rubric-based evaluation (shared with exp3)
- **Scores**: [results/scores.jsonl](results/scores.jsonl) -- raw run-level scores per criterion
- **Latency**: [results/latency.jsonl](results/latency.jsonl) -- per-model latency statistics
- **Cost Summary**: [results/cost_summary.json](results/cost_summary.json) -- pricing and projected monthly costs
- **Audit Record**: [audit/sample_audit_record.json](audit/sample_audit_record.json) -- sample Cloudflare AI Gateway trace export
- **Label Map**: [label-map.json](label-map.json) -- run_id to model name mapping (sealed before scoring; revealed after)

## Session Files

15 session records are stored in `sessions/`:
- `run-41.json` through `run-45.json`: Gemma 4 26B-A4B
- `run-46.json` through `run-50.json`: Claude Haiku 4.5
- `run-51.json` through `run-55.json`: Claude Sonnet 4.6

## Methodology

See [parent repository README](../../README.md) for full methodology and architectural overview of SCOUT.
