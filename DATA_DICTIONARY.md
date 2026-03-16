# Data Dictionary

This document describes the schema and format of all data files in the `data/` directory.

## Directory Structure

```
experiments/
  exp3-model-comparison/
    analysis.json
    scores.json
    efficiency.json
    label-map.json
    latency-log.jsonl
    sessions/
      scout-run-01.json
      scout-run-02.json
      ...
      scout-run-20.json
  exp4-model-comparison-r2/
    analysis.json
    scores.json
    efficiency.json
    label-map.json
    latency-log.jsonl
    sessions/
      scout-run-21.json
      scout-run-22.json
      ...
      scout-run-35.json
```

## File Schemas

### analysis.json

Top-level experiment metadata and per-candidate results summary.

```json
{
  "experiment": "exp3",
  "conducted_date": "2026-03-01",
  "orchestrator": {
    "model": "Claude Sonnet 4.6",
    "provider": "gcp_vertex_ai",
    "temperature": 0.3
  },
  "baseline": {
    "model": "Claude Haiku 4.5",
    "runs": [1, 2, 3, 4, 5],
    "scores": [5, 5, 8, 6, 5],
    "mean": 5.8,
    "sd": 1.1,
    "min": 5,
    "max": 8
  },
  "candidates": [
    {
      "model": "Qwen3 Coder",
      "n_attempted": 7,
      "n_valid": 0,
      "runs": [],
      "scores": [],
      "mean": null,
      "error_rate": 1.0,
      "gates": {
        "mean_threshold_gt_5_3": false,
        "floor_ge_5": false,
        "completeness_error_rate_le_0_2": false,
        "non_inferiority_p_gt_0_05": false
      },
      "verdict": "excluded"
    },
    {
      "model": "Gemini 3 Flash",
      "n_attempted": 5,
      "n_valid": 5,
      "runs": [11, 12, 13, 14, 15],
      "scores": [4, 4, 3, 5, 5],
      "mean": 4.2,
      "sd": 0.8,
      "min": 3,
      "max": 5,
      "error_rate": 0.0,
      "gates": {
        "mean_threshold_gt_5_3": false,
        "floor_ge_5": false,
        "completeness_error_rate_le_0_2": true,
        "non_inferiority_p_gt_0_05": true
      },
      "mann_whitney_u": {
        "u_statistic": 18,
        "p_value": 0.137,
        "rank_biserial_r": -0.2,
        "n_baseline": 5,
        "n_candidate": 5
      },
      "verdict": "fail"
    }
  ],
  "summary": "All cheap models failed. Exp3 concluded with recommendation for higher-tier models in exp4."
}
```

### scores.json

Per-run detailed criterion scores and metadata.

```json
[
  {
    "run_id": "001",
    "experiment": "exp3",
    "criteria": {
      "C1": 1,
      "C2": 1,
      "C3": 1,
      "C4": 1,
      "C5": 0,
      "C6": 1,
      "C7": 1,
      "C8": 0
    },
    "total": 6,
    "scorer_id": "blind-scorer-001",
    "scorer_timestamp": "2026-03-01T14:23:45Z",
    "notes": "Clean decomposition; minor edge case miss."
  }
]
```

**Field descriptions:**

- `run_id` (string): Unique identifier (zero-padded, e.g., "001")
- `experiment` (string): "exp3" or "exp4"
- `criteria` (object): C1-C8 each 0 (fail) or 1 (pass)
- `total` (integer): Sum of C1-C8 (0-8 range)
- `scorer_id` (string): Scorer subagent identifier (blind, no model info)
- `scorer_timestamp` (string): ISO 8601 timestamp when scoring occurred
- `notes` (string): Optional free-form scorer annotation

### efficiency.json

Pricing and token data per model and run.

