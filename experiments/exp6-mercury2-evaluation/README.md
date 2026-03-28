# Experiment 6: Mercury 2 Multi-Role Evaluation

## Research Question

Can `inception/mercury-2` (a diffusion-based LLM) replace `claude-haiku-4-5` in goose-coder
delegate roles without degrading output quality, and can it succeed as SCOUT where
`mistral-small-2603` failed (exp4 mean=5.4/8)?

## Context

Exp3 and exp4 evaluated SCOUT replacements using a tree-sitter synthesis task (n=5, C1-C8 rubric,
blinded). Exp5 extended coverage to all 7 roles using a simpler frontmatter verification task
(n=1 per role, binary correct/incorrect). This experiment applies exp4-style n=5 runs to the
exp5 task, enabling statistical comparison with Mistral Small 2603's exp4 SCOUT score.

Haiku 4.5 baseline: exp3/exp4 mean=5.8/8 (SCOUT, tree-sitter task).
Mistral Small 2603: exp4 mean=5.4/8 (SCOUT, tree-sitter task, verdict=fail).
Mercury 2: exp6 mean=4.6/8 (SCOUT, frontmatter task, this experiment).

**Direct comparison caveat:** The exp6 SCOUT task differs from exp3/exp4. The rubric was adapted
for the frontmatter task. C4 and C6 are structurally 0 for all models when the worktree is
pre-patched (same caveat as exp5). The 4.6 mean includes two structural zeros not attributable
to model capability.

## Method

- 5 runs per role (35 total Mercury 2 invocations)
- Same worktree as exp5: detached HEAD at commit `982531392de` (post-patch state)
- SCOUT: binary C1-C8 rubric adapted for frontmatter task (see `rubric.md`)
- All other roles: binary correct/incorrect per exp5 methodology
- Provider: OpenRouter (`inception/mercury-2`)
- Temperature: role-dependent (see protocol.md)
- Extensions: `developer` only
- Orchestrator: Claude Sonnet 4.6 (goose session, current)
- Same SCOUT caveat as exp5: worktree pre-patched; C4 and C6 structurally 0

## Results

### SCOUT (C1-C8 rubric)

| Run | C1 | C2 | C3 | C4 | C5 | C6 | C7 | C8 | Total |
|-----|----|----|----|----|----|----|----|----|-------|
| 1   |  1 |  1 |  1 |  0 |  1 |  0 |  0 |  1 |   5   |
| 2   |  1 |  0 |  0 |  0 |  1 |  0 |  0 |  1 |   3   |
| 3   |  1 |  1 |  1 |  0 |  1 |  0 |  0 |  1 |   5   |
| 4   |  1 |  1 |  1 |  0 |  1 |  0 |  0 |  1 |   5   |
| 5   |  1 |  1 |  1 |  0 |  1 |  0 |  0 |  1 |   5   |

**Mean: 4.6/8 | Min: 3 | Max: 5 | Error rate: 0.0%**

C4=0 across all 5 runs is a task design constraint (worktree pre-patched, removal already applied),
not a Mercury 2 failure. Same applies to Haiku and Mistral in exp5.

C7=0 across all 5 runs. Mercury 2 never populated `conventions_observed`. Haiku populated it in
exp5 (4 observations including mcp__ prefix and JSON array conventions). This is the only
consistent quality gap vs Haiku.

Run 2 anomaly: proposed_tools = `["gh"]` only, dropping all 10 current tools. Mercury 2
hallucinated that `gh` is the only missing tool. This represents a hard failure mode.

### All Roles (binary correct/incorrect)

| Role   | n  | Correct | Pass rate | Notes |
|--------|----|---------|-----------|-------|
| SCOUT  | 5  | n/a     | n/a       | Scored via C1-C8 rubric; pre-patched caveat applies |
| GUARD  | 5  | 4/5     | 80%       | Run 4: false revise verdict on speculative risks |
| BUILD  | 5  | 5/5     | 100%      | All runs: status=success, verification=passed |
| FIXER  | 5  | 5/5     | 100%      | All runs: fixes_required=false, correct |
| CHECK  | 5  | 5/5     | 100%      | All runs: verdict=PASS, plan compliance correct |
| REVIEW | 5  | 5/5     | 100%      | All runs: verdict=PASS, spec_alignment=aligned |
| QA     | 5  | 5/5     | 100%      | All runs: verdict=PASS, frontmatter valid |

