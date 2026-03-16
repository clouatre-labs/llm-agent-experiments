---
name: New Experiment Proposal
about: Propose a new model comparison or agent evaluation experiment
title: 'exp[N]: [brief description]'
labels: experiment
assignees: ''
---

## Research Question

<!-- What hypothesis are you testing? Be specific. -->

## Task

<!-- Which issue or codebase will delegates analyze? -->

## Models to Evaluate

<!-- List candidate models and the baseline model. -->

| Model | Provider | Cost/MTok (in/out) | Rationale |
|-------|----------|-------------------|-----------|
| (baseline) | | | |
| | | | |

## Sample Size

<!-- How many valid runs per model? Justify stopping rule. -->

n = ___ valid runs per model. Fixed sample, no sequential expansion.

## Blinding

<!-- How will model identity be concealed from the scorer? -->

## Gate Criteria

<!-- What must a candidate satisfy to pass? -->

- [ ] Gate 1: Mean score >= ___
- [ ] Gate 2: No run below ___
- [ ] Gate 3: Error rate <= ___
- [ ] Gate 4: Non-inferiority (Mann-Whitney p > 0.05)

## Pre-registration Checklist

- [ ] Protocol locked before any delegates spawned
- [ ] label-map.json written and sealed before run 1
- [ ] Rubric written and locked before run 1
- [ ] Stopping rule fixed (no early stopping)
