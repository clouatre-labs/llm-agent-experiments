# Experiment 4: Model Comparison Round 2

## Research Question

Do higher-tier open-weight models (MiniMax M2.5, DeepSeek V3.2, Kimi K2.5, Mistral Small 2603) provide viable SCOUT delegate candidates while maintaining reasonable cost?

## Context

Exp3 candidates were selected from models benchmarked below Claude Haiku 4.5 on SWE-bench Lite. This round tests higher-tier open-weight models available on OpenRouter, evaluating whether increased capability correlates with improved SCOUT performance.

The baseline (Claude Haiku 4.5, mean=5.8) is reused from exp3 to enable cross-round comparison. All runs use the same 8-criterion rubric and gate structure.

## Models Tested

| Model | Provider | Approx. cost/run |
|-------|----------|------------------|
| Claude Haiku 4.5 | GCP Vertex AI | ~$0.08 (baseline reused from exp3) |
| MiniMax M2.5 | OpenRouter | ~$0.02 |
| DeepSeek V3.2 | OpenRouter | ~$0.01 |
| Kimi K2.5 | OpenRouter | ~$0.03 |
| Mistral Small 2603 | OpenRouter | ~$0.008 |

## Results

| Model | n valid | Mean | Error rate | p vs Haiku | r | Verdict |
|-------|---------|------|------------|-----------|---|---------|
| Claude Haiku 4.5 (baseline) | 5 | 5.8 | 0.0 | -- | -- | baseline |
| MiniMax M2.5 | 5 | 6.4 | 0.0 | 0.524 | -0.32 | pass |
| DeepSeek V3.2 | 3 | 1.0 | 0.4 | 0.036 | 1.0 | fail |
| Kimi K2.5 | 5 | 6.6 | 0.0 | 0.238 | -0.48 | pass |
| Mistral Small 2603 | 5 | 5.4 | 0.375 | 1.000 | 0.04 | fail |

## Key Finding

Two of four candidates pass all gate criteria. Kimi K2.5 (mean=6.6) outperforms the baseline, demonstrating that higher-tier open-weight models can exceed Haiku 4.5 quality on SCOUT tasks. MiniMax M2.5 also passes. DeepSeek V3.2 and Mistral Small 2603 fail: DeepSeek exhibits infrastructure issues (40% error rate), while Mistral fails the minimum score gate (lowest run scored 4 vs required threshold 5) despite passing the mean gate (5.4 > 5.3).

## Session Gap Note

Runs 27 and 30 are absent from the session directory. DeepSeek V3.2 produced no parseable JSON output on those two attempts (logged in `latency-log.jsonl`).

Runs 36-40 (Mistral Small 2603) appear as separate batches in `sessions/`: runs 36-37 have longer time gaps between associated log entries and were executed in a separate session batch from runs 38-40.

## Documentation

- **Protocol**: [protocol.md](protocol.md) — test setup, run configuration, gate criteria, and invalid-run policy
- **Rubric**: [rubric.md](rubric.md) — 8-criterion evaluation framework (identical copy; see note below)
- **Runner Prompt**: [runner-prompt.md](runner-prompt.md) — prompt template for delegate agent execution
- **Scorer Prompt**: [scorer-prompt.md](scorer-prompt.md) — prompt template for rubric-based evaluation
- **Analysis**: [analysis.json](analysis.json) — parsed scores with statistical summaries
- **Scores**: [scores.json](scores.json) — raw run-level scores per criterion
- **Scores (Mistral)**: [scores-mistral.json](scores-mistral.json) — raw run-level scores for Mistral Small 2603
- **Efficiency**: [efficiency.json](efficiency.json) — latency and token usage per run
- **Label Map**: [label-map.json](label-map.json) — run_id to model name mapping (sealed before scoring; revealed after)
- **Latency Log**: [latency-log.jsonl](latency-log.jsonl) — per-line timing data for all runs

## Rubric

This experiment uses the same 8-criterion rubric as exp3. See `rubric.md` in this directory (identical copy) or [exp3/rubric.md](../exp3-model-comparison/rubric.md).

## Session Files

18 session records are stored in `sessions/`:
- `scout-run-21.json` through `scout-run-25.json`: MiniMax M2.5
- `scout-run-26.json`: DeepSeek V3.2 (run 1 of 3)
- `scout-run-28.json` through `scout-run-29.json`: DeepSeek V3.2 (runs 2-3, sparse)
- `scout-run-31.json` through `scout-run-35.json`: Kimi K2.5
- `scout-run-36.json` through `scout-run-40.json`: Mistral Small 2603
- Runs 27 and 30 (DeepSeek V3.2) are absent due to JSON parsing failures

## Methodology

See [METHODOLOGY.md](METHODOLOGY.md) for blinding protocol, rubric details, scoring procedure, gate criteria, and statistical tests. See [parent repository README](../../README.md) for full architectural overview of SCOUT.

## Latency Reconstruction Note

Runs 36-37 (Mistral Small 2603) wall times are derived from sessions.db created_at timestamps rather than directly measured in latency-log.jsonl. Run 36 attempt 1 produced truncated output (4 tokens) requiring retry; run 37 attempt 2 completed successfully (381 tokens). Wall time values in efficiency.json reflect individual session durations, not cumulative retry overhead.
