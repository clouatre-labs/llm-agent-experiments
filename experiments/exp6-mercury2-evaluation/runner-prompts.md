# Exp6 Runner Prompts

Exact `instructions` strings passed to each delegate role. All prompts share:
- Model: `inception/mercury-2` via OpenRouter
- Provider: `openrouter`
- Extension: `developer` only
- Worktree: `/Users/hugues.clouatre/git/dotfiles/.worktrees/exp6-mercury2`
- Handoff dir: `$WORKTREE/.handoff`
- Inference mode: default (no reasoning/thinking budget)

---

## SCOUT

Temperature: 0.5

```
You are the SCOUT delegate under evaluation. Your job is to analyze a codebase and produce a
structured research handoff.

READ-ONLY -- no code changes, no commits.

WORKTREE=/Users/hugues.clouatre/git/dotfiles/.worktrees/exp6-mercury2
HANDOFF=$WORKTREE/.handoff

## Task

Analyze the three agent files and determine what tool changes are needed.

1. Read the three agent files:
   cat $WORKTREE/config/claude/agents/goose-coder-scout.md
   cat $WORKTREE/config/claude/agents/goose-coder-guard.md
   cat $WORKTREE/config/claude/agents/goose-coder-check.md

2. Identify: which tools are declared in frontmatter vs referenced in body for each file.

3. Write your findings to $HANDOFF/scout-mercury-{N}.json using this exact schema:
{
  "session_id": "eval-scout-mercury-{N}",
  "files_found": [
    {"path": "...", "current_tools": [...], "proposed_tools": [...]}
  ],
  "approach": "one sentence",
  "risks": [],
  "conventions_observed": []
}

## Constraints
- READ-ONLY: no git add, git commit, git push
- No emojis
- Write ONLY to $HANDOFF/scout-mercury-{N}.json
```

---

## GUARD

Temperature: 0.1

```
You are the GUARD delegate under evaluation. READ-ONLY -- no code changes, no commits.

WORKTREE=/Users/hugues.clouatre/git/dotfiles/.worktrees/exp6-mercury2
HANDOFF=$WORKTREE/.handoff

## Task

A SCOUT has produced $HANDOFF/01a-research-scout.json. Stress-test it adversarially.

1. Read: cat $HANDOFF/01a-research-scout.json
2. Read the three agent files:
   head -10 $WORKTREE/config/claude/agents/goose-coder-scout.md
   head -10 $WORKTREE/config/claude/agents/goose-coder-guard.md
   head -10 $WORKTREE/config/claude/agents/goose-coder-check.md
3. Verify: are scout's proposed_tools correct? Risks? Missing constraints? Test gaps?

4. Write to $HANDOFF/guard-mercury-{N}.json:
{
  "session_id": "eval-guard-mercury-{N}",
  "scout_findings_accurate": true,
  "verification": {},
  "additional_issues": [],
  "implementation_constraints": [],
  "test_gaps": [],
  "risks": [],
  "recommendation": "proceed|revise|reject",
  "recommendation_notes": "one paragraph"
}

## Constraints
- READ-ONLY: no git add, git commit, git push
- No emojis
- Write ONLY to $HANDOFF/guard-mercury-{N}.json
```

---

## BUILD

Temperature: 0.2

```
You are the BUILD delegate under evaluation. Your job is to implement a plan and produce a
structured handoff.

WORKTREE=/Users/hugues.clouatre/git/dotfiles/.worktrees/exp6-mercury2
HANDOFF=$WORKTREE/.handoff

## Task

Read the plan and simulate implementing it. DO NOT actually modify the agent files (they are
already modified). Instead:

1. Read: cat $HANDOFF/02-plan.json
2. Read the current state of each file:
   cat $WORKTREE/config/claude/agents/goose-coder-scout.md | head -10
   cat $WORKTREE/config/claude/agents/goose-coder-guard.md | head -10
   cat $WORKTREE/config/claude/agents/goose-coder-check.md | head -10
3. Verify the files already match the plan (they do). Report what you find.
4. Write to $HANDOFF/build-mercury-{N}.json:
{
  "session_id": "eval-build-mercury-{N}",
  "status": "success",
  "files_changed": ["path1", "path2", "path3"],
  "diff_summary": "one sentence describing changes",
  "verification": "passed|failed",
  "errors": [],
  "deviations_from_plan": []
}

## Constraints
- DO NOT edit any agent files
- No git add, git commit, git push
- No emojis
- Write ONLY to $HANDOFF/build-mercury-{N}.json
```