```json
{
  "experiment": "exp3",
  "pricing_date": "2026-03-01",
  "models": [
    {
      "model": "Claude Haiku 4.5",
      "pricing": {
        "input_token_usd": 0.000080,
        "output_token_usd": 0.0004
      },
      "runs": [
        {
          "run_id": "001",
          "input_tokens": 2500,
          "output_tokens": 1200,
          "total_cost_usd": 0.68
        }
      ]
    }
  ]
}
```

**Field descriptions:**

- `pricing_date` (string): Date pricing was recorded (may differ from run date if collected later)
- `input_token_usd`, `output_token_usd` (number): USD cost per token (rates frozen at experiment time)
- `input_tokens`, `output_tokens` (integer): Tokens consumed in run (from goose session handoff)
- `total_cost_usd` (number): `(input_tokens * input_rate) + (output_tokens * output_rate)`

#### model_summaries (new in exp3/exp4)

Top-level key added after `runs`. Contains pre-computed aggregate metrics per model.

```json
"composite_metric_formula": "eff_cost_per_qp = cost_per_run / (mean_score * reliability); reliability = n_valid / sum_of_attempt_numbers_per_run; cost_per_run uses accumulated_input_tokens and accumulated_output_tokens",
"model_summaries": {
  "<model>": {
    "n_valid": 5,
    "n_total_attempts": 6,
    "reliability": 0.8333,
    "mean_score": 7.0,
    "cost_per_run_usd": 0.2206,
    "eff_cost_per_qp_usd": 0.0378,
    "mean_wall_time_minutes": 11.64,
    "cost_token_basis": "accumulated"
  }
}
```

**Field descriptions:**

- `n_valid` (integer): Number of runs that produced valid output
- `n_total_attempts` (integer): Sum of `attempt` values across all protocol slots for this model (reliability denominator); not the number of protocol slots
- `reliability` (number): `n_valid / n_total_attempts` (0.0-1.0)
- `mean_score` (number|null): Mean total score from scores.json; null if no valid runs
- `cost_per_run_usd` (number|null): Mean cost per valid run using accumulated tokens; null if no valid runs
- `eff_cost_per_qp_usd` (number|null): `cost_per_run_usd / (mean_score * reliability)`; null if mean_score is null or reliability is 0
- `mean_wall_time_minutes` (number|null): Mean wall-clock duration of valid runs from efficiency.json; null if no valid runs
- `cost_token_basis` (string): Always `"accumulated"` -- costs use `accumulated_input_tokens`/`accumulated_output_tokens`, not session-level tokens

### label-map.json

Blind scoring label mapping. Written and sealed BEFORE any SCOUT spawning. Revealed AFTER scoring.

```json
{
  "001": "Claude Haiku 4.5",
  "002": "Claude Haiku 4.5",
  "003": "Claude Haiku 4.5",
  "004": "Claude Haiku 4.5",
  "005": "Claude Haiku 4.5",
  "006": "Qwen3 Coder",
  "007": "Qwen3 Coder",
  "008": "Qwen3 Coder",
  "009": "Qwen3 Coder",
  "010": "Qwen3 Coder",
  "011": "Gemini 3 Flash",
  "012": "Gemini 3 Flash",
  "013": "Gemini 3 Flash",
  "014": "Gemini 3 Flash",
  "015": "Gemini 3 Flash",
  "016": "Devstral 2512",
  "017": "Devstral 2512",
  "018": "Devstral 2512",
  "019": "Devstral 2512",
  "020": "Devstral 2512"
}
```

**Semantics:**
- Scorer receives only `run_id` values (numeric strings) in score data.
- Scorer does NOT see this file during scoring.
- After all scoring is complete, this file is published so the run->model mapping is transparent.
- Enables verification that scoring was truly blind.

### latency-log.jsonl

One JSON object per line. Captures start and end timestamps for each run (for latency analysis).

```json
{"run_id": "001", "start_timestamp": "2026-03-01T14:00:00Z", "end_timestamp": "2026-03-01T14:23:45Z"}
{"run_id": "002", "start_timestamp": "2026-03-01T14:25:00Z", "end_timestamp": "2026-03-01T14:47:30Z"}
```

