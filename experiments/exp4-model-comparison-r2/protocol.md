# Experiment 4: Model Comparison Round 2 -- SCOUT Delegates

**Pre-registered protocol. Do not modify after first run begins.**

## Context

Experiment 3 tested three cheap/free models (Qwen3 Coder, Gemini 3 Flash, Devstral 2512) as
SCOUT delegate replacements for Claude Haiku 4.5. All three failed. The gap was in synthesis
criteria (C6: taint-tracking limitations, C7: non-obvious architectural insight), not retrieval.

The exp3 candidates benchmarked below Haiku on SWE-bench. This round tests models that
benchmark in the same league or higher, to determine whether the synthesis gap is structural
to non-Anthropic models or simply a matter of model capability.

- Exp3 results: [experiments/exp3-model-comparison/analysis.json](../exp3-model-comparison/analysis.json)
- Exp3 protocol: [experiments/exp3-model-comparison/protocol.md](../exp3-model-comparison/protocol.md)
- Issue: [clouatre/dotfiles#250](https://github.com/clouatre/dotfiles/issues/250)

## Task

Same as exp3: [clouatre-labs/aptu#737](https://github.com/clouatre-labs/aptu/issues/737)
(evaluate tree-sitter for AST-based vulnerability detection in the SecurityScanner).

The SCOUT delegate clones the aptu repo, analyzes the codebase, and proposes 2-3 solution
approaches for the tree-sitter integration. Output is a structured JSON handoff file.

## Rubric

Same 8-criterion binary rubric as exp3:
[experiments/exp3-model-comparison/rubric.md](../exp3-model-comparison/rubric.md)

No modifications. Reusing the identical rubric enables direct comparison with exp3 baseline.

## Baseline

Reuse the 5 Claude Haiku 4.5 runs from exp3 (runs 01-05). Scores:

| Run | C1 | C2 | C3 | C4 | C5 | C6 | C7 | C8 | Total |
|-----|----|----|----|----|----|----|----|----|-------|
| 01  | 1  | 1  | 0  | 1  | 0  | 0  | 1  | 1  | 5/8   |
| 02  | 1  | 1  | 0  | 1  | 0  | 0  | 1  | 1  | 5/8   |
| 03  | 1  | 1  | 1  | 1  | 1  | 1  | 1  | 1  | 8/8   |
| 04  | 1  | 1  | 0  | 1  | 0  | 1  | 1  | 1  | 6/8   |
| 05  | 1  | 1  | 0  | 1  | 0  | 0  | 1  | 1  | 5/8   |

Baseline mean: 5.8, median: 5, min: 5, max: 8.

Reuse assumption: the aptu repo state, goose-coder recipe, and SCOUT prompt are unchanged
since exp3. The same commit SHA is used for all runs.

## Candidates

| Model | Provider | API string | Price (in/out per 1M) | SWE-bench Verified |
|-------|----------|------------|----------------------|-------------------|
| MiniMax M2.5 | `openrouter` | `minimax/minimax-m2.5` | $0.15/$0.60 | 80.2% |
| DeepSeek V3.2 | `openrouter` | `deepseek/deepseek-chat` | $0.28/$0.42 | 73.0% |
| Kimi K2.5 | `openrouter` | `moonshotai/kimi-k2.5` | ~$0.30/$1.00 | 76.8% |

All three API strings verified via smoke test on 2026-02-25.

Priority order (run cheapest first):
1. MiniMax M2.5 (highest SWE-bench, cheapest input)
2. DeepSeek V3.2 (best cost-efficiency)
3. Kimi K2.5 (second highest SWE-bench)

## Experimental Design

- **Runs per candidate**: 5
- **Total new runs**: 15 (5 per candidate)
- **Run IDs**: run-21 through run-35 (continuing from exp3's run-20)
- **Execution**: Sequential, 1 delegate at a time (avoids 5-delegate concurrency cap)
- **Temperature**: 0.5 (same as exp3 and goose-coder recipe)
- **Extensions**: developer, context7, brave_search (same as SCOUT in goose-coder recipe)

### Blinding

- Run IDs are sequential (21-35), assigned before execution
- `label-map.json` maps run IDs to models, sealed before scoring begins
- Scorer receives only the run outputs and rubric, not the label-map
- Scorer is a separate Claude Haiku 4.5 instance (same as exp3)

### Assignment

| Run IDs | Model |
|---------|-------|
| 21-25   | MiniMax M2.5 |
| 26-30   | DeepSeek V3.2 |
| 31-35   | Kimi K2.5 |

### Invalid Runs

A run is invalid if:
- The delegate fails to produce any output (tool-use failure, provider error)
- The output is not valid JSON
- The delegate drifts off-task (does not address aptu#737)

Invalid runs are retried up to 2 times (same as exp3). If all retries fail, the run is
recorded as missing. Error rate = missing runs / (5 + retries attempted).

### Stopping Rules

- If a model produces 0 valid runs after all retries: stop that model, record as failed
- If a model's first 3 runs all score below 3/8: stop early, record partial results
- Complete all 5 runs for each model before moving to the next

## Statistical Analysis

Mann-Whitney U test, pairwise (each candidate vs Haiku baseline from exp3).
- Alpha: 0.05
- Direction: two-tailed
- No Bonferroni correction (exploratory; noted as limitation)
- Exact p-values via exhaustive permutation (252 permutations for n=5 vs n=5)
- Effect size: rank-biserial correlation (r_rb)

## Gate Criteria

All four must pass for a candidate to be recommended:

1. **Mean threshold**: Candidate mean >= Haiku mean (5.8) minus 0.5 = **5.3**
2. **Floor**: No individual run scores below **5/8**
3. **Completeness**: No missing handoff outputs (error rate < 20%)
4. **Non-inferiority**: No statistically significant degradation (Mann-Whitney U, p < 0.05)

Verdicts:
- **Pass**: All 4 gates pass
- **Conditional pass**: Gates 1-3 pass, gate 4 marginal (0.05 < p < 0.10)
- **Fail**: Any gate fails

## SCOUT Prompt

The exact SCOUT prompt from the goose-coder recipe (`~/.config/goose/recipes/goose-coder.yaml`,
post-PR [#245](https://github.com/clouatre/dotfiles/pull/245) bookending), with the task
set to "research clouatre-labs/aptu#737". See `runner-prompt.md` for the full parameterized
prompt.

## Data Preservation

All artifacts stored in `experiments/exp4-model-comparison-r2/`:
- `label-map.json` -- sealed before scoring
- `sessions/scout-run-NN.json` -- raw SCOUT delegate outputs
- `scores.json` -- blind scorer results
- `latency-log.jsonl` -- per-run timing
- `analysis.json` -- statistical analysis and gate verdicts

## Limitations

- **Small sample size**: n=5 per group; Mann-Whitney U has low power at this size
- **Single task**: Results may not generalize beyond aptu#737
- **No Bonferroni correction**: Three pairwise comparisons increase family-wise error rate
- **LLM-based scoring**: Scorer is Claude Haiku 4.5, not a human expert
- **Baseline reuse**: Exp3 Haiku runs were scored in a different session; temporal confounds possible
- **Provider variability**: OpenRouter routing may introduce latency or quality variance
- **SWE-bench correlation**: Benchmark scores may not predict SCOUT synthesis performance (exp3 demonstrated this)
