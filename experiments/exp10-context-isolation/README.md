# Experiment 10: Context Isolation for GSM8K Evaluation

Tests whether context contamination (irrelevant history in the prompt window) degrades LLM math reasoning performance on GSM8K. Uses a three-condition design with length-matched context windows.

## Research Question

Does the presence of irrelevant conversational history in the context window degrade LLM performance on GSM8K math reasoning tasks, and is any degradation attributable to context contamination specifically (vs. total context length)?

## Conditions

| Condition | Description |
|-----------|-------------|
| Scoped | Only the current task prompt. No history. Length-padded to match Contaminated. |
| Full-History | Complete planner transcript verbatim prepended to the task. Length-padded to match Contaminated. |
| Contaminated | Task injected at a controlled middle position among distractor turns. No padding needed (reference length). |

## Models

| Model | API | Model ID | Price/M input | Price/M output |
|-------|-----|----------|---------------|----------------|
| Google Gemma 4 26B-A4B | OpenRouter | google/gemma-4-26b-it | $0.06 | $0.33 |
| Claude Haiku 4.5 | Bedrock | anthropic.claude-haiku-4-5-20251001-v1:0 | $1.00 | $5.00 |

## Run Configuration

| Config | Value |
|--------|-------|
| Total tasks | 300 (fixed seed 42 from GSM8K test split) |
| Runs per condition | 300 (each task run once per condition) |
| Total runs | 900 (300 tasks x 3 conditions) |
| Max tokens | 4096 |
| Temperature | 0.5 |
| Dataset | openai/gsm8k (test split) |

## Key Methodological Controls

### Length-Matching Approximation

Scoped and Full-History conditions are padded with filler text to match the token count of the Contaminated condition. The filler text is lorem-style prose with no numeric patterns (to avoid false-positive GSM8K answer extraction). Token counts use a whitespace-split approximation, which is not equivalent to tiktoken or Claude's internal subword tokenizer. This is documented as an approximation, not exact equivalence.

### Tokenizer Asymmetry

The whitespace-split token estimate is approximate for Claude models. Claude uses a subword tokenizer (similar to tiktoken) that may produce different counts than whitespace splitting. This asymmetry is acceptable for length-matching purposes because the padding is applied uniformly across conditions and the goal is approximate length equivalence, not exact token parity.

### JSON Extraction Asymmetry

OpenRouter calls use `response_format=json_object` (API-level structured output) when available. Bedrock calls use prompt-only JSON extraction (no API-level structured output). This asymmetry is acceptable for the 50-run secondary check but is documented as a methodological limitation.

## Outputs

| File | Description |
|------|-------------|
| `sessions/<condition>/run-NNN.json` | Per-run model output and metadata |
| `results/latency_log.jsonl` | Per-run latency log |
| `results/cost_summary.json` | Aggregated cost per condition |
| `results/scores.jsonl` | Per-run accuracy scores |
| `results/mcnemar_summary.json` | McNemar paired test results |
| `label-map.json` | Run ID to model key mapping (sealed before runs) |
| `runner-prompt.md` | Task prompt sent to each model |
| `rubric.md` | Scoring rubric |
| `scorer-prompt.md` | Instructions for the blind scorer |

## Usage

```bash
# Dry run (print context lengths without API calls)
uv run python run_inference.py --dry-run

# Pilot run (5 tasks)
uv run python run_inference.py --pilot

# Full run (300 tasks, one condition)
uv run python run_inference.py --condition scoped --model gemma4
uv run python run_inference.py --condition full-history --model gemma4
uv run python run_inference.py --condition contaminated --model gemma4

# Score
uv run python score.py

# Score with model labels revealed
uv run python score.py --reveal
```

## Gate Criteria

- Mean accuracy >= 0.70 across all conditions
- McNemar test p < 0.025 (Bonferroni-corrected) for scoped vs contaminated
- Error rate <= 0.05 per condition
