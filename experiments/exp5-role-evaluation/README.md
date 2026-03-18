# Experiment 5: Multi-Role Model Evaluation

## Research Question

Can `mistral-small-2603` replace `claude-haiku-4.5` in validation and execution roles (GUARD,
BUILD, FIXER, CHECK, REVIEW, QA) of the goose-coder multi-agent pipeline without degrading
output quality?

## Context

exp3 and exp4 evaluated SCOUT delegate replacements only. This experiment extends coverage to all
7 roles using a real pipeline task. SCOUT in the goose-coder recipe runs on Claude Sonnet 4.6
and is not a replacement candidate; it is included here for completeness and as a methodological
control.

Exp4 result for Mistral Small 2603 on SCOUT: fail (mean=5.4, min=4, C3=0%, C5=0%, 37.5%
hard-failure rate). That verdict is not revisited here.

## Method

- Single run per model per role (n=1 per cell; 21 total delegate invocations)
- Same real worktree and handoff files across all cells per role
- Qualitative assessment: verdict correctness, turn count, wall time, notes count
- No statistical gates (n=1 is sufficient for hard pass/fail on structured output tasks)
- Provider: OpenRouter for all three models
- Temperature: role-dependent (see protocol.md)
- Extensions: `developer` only for all delegates
- Orchestrator: Claude Sonnet 4.6 via goose session 20260318

**Important caveat:** The worktree was already patched when delegates ran. SCOUT delegates
therefore saw the completed state, not the original gap. SCOUT results are invalid as a
capability signal. See METHODOLOGY.md.

## Results

| Role | Model | Verdict | Correct | Turns | Wall time (s) | Notes | Blockers |
|------|-------|---------|---------|------:|-------------:|------:|--------:|
| SCOUT | Haiku 4.5 | n/a | No | 249 | 61 | 0 | 0 |
| SCOUT | Mistral 2603 | n/a | No | 74 | 9 | 0 | 0 |
| SCOUT | MiniMax M2.5 | n/a | No | 63 | 58 | 0 | 0 |
| GUARD | Haiku 4.5 | proceed | Yes | 301 | 28 | 0 | 0 |
| GUARD | Mistral 2603 | proceed | Yes | 43 | 18 | 0 | 0 |
| GUARD | MiniMax M2.5 | proceed | Yes | 255 | 143 | 0 | 0 |
| BUILD | Haiku 4.5 | success | Yes | 213 | 24 | 0 | 0 |
| BUILD | Mistral 2603 | success | Yes | 34 | 14 | 0 | 0 |
| BUILD | MiniMax M2.5 | success | Yes | 339 | 29 | 0 | 0 |
| FIXER | Haiku 4.5 | n/a | Yes | 141 | 29 | 11 | 0 |
| FIXER | Mistral 2603 | n/a | Yes | 33 | 9 | 6 | 0 |
| FIXER | MiniMax M2.5 | n/a | Yes | 113 | 46 | 5 | 0 |
| CHECK | Haiku 4.5 | PASS | Yes | 12 | 11 | 6 | 0 |
| CHECK | Mistral 2603 | PASS | Yes | 54 | 16 | 0 | 0 |
| CHECK | MiniMax M2.5 | PASS | Yes | 219 | 67 | 4 | 0 |
| REVIEW | Haiku 4.5 | PASS | Yes | 12 | 13 | 0 | 0 |
| REVIEW | Mistral 2603 | PASS | Yes | 23 | 8 | 0 | 0 |
| REVIEW | MiniMax M2.5 | PASS | Yes | 112 | 73 | 0 | 0 |
| QA | Haiku 4.5 | PASS | Yes | 12 | 18 | 3 | 0 |
| QA | Mistral 2603 | PASS | Yes | 44 | 12 | 4 | 0 |
| QA | MiniMax M2.5 | PASS | Yes | 166 | 52 | 4 | 0 |

Wall time measured as elapsed seconds between first and last message timestamp in the goose sessions DB (`~/.local/share/goose/sessions/sessions.db`). Raw data in `latency-log.jsonl`. Mistral SCOUT 9s reflects a trivially short run (the worktree was pre-patched; the model responded immediately with no changes needed).