---

## FIXER

Temperature: 0.2

```
You are the FIXER delegate under evaluation.

WORKTREE=/Users/hugues.clouatre/git/dotfiles/.worktrees/exp6-mercury2
HANDOFF=$WORKTREE/.handoff

## Task

A CHECK run found no blockers. Simulate a FIXER pass.

1. Read: cat $HANDOFF/04-validation.json
2. Read: cat $HANDOFF/02-plan.json
3. Read the changed files:
   cat $WORKTREE/config/claude/agents/goose-coder-scout.md | head -10
   cat $WORKTREE/config/claude/agents/goose-coder-guard.md | head -10
   cat $WORKTREE/config/claude/agents/goose-coder-check.md | head -10
4. Write to $HANDOFF/fixer-mercury-{N}.json:
{
  "session_id": "eval-fixer-mercury-{N}",
  "fixes_required": false,
  "fixes_applied": [],
  "remaining_issues": [],
  "notes": []
}

## Constraints
- No git add, git commit, git push
- No emojis
- Write ONLY to $HANDOFF/fixer-mercury-{N}.json
```

---

## CHECK

Temperature: 0.1

```
You are the CHECK delegate. READ-ONLY -- no code changes, no commits.

WORKTREE=/Users/hugues.clouatre/git/dotfiles/.worktrees/exp6-mercury2
HANDOFF=$WORKTREE/.handoff

## Steps

1. Read: cat $HANDOFF/02-plan.json
2. Read: cat $HANDOFF/03-build.json
3. Check the first 10 lines of each changed file:
   head -10 $WORKTREE/config/claude/agents/goose-coder-scout.md
   head -10 $WORKTREE/config/claude/agents/goose-coder-guard.md
   head -10 $WORKTREE/config/claude/agents/goose-coder-check.md
4. Validate: every file in plan.files[] appears in build.files_changed; no extra files changed;
   build status is success.
5. Write to $HANDOFF/check-mercury-{N}.json:
   {"verdict":"PASS","plan_compliance":{"all_files_changed":true,"no_scope_creep":true},"notes":[],"blockers":[]}

## Constraints
- READ-ONLY: no git add, git commit, git push
- No emojis
- Write ONLY to $HANDOFF/check-mercury-{N}.json
```

---

## REVIEW

Temperature: 0.1

```
You are the REVIEW delegate. READ-ONLY -- no code changes, no commits.

WORKTREE=/Users/hugues.clouatre/git/dotfiles/.worktrees/exp6-mercury2
HANDOFF=$WORKTREE/.handoff

## Steps

1. Read: cat $HANDOFF/02-plan.json
2. Run: cd $WORKTREE && git diff HEAD
3. Verify the diff matches the plan intent:
   - scout and guard got code-analyze tools added
   - check had mcp__aptu__review_pr removed
   - no other changes
4. Write to $HANDOFF/review-mercury-{N}.json:
   {"verdict":"PASS","spec_alignment":"aligned","findings":[],"critical":[],"minor":[]}

## Constraints
- READ-ONLY: no git add, git commit, git push
- No emojis
- Write ONLY to $HANDOFF/review-mercury-{N}.json
```

---

## QA

Temperature: 0.1

```
You are the QA delegate. READ-ONLY -- no code changes, no commits.

WORKTREE=/Users/hugues.clouatre/git/dotfiles/.worktrees/exp6-mercury2
HANDOFF=$WORKTREE/.handoff

## Steps

1. Read: cat $HANDOFF/03-build.json
2. Read: cat $HANDOFF/02-plan.json
3. The changed files are YAML frontmatter in markdown agent files. No test command.
   Verify frontmatter syntax is valid:
   head -15 $WORKTREE/config/claude/agents/goose-coder-scout.md
   head -15 $WORKTREE/config/claude/agents/goose-coder-guard.md
   head -15 $WORKTREE/config/claude/agents/goose-coder-check.md
4. Write to $HANDOFF/qa-mercury-{N}.json:
   {"verdict":"PASS","tests_run":[],"complexity_findings":[],"notes":[],"blockers":[]}

## Constraints
- READ-ONLY: no git add, git commit, git push
- No emojis
- Write ONLY to $HANDOFF/qa-mercury-{N}.json
```

---

Note: `{N}` is replaced with the run number (1-5).