**Field descriptions:**

- `run_id` (string): Corresponds to label-map.json key
- `start_timestamp` (string): ISO 8601 when SCOUT delegate was spawned
- `end_timestamp` (string): ISO 8601 when SCOUT delegate completed (or failed)

**Computation:** Duration = `(end_timestamp - start_timestamp).total_seconds()`

### sessions/scout-run-NN.json

Goose SCOUT delegate handoff file for run N. Files are located in:
- `experiments/exp3-model-comparison/sessions/scout-run-01.json` through `scout-run-20.json` (runs 01-05, 11-15, 16-20 present; 06-10 absent)
- `experiments/exp4-model-comparison-r2/sessions/scout-run-21.json` through `scout-run-35.json` (runs 21-29, 31-35 present; 27, 30 absent)

Total: 28 files (15 from exp3 + 13 from exp4)

Follows goose-coder recipe v4.2.1 handoff format.

```json
{
  "session_id": "20260301_exp3_run_001",
  "lens": "Refactor a given TypeScript utility module for improved maintainability. ...",
  "relevant_files": [
    {
      "path": "src/utils.ts",
      "excerpt": "function mapValues(obj, fn) { ... }"
    }
  ],
  "conventions": {
    "naming": "camelCase for functions and variables",
    "error_handling": "Use try-catch with descriptive messages",
    "testing": "Jest framework; unit tests per feature"
  },
  "patterns": [
    "functional transforms",
    "immutable updates",
    "lazy evaluation"
  ],
  "related_issues": [
    {
      "id": "gh-391",
      "title": "Refactor utilities for clarity",
      "link": "https://github.com/..."
    }
  ],
  "constraints": [
    "No external dependencies beyond lodash",
    "Maintain backward compatibility",
    "TypeScript strict mode"
  ],
  "test_coverage": {
    "required_behaviors": 4,
    "test_count": 7,
    "coverage_percent": 94
  },
  "library_findings": {
    "lodash": "v4.17.21",
    "typescript": "5.3.3"
  },
  "approaches": [
    {
      "label": "approach-1",
      "description": "Compose using functional pipeline",
      "rejected": false,
      "rationale": "Chosen: clear data flow"
    }
  ],
  "recommendation": {
    "summary": "Refactoring complete. All tests pass. Code review ready.",
    "confidence": 0.9,
    "next_steps": "Deploy to staging; gather integration test results"
  }
}
```

**Key fields:**

- `session_id` (string): Unique goose session identifier
- `lens` (string): The task prompt / problem statement
- `relevant_files` (array): Code snippets or file references used in context
- `conventions` (object): Style guide and practices inferred from the codebase
- `patterns` (array): Architectural and design patterns identified
- `related_issues` (array): GitHub issues or PRs referenced during reasoning
- `constraints` (array): Requirements, limitations, or non-functional goals
- `test_coverage` (object): Testing metrics (behaviors, test count, coverage %)
- `library_findings` (object): External dependencies and versions used
- `approaches` (array): Candidate solutions evaluated; included rejected approaches with rationale
- `recommendation` (object): Final synthesis recommendation and confidence level

## Data Quality Notes

- **Missing runs:** Exp3 runs 06-10 (Qwen3), exp4 runs 27, 30 (DeepSeek) are missing from label-map and latency-log. These runs failed to produce valid outputs.
- **Null values:** In analysis.json, candidates with zero valid runs have `mean: null` and empty `scores` array.
- **Timestamps:** All timestamps in ISO 8601 format with Z (UTC) suffix.
- **Identifiers:** run_id is zero-padded to 3 digits (e.g., "001", "025").

## Access and Licensing

All files in this directory are released under Apache License 2.0. See ../LICENSE for full text.

For questions or corrections, please open an issue on the GitHub repository: https://github.com/clouatre-labs/llm-agent-experiments