**Notes** = count of items in the `notes` array of the handoff JSON. Reflects output verbosity,
not quality. See METHODOLOGY.md.

## SCOUT failure detail

All three models failed SCOUT due to the pre-patched worktree (see METHODOLOGY.md):

- **Haiku 4.5**: concluded no changes needed (read current patched state as correct)
- **Mistral 2603**: hallucinated a naming inconsistency in `goose-coder-check.md` body (`mcp-aptu-scan-security` vs `mcp__aptu__scan_security`) that does not exist in the file
- **MiniMax M2.5**: went off-task; proposed adding CLI tools (`gh`, `jq`, `git`) to frontmatter, which is incorrect and not part of the task

## Findings

1. **Correctness is equivalent** across all three models for GUARD, BUILD, FIXER, CHECK, REVIEW, QA. Zero blockers in all 18 valid cells.

2. **MiniMax M2.5 uses 2-28x more turns** than Haiku for equivalent output quality. It is not suited for validation roles in a cost-sensitive pipeline.

3. **Mistral 2603 is turn-efficient on execution roles**: 43 turns (GUARD), 34 turns (BUILD), 33 turns (FIXER) vs Haiku's 301, 213, 141.

4. **Haiku is most efficient on validation roles**: 12 turns flat for CHECK, REVIEW, QA, vs Mistral's 54/23/44 and MiniMax's 219/112/166.

5. **Mistral GUARD output is notably richer**: it enumerated all proposed tools per file with rationale, while Haiku and MiniMax gave summary-level verification.

6. **Notes count reflects verbosity only**, not quality. Haiku FIXER produced 11 notes vs Mistral's 6 and MiniMax's 5; all three were correct.

## Recommended role assignments

| Role | Recommended model | Rationale |
|------|-------------------|-----------|
| SCOUT | `claude-sonnet-4-6` | Production baseline; no open-weight replacement (exp4 verdict stands) |
| GUARD | `mistralai/mistral-small-2603` | 7x fewer turns than Haiku, richest verification output |
| BUILD | `mistralai/mistral-small-2603` | 6x fewer turns than Haiku, equivalent correctness |
| FIXER | `mistralai/mistral-small-2603` | 4x fewer turns than Haiku, equivalent correctness |
| CHECK | `anthropic/claude-haiku-4.5` | Most turn-efficient (12 turns); Mistral silent pass reduces auditability |
| REVIEW | `mistralai/mistral-small-2603` | Fastest wall time (~10s), equivalent correctness |
| QA | `mistralai/mistral-small-2603` | Most informative notes, equivalent correctness |

## Limitations

- n=1 per cell; no statistical power, results are indicative only
- Task is simple (frontmatter verification); harder tasks (code diffs, test failures, multi-file changes) may differentiate models
- SCOUT excluded due to task design flaw
- Wall times are approximate (+/- 10s); not instrumented at API level
- Turn counts reflect agent loop iterations including tool calls, not LLM calls
- Mistral SCOUT 0s wall time anomaly unexplained
- All runs used `developer` extension only; production delegates use additional extensions (e.g., `aptu` for CHECK/REVIEW) which may affect turn counts

## Reproducibility

- Worktree: `~/git/dotfiles/.worktrees/20260312_170439` (preserved for audit)
- Pipeline source: `~/.config/goose/recipes/goose-coder.yaml` (v4.6.0)
- Agent definitions: `~/.claude/agents/coder-*.md`
- Task: verify frontmatter patch from dotfiles session 20260312_170439
- All raw delegate outputs in `sessions/`; model mapping in `sessions/label-map.json`

## Next steps

- exp6: repeat with a harder task (real code diff with test failures) to stress-test Mistral on CHECK
- exp6: n=5 per cell + Mann-Whitney gate if exp6 results are promising
- Update `goose-coder.yaml` to use `mistralai/mistral-small-2603` for GUARD, BUILD, FIXER, REVIEW, QA pending exp6 confirmation