Note: initial REVIEW runs (sessions 20260328_110-114) used `git diff HEAD` which returns empty
on a committed worktree. Re-run with `git diff HEAD~1 HEAD`. Documented as a prompt design gap,
not a model failure. Mercury 2 correctly reported FAIL when diff was empty.

### Performance and Cost

| Role   | Mean tokens | Mean in | Mean out | Mean wall (s) | Cost/run ($) |
|--------|------------|---------|----------|---------------|--------------|
| SCOUT  |     11,237 |  11,051 |      186 |           5.8 |      0.00290 |
| GUARD  |      6,244 |   6,159 |       85 |           3.0 |      0.00160 |
| BUILD  |      6,062 |   5,894 |      168 |           3.2 |      0.00160 |
| FIXER  |      5,722 |   5,675 |       48 |           2.4 |      0.00145 |
| CHECK  |      6,304 |   6,198 |      106 |           3.6 |      0.00163 |
| REVIEW |      6,131 |   6,059 |       72 |           1.8 |      0.00157 |
| QA     |      6,410 |   6,326 |       84 |           3.2 |      0.00164 |

**Total per full pipeline run (7 roles): $0.0124**
**Total for all 35 experiment runs: $0.062**

Pricing: $0.25/M input, $0.75/M output (OpenRouter, 2026-03-28).

### Comparison with Haiku 4.5 and Mistral Small 2603 (exp5 data, n=1)

| Model | SCOUT wall (s) | Pipeline wall (s) | Pipeline cost ($) | GUARD pass | BUILD pass |
|-------|---------------|-------------------|-------------------|------------|------------|
| Haiku 4.5 | 61 | 184 | 0.0685 | 1/1 | 1/1 |
| Mistral 2603 | 9 | 86 | 0.0097 | 1/1 | 1/1 |
| **Mercury 2** | **5.8** | **23** | **0.0124** | **4/5** | **5/5** |

Mercury 2 is the fastest model tested across all roles. Pipeline wall time 8x faster than Haiku,
3.7x faster than Mistral. Cost 5.5x cheaper than Haiku, 28% more expensive than Mistral.

Mercury 2 SCOUT output tokens are extremely low (mean=186 vs Haiku ~600+). This reflects the
diffusion model's tendency toward minimal completions. It can produce correct structured JSON
in 4 runs out of 5, but run 2 shows instability (proposed_tools truncated to single hallucinated
tool).

## SCOUT Failure Analysis

### Consistent failures

**C4 (removal detection):** 0/5. Task design constraint. The worktree is pre-patched;
`mcp__aptu__review_pr` is already absent. Mercury 2 correctly reads the current state (no tool
to remove). Same failure in all exp5 models. Not a Mercury 2 capability signal.

**C6 (change direction):** 0/5. Post-patch worktree means current==proposed in most runs.
Mercury 2 does not infer historical change direction from current state (nor does Haiku or
Mistral in exp5).

**C7 (conventions_observed):** 0/5. Mercury 2 always returns empty `conventions_observed`.
Haiku populated this field with 4 relevant observations in exp5. This is a genuine gap: Mercury
2 completes the structural task but omits the convention-extraction component.

### Run 2 anomaly

Run 2 proposed `["gh"]` as the sole tool for scout.md and guard.md, dropping all 10 existing
tools. This is a hard failure: incorrect proposed_tools, incorrect change scope. In a real
pipeline, a GUARD agent would catch this. The 20% single-run anomaly rate (1/5) matches
Mistral's instability pattern from exp4 (37.5% hard-failure rate on SCOUT).

## Findings

1. **Mercury 2 passes all execution roles** (BUILD, FIXER, CHECK, REVIEW, QA) with 100%
   correctness and 5/5 runs each. Zero blockers in all 25 valid execution cells.

2. **Mercury 2 GUARD is 80% correct** (4/5 runs). Run 4 produced a false `revise` verdict
   based on speculative risks (untrusted web data, resource intensity). No actual blockers
   were identified. GUARD failure rate is higher than Haiku/Mistral (both 100% in exp5, n=1).

3. **Mercury 2 SCOUT scores 4.6/8 mean** on the adapted rubric. Excluding the two structural
   zeros (C4, C6), the adjusted score is 4.6/6 = 77%. The remaining gap vs Haiku (exp5: C7
   populated, richer output) is Mercury 2's empty `conventions_observed` and one hard-failure
   run (run 2).

