# Experiment 3: Model Comparison for SCOUT Delegates

## Research Question

Can open-weight models (Qwen3 Coder, Gemini 3 Flash, Devstral 2512) replace Claude Haiku 4.5 as SCOUT delegates at 80-160x lower cost?

## Context

This experiment addresses cost reduction objectives outlined in [dotfiles issue #246](https://github.com/hugues-cloudatre/dotfiles/issues/246). The SCOUT (Specification Compliance Outcome Utility Tester) framework uses lightweight delegate models to validate agent decision-making. At ~$0.08 per run, Haiku 4.5 is the cost baseline. This round evaluates whether budget-tier models from OpenRouter and GCP can maintain quality gates.

## Models Tested

| Model | Provider | Approx. cost/run |
|-------|----------|------------------|
| Claude Haiku 4.5 | GCP Vertex AI | ~$0.08 |
| Qwen3 Coder | OpenRouter | ~$0.001 |
| Gemini 3 Flash | GCP Vertex AI | ~$0.01 |
| Devstral 2512 | OpenRouter | ~$0.0005 |

## Results

| Model | n valid | Scores | Mean | Verdict |
|-------|---------|--------|------|---------|
| Claude Haiku 4.5 (baseline) | 5 | 5, 6, 7, 6, 5 | 5.8 | baseline |
| Qwen3 Coder | 0 | n/a | n/a | excluded |
| Gemini 3 Flash | 5 | 4, 4, 3, 5, 5 | 4.2 | fail (all gates) |
| Devstral 2512 | 5 | 4, 3, 3, 3, 2 | 3.0 | fail (all gates) |

## Key Finding

All three candidates fail all four gate criteria. C5 (specific pattern IDs) and C6 (data-flow/taint tracking gap) are the primary discriminators between Haiku and the candidates. Qwen3 Coder's complete exclusion reflects infrastructure limitations (JSON parsing failures after 7 total attempts) rather than semantic capability.

## Session Gap Note

Runs 06-10 are absent from the session directory. Qwen3 Coder failed to produce valid JSON output after 7 total attempts (infrastructure failures and instruction-following breakdown). This exclusion is documented in `protocol.md` under the invalid run policy.

## Documentation

- **Protocol**: [protocol.md](protocol.md) — test setup, run configuration, gate criteria, and invalid-run policy
- **Rubric**: [rubric.md](rubric.md) — 8-criterion evaluation framework used by all scorers
- **Runner Prompt**: [runner-prompt.md](runner-prompt.md) — prompt template for delegate agent execution
- **Scorer Prompt**: [scorer-prompt.md](scorer-prompt.md) — prompt template for rubric-based evaluation
- **Analysis**: [analysis.json](analysis.json) — parsed scores with statistical summaries
- **Scores**: [scores.json](scores.json) — raw run-level scores per criterion
- **Efficiency**: [efficiency.json](efficiency.json) — latency and token usage per run
- **Label Map**: [label-map.json](label-map.json) — run_id to model name mapping (sealed before scoring; revealed after)
- **Latency Log**: [latency-log.jsonl](latency-log.jsonl) — per-line timing data for all runs

## Session Files

15 session records are stored in `sessions/`:
- `scout-run-01.json` through `scout-run-05.json`: Claude Haiku 4.5 baseline
- `scout-run-11.json` through `scout-run-15.json`: Gemini 3 Flash
- `scout-run-16.json` through `scout-run-20.json`: Devstral 2512
- Runs 06-10 (Qwen3 Coder) are absent due to exclusion criteria

## Methodology

See [parent repository README](../../README.md) for full methodology and architectural overview of SCOUT.
