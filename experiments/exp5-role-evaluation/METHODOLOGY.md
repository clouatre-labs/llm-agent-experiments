# Methodology

## Design

This is an exploratory n=1 experiment. Unlike exp3/exp4 (n=5, blinded, pre-registered rubric,
Mann-Whitney gates), exp5 uses a single run per cell to answer a binary question: does the model
follow the prompt, read the right files, and produce valid structured JSON output?

For structured output tasks (CHECK, REVIEW, QA, GUARD, BUILD, FIXER), a single run is sufficient
to detect hard blockers: invalid JSON, wrong verdict, hallucinated file paths, constraint violations.
Quality differences between correct outputs are captured via verbosity and turn count.

This design is appropriate for a first-pass feasibility screen. Any model that passes all roles
with n=1 is a candidate for follow-up with n=5 and statistical gates (see exp3/exp4 protocol).

## What "Notes" means

The `notes` field in handoff JSON is a free-text array populated at the delegate's discretion.
Higher notes count = more verbose output, not higher quality. A silent PASS (`notes=[]`) and a
verbose PASS (`notes=[...]`) are equivalent on correctness. Notes were retained in raw session
files for auditability and are not scored.

## Turn count

Turn count = number of agent loop iterations including tool calls. It is not the same as LLM
call count. High turn count increases latency and token cost. It is a proxy for task efficiency:
a model that completes a task in 12 turns is more economical than one that uses 219 turns for
identical output. MiniMax M2.5 consistently used 2-28x more turns than Haiku for equivalent
outputs, making it uneconomical for validation roles despite correct results.

## Wall time

Wall times are approximate, logged from task completion messages in the orchestrator session.
Not instrumented at the API level. Precision is approximately +/- 10s. They reflect real elapsed
time including network latency and queuing on OpenRouter, not pure model inference time.

## SCOUT caveat

SCOUT delegates were evaluated against a pre-patched worktree. The task was to identify what
tool changes were needed across three agent files -- but those changes had already been applied
by a prior session. All three models read the current (correct) state and either reported no
changes needed (Haiku), hallucinated a non-existent inconsistency (Mistral), or went off-task
entirely (MiniMax). This is a task design flaw, not a model capability signal for SCOUT.

The valid SCOUT benchmark remains exp4: clean repo, synthesis from scratch, n=5, blinded, rubric.
Mistral failed exp4 SCOUT (mean=5.4, min=4, C3=0%, C5=0%, 37.5% hard-failure rate). That verdict
stands and is not affected by exp5.

## Relationship to exp3/exp4

exp3 and exp4 tested SCOUT only, using a harder synthesis task (tree-sitter integration analysis
for a Rust security scanner). exp5 extends coverage to all 7 roles using a simpler verification
task (frontmatter patch confirmation). The two experiment series are complementary:

- exp3/exp4: which models can synthesize architectural proposals from a real codebase? (SCOUT)
- exp5: which models can execute structured validation tasks reliably? (all other roles)

Mistral Small 2603 fails the exp4 SCOUT bar and passes the exp5 validation bar. These findings
are consistent: the model is capable of structured read-and-verify tasks but not deep synthesis.
