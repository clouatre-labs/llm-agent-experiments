# Experiment 9: OpenRouter Model Evaluation (Round 2)

Replicates Experiment 8 on a new task (aptu#1205: multi-forge support) with three fixes: corrected runner prompt, broadened C4 heuristic, and proper C8 JSON validation.

## Research Question

When routing all three models through a single OpenRouter endpoint, does the ranking (Gemma 4 vs Haiku 4.5 vs Sonnet 4.6) replicate across tasks, or are the exp8 results task-specific?

## Models

| Model | API | Run IDs | Price/M input | Price/M output |
|-------|-----|---------|---------------|----------------|
| Google Gemma 4 26B-A4B | OpenRouter | run-86 to run-95 | $0.06 | $0.33 |
| Claude Haiku 4.5 | OpenRouter | run-96 to run-105 | $1.00 | $5.00 |
| Claude Sonnet 4.6 | OpenRouter | run-106 to run-115 | $3.00 | $15.00 |

## Run Configuration

| Config | Value |
|--------|-------|
| Total runs | 30 (10 per model) |
| Pilot runs | run-86 (gemma4), run-96 (haiku45), run-106 (sonnet46) |
| Endpoint | OpenRouter (https://openrouter.ai/api/v1) |
| Task | SCOUT research on clouatre-labs/aptu#1205 |
| Max tokens | 4096 |
| Temperature | 0.5 |

## Outputs

| File | Description |
|------|-------------|
| `sessions/run-NN.json` | Raw model output (response text, tokens, latency, cost) |
| `results/latency.jsonl` | Per-run latency log |
| `results/cost_summary.json` | Aggregated cost per model |
| `results/scores.jsonl` | Blind C1-C8 scores per run |
| `label-map.json` | Run ID to model key mapping (sealed before runs) |
| `runner-prompt.md` | Task prompt sent to each model |
| `rubric.md` | Scoring rubric (C1-C8) |
| `scorer-prompt.md` | Instructions for the blind scorer |

## Gate Criteria

Same as exp8:

- Mean score >= 5.3/8 (67%)
- Minimum score >= 5/8
- Error rate <= 0.2 (2/10 failures)
- Mann-Whitney U test p >= 0.05 between consecutive models

## Amendments vs exp8

Three fixes applied:

1. **Corrected runner prompt.** exp8 used the raw bash-escaped SCOUT_INSTRUCTIONS variable (\\n literals) from exp3's runner-prompt.md. exp9 properly unescapes into real newlines via the `runner-prompt.md` extraction logic.
2. **Broadened C4 heuristic.** Old C4 checked for `#735`, `#736`, `#737`, `issue`, `pr`. New C4 checks for `#1205` OR (multi-forge domain keywords AND structural code keywords).
3. **Proper C8 JSON validation.** Old C8 returned 1 unconditionally. New C8 parses the response text as JSON and validates all 11 required handoff schema fields.

## Usage

```bash
# Pilot run (one per model)
uv run python run_inference.py --pilot

# Full run
uv run python run_inference.py

# Score
uv run python score.py

# Score with model labels revealed
uv run python score.py --reveal
```