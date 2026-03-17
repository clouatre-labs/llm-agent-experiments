> This rubric is identical to [experiments/exp3-model-comparison/rubric.md](../exp3-model-comparison/rubric.md). Copied here for standalone reproducibility.

# Experiment 3: Scoring Rubric

**Pre-registered rubric -- locked before any delegates are spawned.**

Binary scoring only: 1 = criterion met, 0 = criterion not met. No half-credit.

Total score: 0-8 points.

---

## Criteria

### C1: SecurityScanner implementation file identified

**Criterion:** Delegate identifies the primary file containing the SecurityScanner implementation.

**Ground truth:** `crates/aptu-core/src/scanner.rs` or equivalent verified against actual repo structure at the HEAD SHA used for all delegates. Must not be assumed from issue text alone.

**Scoring:** 1 if delegate explicitly names the correct file and verifies it exists in the codebase. 0 if file is not named, is incorrect, or is assumed without verification.

**Rationale:** Establishes that delegate read the actual codebase, not just the issue text. Baseline for all subsequent analysis.

---

### C2: Line-by-line regex limitation understood

**Criterion:** Delegate explicitly references the single-line constraint of regex-based pattern matching and cites supporting evidence.

**Ground truth:** References to [aptu#735](https://github.com/clouatre-labs/aptu/issues/735) or [PR #736](https://github.com/clouatre-labs/aptu/pull/736) or quotes from test fixtures demonstrating the limitation. Must show understanding that regex patterns cannot match across line boundaries without explicit multi-line flags.

**Scoring:** 1 if delegate cites at least one of the above sources or quotes test code demonstrating the limitation. 0 if limitation is mentioned generically without evidence.

**Rationale:** Ensures delegate understands the core problem being solved. Prevents generic summaries that miss the architectural constraint.

---

### C3: Cargo.toml absence explicitly noted

**Criterion:** Delegate explicitly states that tree-sitter is not present in the aptu Cargo.toml and must be added as a new dependency.

**Ground truth:** tree-sitter is absent from the aptu Cargo.toml as of the experiment date.

**Scoring:** 1 if delegate explicitly states that tree-sitter is not present in Cargo.toml or the dependency list and must be added. 0 if absence is not stated explicitly, if it is only inferred from the issue title, or if the delegate only cites a version number without noting absence.

**Rationale:** A model that read Cargo.toml will note the absence directly. This criterion can only be satisfied by a model that inspected the file, making it a reliable proxy for tool use and anti-hallucination.

---

### C4: Hybrid vs. full-migration tradeoff articulated with codebase evidence

**Criterion:** Delegate proposes a hybrid approach (keeping existing regex for simple patterns, adding tree-sitter for complex ones) and supports the tradeoff with specific codebase evidence.

**Ground truth:** Delegate must name specific patterns (e.g., "sql-injection-concat", "hardcoded-secrets") or specific files (e.g., "patterns.rs", "detection.rs") as evidence. Generic prose about "keeping simple patterns" without naming them does not count.

**Scoring:** 1 if delegate names at least 2 specific patterns or files and explains why they would benefit from tree-sitter. 0 if tradeoff is discussed generically or without codebase references.

**Rationale:** Prevents hand-waving. Requires delegate to read actual pattern definitions and make concrete architectural decisions.

---

### C5: At least 2 specific patterns identified as requiring multi-line detection

**Criterion:** Delegate identifies specific vulnerability patterns that require multi-line detection and explains why regex alone is insufficient.

**Ground truth:** Must name actual pattern IDs or descriptions from the aptu codebase (e.g., "sql-injection-concat", "command-injection-format", "hardcoded-secrets"). Must explain why the pattern requires data-flow or syntactic context across multiple lines.

**Scoring:** 1 if delegate names at least 2 specific patterns from the codebase and explains the multi-line requirement. 0 if patterns are generic examples or not named.

**Rationale:** Ensures delegate synthesized from source code, not just issue text. Prevents ceiling effect by requiring concrete pattern analysis.

---

### C6: Data-flow/taint tracking gap noted as unsolved by tree-sitter alone

**Criterion:** Delegate explicitly acknowledges that tree-sitter AST traversal does not solve data-flow or taint analysis problems.

**Ground truth:** Explicit statement that AST parsing is necessary but not sufficient for detecting vulnerabilities that require tracking data flow across function boundaries or through variable assignments. Examples: "tree-sitter can identify function calls but cannot track whether the argument comes from user input" or "AST alone cannot determine if a string is sanitized before use".

**Scoring:** 1 if delegate makes an explicit statement about the limitations of AST-only approaches for taint tracking. 0 if this gap is not mentioned or is dismissed as solvable by tree-sitter alone.

**Rationale:** Demonstrates architectural maturity. Prevents naive solutions that assume AST parsing is a complete answer.

---

### C7: Non-obvious architectural implication requiring code synthesis

**Criterion:** Delegate identifies a non-obvious architectural implication that requires reading and synthesizing code, not just summarizing the issue.

**Ground truth:** Examples of acceptable responses:
- Recognizing that binary size impact depends on which language grammars are included (tree-sitter-rust ~2-3MB, tree-sitter-python ~4-5MB, etc.) and proposing a staged rollout to minimize bloat
- Identifying that the existing pattern JSON schema must be extended with a new field (e.g., `ts_query`) and proposing backward-compatible migration
- Noting that the SecurityScanner's dispatch logic must route patterns to the appropriate engine (regex vs. tree-sitter) and proposing a concrete implementation strategy
- Recognizing that tree-sitter queries must be compiled at startup or build time, not runtime, and proposing where to cache them

**Scoring:** 1 if delegate identifies at least one non-obvious implication that requires synthesis beyond the issue text. 0 if all points are direct summaries of the issue or generic advice.

**Rationale:** Prevents ceiling effect. Requires delegate to think beyond the issue description and propose concrete implementation details.

---

### C8: Valid JSON output per handoff schema

**Criterion:** Delegate produces a valid JSON file matching the handoff schema specified in the orchestration instructions.

**Ground truth:** Output file must be valid JSON (parseable by `jq`), must contain required fields per the SCOUT handoff schema: `session_id`, `lens`, `relevant_files`, `conventions`, `patterns`, `related_issues`, `constraints`, `test_coverage`, `library_findings`, `approaches`, `recommendation`. Must not contain syntax errors.

**Scoring:** 1 if output file is valid JSON and contains all required fields per the handoff schema. 0 if file is missing, is not valid JSON, or is missing required fields.

**Rationale:** Ensures delegate followed instructions and produced machine-readable output. Non-negotiable for downstream processing.

---

## Scoring Procedure

1. **Scorer receives:** 20 run files (`scout-run-01.json` through `scout-run-20.json`), this rubric, and no other metadata
2. **Scorer does not receive:** `label-map.json`, model names, run order, or any information that would reveal which model produced which run
3. **For each run:** Score each criterion independently (1 or 0)
4. **Total score:** Sum of all 8 criteria (0-8)
5. **Output:** Write `scores.json` with run ID, individual criterion scores, total score, and brief justification for each criterion
6. **After scoring:** Orchestrator reveals `label-map.json` and computes group statistics

---

## Justification Format

For each criterion, scorer provides a brief justification (1-2 sentences) explaining why the criterion was met or not met. Examples:

- **C1 met:** "Delegate explicitly names `crates/aptu-core/src/scanner.rs` and verifies it exists in the repo."
- **C1 not met:** "Delegate mentions 'the scanner file' but does not name it or verify its location."
- **C7 met:** "Delegate recognizes that pattern JSON schema must be extended with `ts_query` field and proposes backward-compatible migration strategy."
- **C7 not met:** "Delegate summarizes the issue but does not propose any non-obvious architectural implications."

---

## Comparability with Experiment 2

Criteria C1-C6 are kept from exp2 rubric to maintain comparability across experiments. C7 and C8 are new:

- **C7 (exp2):** Binary size / grammar crate count estimated with specifics
- **C7 (exp3):** Non-obvious architectural implication requiring code synthesis (broader, avoids ceiling effect)
- **C8 (exp3):** Valid JSON output per handoff schema (new, ensures machine-readable output)

This change addresses the ceiling effect observed in exp2 (all runs scored 7/7) by raising the bar for C7 and adding a structural requirement (C8).

---

## References

- Target issue: https://github.com/clouatre-labs/aptu/issues/737
- SecurityScanner context: [aptu#735](https://github.com/clouatre-labs/aptu/issues/735), [PR #736](https://github.com/clouatre-labs/aptu/pull/736)
- Experiment 2 rubric: [exp2-treesitter-synthesis/scores.json](https://github.com/clouatre-labs/prompt-repetition-experiments/blob/main/experiments/exp2-treesitter-synthesis/scores.json)
- tree-sitter Rust: https://tree-sitter.github.io/tree-sitter/using-parsers/queries
