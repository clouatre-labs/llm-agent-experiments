# Experiment 6: Scoring Rubric

**Pre-registered rubric -- locked before any delegates are spawned.**

Binary scoring only: 1 = criterion met, 0 = criterion not met. No half-credit.

Total score: 0-8 points. Applied to SCOUT role only.

All other roles (GUARD, BUILD, FIXER, CHECK, REVIEW, QA) are scored binary correct/incorrect
per exp5 methodology.

---

## SCOUT Criteria

### C1: All three target files identified

**Criterion:** Delegate names all three target files in `files_found`.

**Ground truth:** `config/claude/agents/goose-coder-scout.md`,
`config/claude/agents/goose-coder-guard.md`, `config/claude/agents/goose-coder-check.md`.
Partial paths acceptable (e.g., `goose-coder-scout.md`) if unambiguous.

**Scoring:** 1 if all three files appear in `files_found`. 0 if any file is missing, wrong, or
not found by the delegate.

**Rationale:** Baseline check -- confirms the delegate read the right files.

---

### C2: Correct proposed_tools for scout.md (three code-analyze tools)

**Criterion:** `files_found` entry for `goose-coder-scout.md` lists all three code-analyze tools
in `proposed_tools`:
- `mcp__code-analyze__analyze_directory`
- `mcp__code-analyze__analyze_file`
- `mcp__code-analyze__analyze_symbol`

**Scoring:** 1 if all three appear in proposed_tools for scout.md. 0 if any is missing or wrong.

**Rationale:** Core correctness check for the primary add-tools change.

---

### C3: Correct proposed_tools for guard.md (same three tools)

**Criterion:** `files_found` entry for `goose-coder-guard.md` lists the same three code-analyze
tools in `proposed_tools`.

**Scoring:** 1 if all three appear in proposed_tools for guard.md. 0 if any is missing or wrong.

**Rationale:** Verifies the delegate did not conflate scout and guard changes.

---

### C4: Removal of mcp__aptu__review_pr from check.md identified

**Criterion:** `files_found` entry for `goose-coder-check.md` shows `mcp__aptu__review_pr` in
`current_tools` but absent from `proposed_tools`, OR the delegate explicitly notes its removal
in `approach` or a notes field.

**Ground truth:** `mcp__aptu__review_pr` is present before the patch, absent after.

**Scoring:** 1 if delegate identifies this removal. 0 if delegate misses it, misidentifies the
tool, or incorrectly includes it in proposed_tools.

**Rationale:** The subtraction change is harder to detect than additions; tests careful reading.

---

### C5: No hallucinated tools

**Criterion:** No tool names appear in any `proposed_tools` array that do not exist in the
post-patch ground truth for that file. No invented tool names (e.g., tools with wrong prefixes
or names not in the actual frontmatter).

**Ground truth:** Post-patch tools for each file are verified from the worktree.

**Scoring:** 1 if no hallucinated tools. 0 if any proposed_tools entry contains a tool not
present in the ground truth for that file.

**Rationale:** Anti-hallucination gate. A model that reads carefully will not invent tool names.

---

### C6: current_tools vs proposed_tools distinction correct

**Criterion:** For at least two of the three files, the delegate correctly populates both
`current_tools` and `proposed_tools` with distinct values that reflect the actual change
(add or remove). Both fields must be present and non-empty.

**Ground truth:** Before patch (current): scout.md and guard.md lack the three code-analyze
tools; check.md has `mcp__aptu__review_pr`. After patch (proposed): additions/removal applied.

**Caveat:** Since the worktree is already patched, a delegate reading the current state will see
the post-patch tools as `current_tools`. It may then produce `proposed_tools == current_tools`
(no change) rather than inferring the pre-patch state. If the delegate reads the post-patch state
and reports it accurately (current = proposed = post-patch), this criterion is scored 0 unless
the delegate explicitly reasons about the change direction.

**Scoring:** 1 if the delegate correctly represents the change direction (additions for scout/guard,
removal for check) in the current/proposed distinction. 0 if proposed_tools equals current_tools
for all three files with no explanation, or if the distinction is absent.

**Rationale:** Measures whether the model understands change direction, not just current state.

---

### C7: conventions_observed contains relevant tool naming conventions

**Criterion:** `conventions_observed` includes at least one observation about tool naming
conventions (e.g., JSON array format, `mcp__` prefix convention, tool naming patterns).

**Scoring:** 1 if conventions_observed contains a relevant tool naming or frontmatter convention.
0 if empty or contains only generic observations unrelated to the task.

**Rationale:** Confirms the delegate extracted task-relevant conventions, not just boilerplate.

---

### C8: Valid JSON output per handoff schema

**Criterion:** Delegate produces a valid JSON file matching the SCOUT handoff schema. Must be
parseable by `jq`. Must contain all required fields:
`session_id`, `files_found`, `approach`, `risks`, `conventions_observed`.
Each entry in `files_found` must have `path`, `current_tools`, `proposed_tools`.

**Scoring:** 1 if output is valid JSON with all required fields. 0 if file is missing, invalid
JSON, or any required field is absent.

**Rationale:** Non-negotiable for downstream processing. Mercury 2 uses diffusion decoding;
structured output stability is a key capability signal.

---

## Scoring Procedure

1. **Scorer receives:** 5 run files (`scout-mercury-1.json` through `scout-mercury-5.json`),
   this rubric, and no other metadata.
2. **Scorer does not receive:** model names, run order, or comparison scores.
3. **For each run:** Score C1-C8 independently (1 or 0).
4. **Total score:** Sum of C1-C8 (0-8).
5. **Output:** Write `scores.json` with run ID, individual criterion scores, total, justification.

## Other roles

GUARD, BUILD, FIXER, CHECK, REVIEW, QA: scored correct (1) or incorrect (0) per exp5 rubric
(valid JSON, correct verdict, no hallucinated paths, constraint respected). No C1-C8 applied.