4. **Mercury 2 is the fastest model tested**: 5.8s SCOUT, 23s full pipeline. 8x faster than
   Haiku, 3.7x faster than Mistral. This reflects the diffusion architecture's speed advantage.

5. **Mercury 2 output tokens are minimal**: mean 186 output tokens for SCOUT vs ~500+ expected
   from Haiku. The model is terse. This reduces output cost significantly but may limit
   verbosity in roles requiring detailed analysis (GUARD notes, REVIEW findings).

6. **Cost is competitive**: $0.0124/pipeline vs $0.0685 (Haiku) and $0.0097 (Mistral). Mercury
   2 is 5.5x cheaper than Haiku but 28% more expensive than Mistral per pipeline run.

## Recommended Role Assignments (updated with Mercury 2)

| Role   | Recommended model | Rationale |
|--------|-------------------|-----------|
| SCOUT  | `claude-sonnet-4-6` | Mercury 2 run 2 anomaly (hard failure), empty conventions, C7=0. Sonnet remains the only reliable SCOUT. |
| GUARD  | `mistralai/mistral-small-2603` | Mercury 2 80% pass rate (1/5 false revise); Mistral 100% in exp5 with richest verification output. |
| BUILD  | `inception/mercury-2` | 100% pass rate, 3.2s, $0.0016/run. Fastest and cheapest among models with perfect BUILD record. |
| FIXER  | `inception/mercury-2` | 100% pass rate, 2.4s, $0.0014/run. Fastest FIXER by a large margin (Haiku: 29s, Mistral: 9s). |
| CHECK  | `inception/mercury-2` | 100% pass rate, 3.6s, $0.0016/run. Faster than both baselines, zero false positives. |
| REVIEW | `inception/mercury-2` | 100% pass rate, 1.8s, $0.0016/run. Fastest REVIEW tested. |
| QA     | `inception/mercury-2` | 100% pass rate, 3.2s, $0.0016/run. Zero notes (terse but correct). |

### Mixed-model configuration

Mercury 2 is strong for execution roles (BUILD, FIXER, CHECK, REVIEW, QA): 100% correctness
across 25 cells. Mistral remains better for GUARD (richer output, no false revise verdicts).
SCOUT stays on Sonnet.

Proposed production configuration:
- SCOUT: `gcp_vertex_ai/claude-sonnet-4-6@default`
- GUARD: `openrouter/mistralai/mistral-small-2603`
- BUILD, FIXER, CHECK, REVIEW, QA: `openrouter/inception/mercury-2`

Estimated pipeline cost with mixed config:
- SCOUT (Sonnet): ~$0.02-0.05/run (token-dependent)
- GUARD (Mistral): ~$0.0017/run
- Execution roles (Mercury 2, 5 roles): ~$0.008/run
- Total: ~$0.03-0.06/pipeline (vs $0.0685 Haiku-only)

## Limitations

- n=5 per role; no statistical gates vs Haiku (Mann-Whitney requires known baseline distribution)
- SCOUT task mismatch: rubric adapted from exp3/exp4 tree-sitter task; direct comparison
  to exp4 Mistral mean (5.4/8, different task) is indicative only
- GUARD run 4 false revise verdict may reflect temperature sensitivity; single observation
- Wall times measured as goose session DB timestamps (orchestrator overhead not excluded)
- Mercury 2 via OpenRouter; Inception's direct API may differ in latency and structured output stability
- All runs used `developer` extension only; production delegates use additional extensions

## Reproducibility

- Worktree: `/Users/hugues.clouatre/git/dotfiles/.worktrees/exp6-mercury2` (preserved)
- Commit: `982531392de` (detached HEAD)
- All session outputs: `sessions/` directory (35 files)
- Latency log: `latency-log.jsonl`
- Scores: `scores.json`
- Rubric: `rubric.md`
- Prompts: `runner-prompts.md`

## Next Steps

- exp7: evaluate Mercury 2 BUILD on a real code diff with test failures (harder BUILD task)
  to confirm 100% correctness holds on non-trivial changes
- exp7: n=5 GUARD runs for Mistral to get statistical baseline for GUARD role
- Consider AGENTS.md update: add `inception/mercury-2` as known OpenRouter model for execution
  roles, with caveat about run 2 SCOUT anomaly
- Production deployment: gate Mercury 2 execution roles behind Mistral GUARD for safety
