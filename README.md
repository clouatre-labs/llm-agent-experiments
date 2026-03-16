# llm-agent-experiments

[![License: Apache 2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://github.com/clouatre-labs/llm-agent-experiments/blob/main/LICENSE)
[![GitHub stars](https://img.shields.io/github/stars/clouatre-labs/llm-agent-experiments.svg?style=social)](https://github.com/clouatre-labs/llm-agent-experiments)

## Summary

**Finding:** Exp3: all cheap models fail synthesis criteria. Exp4: MiniMax M2.5 and Kimi K2.5 pass; DeepSeek V3.2 fails with a 40% run error rate.

## The Question

Can open-weight models replace Claude Haiku 4.5 as SCOUT delegates in the goose-coder recipe at lower cost without degrading research quality?

## Experiment Setup

```
Goose + coder recipe v4.2.1 | Orchestrator: Claude Sonnet 4.6 | 
Scorer: blind subagent | Rubric: 8-criterion binary (0-8)
```

## Scoring Rubric

| Criterion | Description |
|-----------|-------------|
| C1 | Correct problem decomposition |
| C2 | Appropriate tool selection |
| C3 | Valid syntax across all artifacts |
| C4 | Handles edge cases |
| C5 | Error handling present |
| C6 | No redundant or circular logic |
| C7 | Architecture matches specification |
| C8 | Code usability and clarity |

## Results -- Experiment 3

All candidate models failed one or more gates against baseline (Claude Haiku 4.5).

| Model | n | Scores | Mean | Verdict |
|-------|---|--------|------|---------|
| Claude Haiku 4.5 (baseline) | 5 | 5,5,8,6,5 | 5.8 | baseline |
| Qwen3 Coder | 0 | n/a | n/a | excluded (0/7 valid runs) |
| Gemini 3 Flash | 5 | 4,4,3,5,5 | 4.2 | fail |
| Devstral 2512 | 5 | 4,3,3,3,2 | 3.0 | fail |

**Verdict:** All cheap candidates excluded or failed synthesis gates.

## Results -- Experiment 4

Two models cleared all gates; one failed with high error rate.

| Model | n | Mean | Error rate | p (vs Haiku) | Verdict |
|-------|---|------|-------------|--------------|---------|
| Claude Haiku 4.5 (baseline) | 5 | 5.8 | 0.0 | -- | baseline |
| MiniMax M2.5 | 5 | 6.0 | 0.0 | 0.492 | pass |
| DeepSeek V3.2 | 3 | 1.0 | 0.4 | 0.018 | fail |
| Kimi K2.5 | 5 | 7.0 | 0.0 | 0.183 | pass |

**Verdict:** MiniMax and Kimi qualify as cost-effective delegates; DeepSeek unsuitable.

## Cross-Experiment Summary

| Experiment | Phase | Baseline Mean | Candidates Tested | Passed | Failed/Excluded | Key Finding |
|------------|-------|----------------|------------------|--------|-----------------|-------------|
| Exp 3 | Discovery | 5.8 | 3 | 0 | 3 | Cheap tier models too weak |
| Exp 4 | Validation | 5.8 | 3 | 2 | 1 | Mid-tier models viable; DeepSeek unstable |

## Repository Structure

```
llm-agent-experiments/
  README.md                          This file
  METHODOLOGY.md                     Shared methodology and statistical protocol
  DATA_DICTIONARY.md                 Schema definitions for all data files
  CITATION.cff                       Dataset citation metadata
  LICENSE                            Apache License 2.0
  recipe/
    goose-coder.yaml                 Goose recipe v4.2.1 (from dotfiles d4ac9e8)
  data/                              Data files (managed by shard B)
    exp3/
      analysis.json                  Experiment 3 metadata and per-candidate scores
      scores.json                    Per-run criterion scores (C1-C8)
      efficiency.json                Pricing and token data
      label-map.json                 Blind scoring: run_id -> model mapping
      latency-log.jsonl              Per-run timestamps (ISO 8601)
    exp4/
      analysis.json
      scores.json
      efficiency.json
      label-map.json
      latency-log.jsonl
    sessions/                        SCOUT and Guard handoff files
      scout-run-001.json             ... through scout-run-013.json
      ...
```

## Data Files

### analysis.json
Experiment metadata, baseline summary, per-candidate verdict structure with scores, gates (pass/fail), statistical test results, and overall recommendation.

### scores.json
Per-run array of criterion scores (C1-C8, each 0-1 binary), total (0-8), scorer annotations, and timestamp.

### efficiency.json
Per-model pricing (USD per MCT hour), token counts, and interpolated cost per run.

### label-map.json
JSON object mapping `run_id` (string) to model name. Written before any SCOUT spawning; scorer receives numeric labels only.

### latency-log.jsonl
One JSON per line: `{run_id, start_timestamp, end_timestamp}` in ISO 8601 format.

### sessions/scout-run-N.json
SCOUT handoff schema (goose-coder v4.2.1): `session_id`, `lens`, `relevant_files`, `conventions`, `patterns`, `related_issues`, `constraints`, `test_coverage`, `library_findings`, `approaches`, `recommendation`.

## Session Gaps

**Exp 3 runs 06-10:** Qwen3 Coder produced zero valid outputs after 7 infrastructure and instruction-following attempts. Marked as excluded (0/7 valid runs).

**Exp 4 runs 27 and 30:** DeepSeek V3.2 failed to produce parseable JSON on those two attempts (infrastructure timeouts). Counted as errors in error_rate calculation (2 / 5 = 0.4).

## Raw Log Gap

Raw JSONL conversation logs (goose session records) are not included in this repository. The reference repository (prompt-repetition-experiments) includes them for exp1 and exp2; they were not captured in the pipeline for exp3 and exp4. This is documented as a limitation (see Limitations below).

## Reproducibility

All experiments used the Goose agent framework with the public coder recipe (v4.2.1, committed at d4ac9e8 in the dotfiles repo). The recipe and orchestrator model are deterministic at temperature 0.3. To reproduce:

1. Install Goose (version pinned in Software Versions section below)
2. Load the `recipe/goose-coder.yaml` recipe into your local Goose config
3. Set orchestrator to Claude Sonnet 4.6 via GCP Vertex AI, temperature 0.3
4. Follow the protocol in `METHODOLOGY.md` for delegate spawning and blind scoring
5. Use the label-map.json to reveal model identities only after scoring is complete

## Software Versions

| Component | Version | Notes |
|-----------|---------|-------|
| Goose | [pinned version] | Agent orchestrator |
| goose-coder recipe | 4.2.1 | At git d4ac9e8, dotfiles repo |
| Orchestrator model | Claude Sonnet 4.6 | GCP Vertex AI, temp 0.3 |
| SCOUT delegate models | See exp3/exp4 protocol | Variable per experiment |

## Limitations

1. **Underpowered study design:** n=5 per model is insufficient for strong statistical power. Results are indicative, not definitive.
2. **No raw logs:** Conversation records (goose session JSONL) are absent; only scored outputs and handoff metadata are available.
3. **Qwen3 Coder exclusion:** Zero valid runs after 7 attempts; excluded from analysis. Cause unclear (infrastructure vs. model capability).
4. **DeepSeek V3.2 partial sample:** n=3 valid (2 of 5 runs failed); increases variance in comparison. p-value should be interpreted conservatively.
5. **Single orchestrator:** All runs used Claude Sonnet 4.6; generalization to other orchestrators unknown.

## Ethics Statement

This repository documents a research experiment conducted using commercial and open-weight large language models. The study was pre-registered (label-map.json sealed before scoring) to mitigate confirmation bias. Model names were withheld from the scorer until completion. All statistical tests were two-tailed with alpha=0.05. Findings are presented with limitations explicitly stated. No human participants were involved; no personal data was collected.

## Data Availability

This repository contains the complete dataset, methodology, and analysis code. All files are public under the Apache License 2.0. Supplementary materials (goose recipe, METHODOLOGY.md) are included. The source orchestrator (Claude Sonnet 4.6, GCP Vertex AI) and SCOUT delegate models are noted for reference; raw model outputs are in the sessions/ directory.

## Funding and Conflict of Interest

This research was funded internally. The researchers have no competing financial interests. Claude Haiku 4.5 (the baseline) is a commercial model offered by Anthropic; the authors work with Anthropic technology in the goose framework context. Open-weight model comparisons are not endorsements, only technical evaluations.

## Citation

If you use this dataset or methodology, please cite:

```bibtex
@dataset{clouatre2026llmagent,
  title={LLM Agent Experiments: Model Comparison for SCOUT Delegates},
  author={Clouatre, Hugues},
  year={2026},
  month={March},
  day={16},
  howpublished={\url{https://github.com/clouatre-labs/llm-agent-experiments}},
  note={Pre-registered model comparison experiments (exp3, exp4) in the goose-coder recipe. Blind scoring with Mann-Whitney U statistical test.}
}
```

See CITATION.cff for additional metadata.

## License

This repository is licensed under the Apache License 2.0. See LICENSE for full text.
