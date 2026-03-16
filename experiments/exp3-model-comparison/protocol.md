# Experiment 3: Model Comparison for SCOUT Delegates

**Pre-registered protocol -- locked before any delegates are spawned.**

This is the third experiment in the prompt repetition series, designed to evaluate cheaper model alternatives to Claude Haiku 4.5 for SCOUT delegate execution.

---

## Context

Experiments 1 and 2 established that prompt repetition does not improve accuracy on structured engineering tasks when the rubric is well-designed (avoiding ceiling effects). Both experiments used Claude Haiku 4.5 via GCP Vertex AI as the sole delegate model.

Issue: [dotfiles#246](https://github.com/clouatre/dotfiles/issues/246) -- evaluate cheaper models for SCOUT delegates to reduce operational cost while maintaining quality.

Paper: [Leviathan et al. (2025)](https://arxiv.org/abs/2502.07869) -- repeating input prompts improves non-reasoning LLM accuracy.

## Why This Experiment

SCOUT delegates are spawned frequently in the goose-coder recipe (v4.1.0, post-PR #245). Current cost per delegate run:
- Claude Haiku 4.5 via GCP Vertex AI: ~$0.08 per run (input+output tokens)
- Qwen3 Coder via OpenRouter: ~$0.001 per run (free tier)
- Gemini 3 Flash Preview via GCP Vertex AI: ~$0.01 per run
- Devstral 2512 via OpenRouter: ~$0.0005 per run (free tier)

Baseline (Haiku 4.5) is reliable but expensive. Candidates are 80-160x cheaper but unproven on this task class.

---

## Pre-registration (locked before any runs)

All decisions below are final. No post-hoc amendments after the first delegate is spawned.

### Sample size and stopping rule

- Fixed n: 20 valid runs total (5 baseline Haiku, 5 per candidate model x3 = 15 candidate runs)
- Hybrid staged design:
  - **Stage 1 (Baseline validation):** 5 Haiku 4.5 runs to validate rubric and establish baseline distribution
  - **Stage 2 (Candidate evaluation):** 5 runs each for Qwen3 Coder, Gemini 3 Flash, Devstral 2512 (sequential, cheapest-first priority)
- No sequential expansion regardless of delta magnitude
- Stopping rule is fixed; no early stopping

### Invalid run policy

- An invalid run is defined as: delegate completes but writes no output file, or output file is not valid JSON per handoff schema
- Execution failures (infrastructure noise, provider errors) may be re-run, up to 5 total attempts per model (i.e. up to 5 re-runs per model to achieve 5 valid runs)
- All attempts (valid and invalid) must be logged with timestamps and failure reason
- Scoring failures (agent produced output but scored poorly) are NOT re-run -- they are signal, not noise
- If 5 valid runs cannot be achieved in a model group after 5 total attempts, report actual n and note as limitation

### Blinding

- Output files named `scout-run-{01-20}.json` (no model label in filename)
- A separate `label-map.json` file maps run numbers to model assignments, written before any delegates are spawned, sealed (not read by scoring delegate)
- Scoring delegate scores all 20 runs without access to `label-map.json`
- `label-map.json` is revealed only after all 20 scores are written to `scores.json`
- This must be enforced in the orchestration session instructions

### Statistical test

- Mann-Whitney U test, two-tailed, alpha = 0.05
- Applied pairwise: each candidate model vs baseline (Haiku 4.5)
- Three comparisons: Qwen3 vs Haiku, Gemini vs Haiku, Devstral vs Haiku
- With n=5 per group this test is underpowered for small effects -- a non-significant result does not rule out a small true effect; note this as a limitation
- Do not apply parametric tests (t-test) regardless of apparent normality given n=5

### Latency

- Record wall-clock start time and completion time per delegate (ISO 8601)
- Report median latency per model, not mean (resistant to outliers)
- Latency is a secondary metric only -- does not affect the verdict

### Raw data preservation

- All 20 `scout-run-{01-20}.json` files, `label-map.json`, `scores.json`, and the latency log published as a single GitHub gist before closing the issue
- Gist URL recorded in the issue comment alongside results

---

## Experimental Design

### Target

- Issue: [clouatre-labs/aptu#737](https://github.com/clouatre-labs/aptu/issues/737) (open, unimplemented -- zero cheating risk)
- Record repo HEAD SHA at time of first delegate spawn; all delegates use the same SHA
- Extensions: developer, context7, brave_search (identical across all delegates)
- Temperature: 0.5 (consistent with exp2)

### Stage 1: Baseline (Haiku 4.5)

- Model: `claude-haiku-4-5@20251001`
- Provider: `gcp_vertex_ai`
- Temperature: 0.5
- Runs: 5 sequential
- Purpose: Validate rubric and establish baseline score distribution before committing resources to candidate models
- Files named: `scout-run-01.json` through `scout-run-05.json`

### Stage 2: Candidates (Sequential, Cheapest-First)

#### Run 06-10: Qwen3 Coder

- Model: `qwen/qwen3-coder`
- Provider: `openrouter` (free tier)
- Temperature: 0.5
- Smoke-test verification: Confirm OpenRouter API availability and model availability before spawning delegates
- Files named: `scout-run-06.json` through `scout-run-10.json`

#### Run 11-15: Gemini 3 Flash Preview

- Model: `gemini-3-flash-preview`
- Provider: `gcp_vertex_ai`
- Temperature: 0.5
- Smoke-test verification: Confirm GCP Vertex AI availability and model availability before spawning delegates
- Files named: `scout-run-11.json` through `scout-run-15.json`

#### Run 16-20: Devstral 2512

- Model: `mistralai/devstral-2512`
- Provider: `openrouter` (free tier)
- Temperature: 0.5
- Smoke-test verification: Confirm OpenRouter API availability and model availability before spawning delegates
- Files named: `scout-run-16.json` through `scout-run-20.json`

### Delegate Configuration

All delegates receive identical Scout instructions from goose-coder recipe (post-PR #245, commit d4ac9e8). Each delegate independently clones clouatre-labs/aptu into a unique temp dir using the same repo HEAD SHA.

---

## Blinding Procedure

1. **Pre-spawn:** Orchestrator writes `label-map.json` mapping run numbers 01-20 to model assignments:
   ```json
   {
     "01": "haiku-4.5",
     "02": "haiku-4.5",
     ...
     "06": "qwen3-coder",
     ...
     "16": "devstral-2512",
     ...
   }
   ```

2. **Spawn:** Orchestrator spawns delegates sequentially (Stage 1, then Stage 2 per priority order). Each delegate writes output to `scout-run-{NN}.json` with no model label.

3. **Scoring:** Scoring delegate receives only the 20 run files and the rubric. No access to `label-map.json`, no metadata about which model produced which run.

4. **Reveal:** After `scores.json` is written, orchestrator reveals `label-map.json` and computes group statistics.

---

## Statistical Test

### Pairwise Comparisons

For each candidate model C, compute Mann-Whitney U test:
- H0: Haiku 4.5 and model C have equal score distributions
- H1: Distributions differ (two-tailed)
- Alpha = 0.05
- Test statistic: U (Mann-Whitney)
- Report: U, p-value, effect size (rank-biserial correlation)

### Multiple Comparisons

Three independent tests (Qwen3 vs Haiku, Gemini vs Haiku, Devstral vs Haiku). No Bonferroni correction applied (exploratory stage); note this as a limitation.

---

## Gate Criteria (Pre-registered from dotfiles#246)

A candidate model passes the gate if ALL of the following hold:

1. **Mean score >= Haiku baseline mean - 0.5** (on 8-point rubric)
   - Rationale: Allow up to 0.5-point degradation from baseline while maintaining acceptable quality
   - Calculation: mean(candidate scores) >= mean(haiku scores) - 0.5

2. **No runs with score < 5/8**
   - Rationale: Avoid models that produce occasional low-quality outputs
   - Calculation: min(candidate scores) >= 5

3. **No runs that fail to produce the handoff JSON file**
   - Rationale: Reliability is non-negotiable; infrastructure failures are acceptable (re-run), but model failures are not
   - Calculation: all 5 valid runs must have output files

4. **Error rate (provider failures, tool-use failures) < 20%**
   - Rationale: Provider instability or model tool-use failures make the model unsuitable for production
   - Calculation: (failed attempts / total attempts) < 0.20

### Interpretation

- **Pass:** Candidate meets all 4 gates AND Mann-Whitney U p >= 0.05 (no significant degradation)
- **Conditional pass:** Candidate meets all 4 gates BUT Mann-Whitney U p < 0.05 (significant degradation detected, but within acceptable bounds per gate 1)
- **Fail:** Candidate fails any gate

---

## Execution Notes

- Record the aptu HEAD SHA before spawning delegate 1; use that SHA for all delegates
- Each Scout delegate independently clones aptu -- no shared worktree state
- Orchestrator writes `label-map.json` before spawning any delegates; does not share it with scoring delegate
- Scoring delegate receives only the 20 run files and the rubric
- After `scores.json` is written, orchestrator reveals `label-map.json` and computes group statistics and Mann-Whitney U tests
- Preserve all outputs as a gist immediately after scoring, before /tmp is cleared
- Document data preservation: `sessions/` directory holds structured handoff JSONs (what gets scored), `raw/` directory holds full JSONL conversation logs

---

## Limitations (pre-acknowledged)

- n=5 per model is underpowered; Mann-Whitney U at this n has low power for effect sizes below ~1.5 points
- Scoring delegate is an LLM judge -- inter-rater reliability is not measured
- Single issue (aptu#737), single temperature (0.5), single task class (code synthesis) -- results do not generalize beyond this configuration
- brave_search access means Scouts can find documentation online; this is a constant across models, not a confound, but limits ecological validity for air-gapped environments
- Multiple comparisons (3 pairwise tests) without Bonferroni correction increases family-wise error rate; note this as exploratory
- Provider availability and pricing may change; smoke-test verification required before execution
- Ceiling effect risk persists if rubric criteria are too easy; mitigated by C7 and C8 requiring synthesis beyond issue text

---

## References

- Leviathan, Y. et al., "Prompt Repetition Improves Non-Reasoning LLMs" (2025) -- https://arxiv.org/abs/2502.07869
- Experiment 1: [exp1-fastmcp-refactor](https://github.com/clouatre-labs/prompt-repetition-experiments/blob/main/experiments/exp1-fastmcp-refactor/protocol.md)
- Experiment 2: [exp2-treesitter-synthesis](https://github.com/clouatre-labs/prompt-repetition-experiments/blob/main/experiments/exp2-treesitter-synthesis/protocol.md)
- Target issue: https://github.com/clouatre-labs/aptu/issues/737
- Cost evaluation: https://github.com/clouatre/dotfiles/issues/246
- goose-coder recipe: commit d4ac9e8 (post-PR #245 bookending); recipe managed at ~/.config/goose/recipes/goose-coder.yaml via dotfiles hardlinks
- SecurityScanner context: [aptu#735](https://github.com/clouatre-labs/aptu/issues/735), [PR #736](https://github.com/clouatre-labs/aptu/pull/736)
- tree-sitter Rust: https://tree-sitter.github.io/tree-sitter/using-parsers/queries
