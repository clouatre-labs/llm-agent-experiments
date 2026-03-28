# Experiment 6: Protocol

**Pre-registered:** No. Exploratory, n=5 per role.
**Date:** 2026-03-28
**Orchestrator:** Claude Sonnet 4.6 (goose session, current)

## Research Question

Can `inception/mercury-2` (a diffusion-based LLM) replace `claude-haiku-4-5` in goose-coder
delegate roles (SCOUT, GUARD, BUILD, FIXER, CHECK, REVIEW, QA) without degrading output quality,
and can it succeed as SCOUT where `mistral-small-2603` failed (exp4 mean=5.4/8)?

## Task

Same as exp5: verify the frontmatter patch on three Claude agent files in a dotfiles worktree.

Target files (post-patch state, same worktree commit as exp5):
- `config/claude/agents/goose-coder-scout.md`: three code-analyze MCP tools added
- `config/claude/agents/goose-coder-guard.md`: same three code-analyze MCP tools added
- `config/claude/agents/goose-coder-check.md`: `mcp__aptu__review_pr` removed

Worktree: `/Users/hugues.clouatre/git/dotfiles/.worktrees/exp6-mercury2` (detached HEAD at
`982531392de`, same commit as exp5 post-patch state).

**Same SCOUT caveat as exp5 applies:** The worktree is already patched. SCOUT delegates see the
completed state, not the original gap. SCOUT results measure the model's ability to characterize
the current state and propose changes (from the "before" perspective), not its ability to discover
an unprompted gap. The valid SCOUT benchmark for synthesis from scratch remains exp4.

## Model

| Model | OpenRouter ID | Input (per 1M) | Output (per 1M) | Context |
|-------|--------------|----------------|-----------------|---------|
| Mercury 2 | `inception/mercury-2` | $0.25 | $0.75 | 128K |

## Inference mode

All delegates use default inference mode. No reasoning/thinking budget set.

## Temperature by role

| Role | Temp |
|------|------|
| SCOUT | 0.5 |
| GUARD | 0.1 |
| BUILD | 0.2 |
| FIXER | 0.2 |
| CHECK | 0.1 |
| REVIEW | 0.1 |
| QA | 0.1 |

## Extensions

All delegates: `developer` only.

## Design

n=5 runs per role (35 total Mercury 2 invocations). Runs are sequential per role across
5 complete pipeline passes. Each pipeline pass: SCOUT -> GUARD -> BUILD -> FIXER -> CHECK ->
REVIEW -> QA. Each role receives the same handoff context across all 5 runs (handoff files
are reset to baseline between runs to keep runs independent).

**Handoff baseline (shared across all runs):**
- `01a-research-scout.json`: haiku scout output from exp5 (used as input for GUARD)
- `02-plan.json`: reconstructed from exp5 ground truth (used for BUILD/FIXER/CHECK/REVIEW/QA)
- `03-build.json`: reconstructed from exp5 (used for FIXER/CHECK/REVIEW/QA)
- `04-validation.json`: reconstructed from exp5 (used for FIXER)

SCOUT writes to `scout-mercury-{run}.json`. All other roles write to role-specific output files
with run suffix. This prevents cross-run contamination.

## Scoring

**SCOUT:** 8-criterion binary rubric (C1-C8) adapted for frontmatter task. See `rubric.md`.
**All other roles:** Binary correct/incorrect per exp5 methodology.

## Handoff schemas

Same as exp5. See `runner-prompts.md` for exact prompts per role.

## Cost tracking

OpenRouter usage API queried after each run. Cost per invocation = `cost` field from
`/api/v1/generation?id={generation_id}` or from completion response `usage.cost`.

## Ground truth

- Repo: clouatre-labs/dotfiles (private)
- Commit before: `b120a55f2b872aee431991ab87f8f01ef885c63a`
- Commit after: `982531392de66b4352a3e63cbca5d3f98adb36e0`
- PR: clouatre-labs/dotfiles#350
- Changes:
  - `goose-coder-scout.md`: add `mcp__code-analyze__analyze_directory`,
    `mcp__code-analyze__analyze_file`, `mcp__code-analyze__analyze_symbol` to tools frontmatter
  - `goose-coder-guard.md`: same three tools added
  - `goose-coder-check.md`: remove `mcp__aptu__review_pr` from tools frontmatter
