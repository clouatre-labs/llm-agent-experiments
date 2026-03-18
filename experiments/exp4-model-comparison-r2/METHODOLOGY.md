# Experiment 4: Methodology

## Experimental Design

Four candidates tested against Claude Haiku 4.5 baseline (reused from exp3). 8 rounds of 5 runs each (40 total). Blind scoring protocol applied uniformly across all candidates.

## Blinding Procedure

- label-map.json sealed before first run
- Scorer receives run IDs only (no model names or identifying information)
- Scores recorded in scores.json with per-criterion justifications
- Label map revealed only after all scoring complete
- Mistral Small 2603 (runs 36-40) scored in a separate session using identical blinding protocol

## Rubric

8-criterion binary rubric (0 or 1 per criterion, max total = 8):

- C1: Identifies correct primary file
- C2: Explains current pattern and limitation
- C3: Acknowledges tree-sitter is absent from Cargo.toml (not a current dependency)
- C4: Proposes 3 approaches with codebase evidence
- C5: Names specific pattern IDs requiring multi-line detection
- C6: Acknowledges AST-only limitation for data-flow/taint tracking
- C7: Non-obvious architectural synthesis beyond issue text
- C8: Valid JSON output matching schema

Note: C3 criterion was refined from exp3 (now requires explicit acknowledgment of tree-sitter absence, not just version citation).

## Scoring Procedure

- Scorer: mistral-large (blind to run identity)
- Scores recorded in scores.json with per-criterion justification notes
- Mistral Small 2603 blind scores with justifications in scores-mistral.json
- All criterion scores are binary (0 or 1)

## Gate Criteria

All four gates must pass for a PASS verdict:

| Gate | Criterion | Threshold |
|------|-----------|-----------|
| G1 | Mean score > baseline floor | > 5.3 (haiku mean - 0.5) |
| G2 | Floor score | >= 5 (no run below 5) |
| G3 | Valid runs | >= 5 |
| G4 | Non-inferiority (Mann-Whitney) | p >= 0.05 (no significant degradation) |

## Statistical Test

Mann-Whitney U test, two-tailed, exact permutation (exhaustive). Alpha = 0.05. Effect size: rank-biserial correlation r_rb.

Note: No Bonferroni correction applied (exploratory analysis across 4 pairwise comparisons; limitation noted in analysis).

## Efficiency Metric

eff_cost_per_qp = cost_per_run / (mean_score * reliability)

Where reliability = n_valid / n_total_attempts.

Costs based on OpenRouter pricing (as of experiment run date). Token counts accumulated from session metadata in sessions.db.

## Candidate-Specific Notes

### DeepSeek V3.2

Runs 27 and 30 produced no parseable JSON output. Both attempts logged in latency-log.jsonl. Reliability = 3/8 = 0.33 (6 of 8 attempts successful).

### Mistral Small 2603

8 total attempts across 5 run slots. Reliability = 5/8 = 0.625. Passes mean gate (5.4 > 5.3) but fails gate_2 (min score 4 < threshold 5). Criterion pass rates: C1=1.0, C2=1.0, C3=0.0, C4=1.0, C5=0.0, C6=0.6, C7=0.6, C8=1.0. Mann-Whitney p=1.0 (no significant difference vs baseline).

### Kimi K2.5

6 total attempts; run 33 required retry. Reliability = 5/6 = 0.83.

## Mistral Latency Reconstruction Note

Runs 36-37 wall times are derived from sessions.db created_at timestamps rather than directly measured in latency-log.jsonl. Run 36 attempt 1 produced truncated output (4 tokens), requiring a retry. Run 37 attempt 2 completed successfully (381 tokens output). Wall time values in efficiency.json reflect individual session duration, not cumulative retry time across attempts.
