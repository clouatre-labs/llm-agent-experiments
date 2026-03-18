# Experiment 5: Protocol

**Pre-registered:** No. Exploratory, single run per cell.
**Date:** 2026-03-18
**Orchestrator:** Claude Sonnet 4.6 (goose session 20260318)

## Task

Verify that three Claude agent files in ~/git/dotfiles were correctly patched:

- `config/claude/agents/goose-coder-scout.md`: add 3 code-analyze MCP tools
- `config/claude/agents/goose-coder-guard.md`: add 3 code-analyze MCP tools
- `config/claude/agents/goose-coder-check.md`: remove `mcp__aptu__review_pr`

Worktree: `~/git/dotfiles/.worktrees/20260312_170439` (session 20260312_170439)

The worktree was already patched when delegates ran. SCOUT delegates therefore saw the completed state, not the original gap. This is a task design flaw affecting SCOUT results only (see METHODOLOGY.md).

## Models

| Model | OpenRouter string | Notes |
|-------|-------------------|-------|
| Claude Haiku 4.5 | `anthropic/claude-haiku-4.5` | Baseline; also used in exp3/exp4 |
| Mistral Small 2603 | `mistralai/mistral-small-2603` | Candidate; failed SCOUT in exp4 |
| MiniMax M2.5 | `minimax/minimax-m2.5` | Passed exp4 SCOUT; included for comparison |

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

## Scoring

Binary: Correct / Incorrect.

- **Correct**: output matches ground truth, schema valid, verdict matches expected, no hallucinated paths or tool calls, read-only constraint respected.
- **Incorrect**: wrong verdict, invalid JSON, hallucinated content, or constraint violation.

Ground truth: worktree diff confirms all three files patched as described. No rubric. No blinding. n=1 per cell.

## Handoff schema per role

| Role | Output file | Key fields |
|------|-------------|------------|
| SCOUT | `scout-{model}.json` | `files_found`, `approach`, `conventions_observed` |
| GUARD | `guard-{model}.json` | `scout_findings_accurate`, `recommendation`, `verification` |
| BUILD | `build-{model}.json` | `status`, `files_changed`, `verification`, `deviations_from_plan` |
| FIXER | `fixer-{model}.json` | `fixes_required`, `fixes_applied`, `remaining_issues` |
| CHECK | `check-{model}.json` | `verdict`, `plan_compliance`, `notes`, `blockers` |
| REVIEW | `review-{model}.json` | `verdict`, `spec_alignment`, `findings`, `critical`, `minor` |
| QA | `qa-{model}.json` | `verdict`, `tests_run`, `complexity_findings`, `notes`, `blockers` |
