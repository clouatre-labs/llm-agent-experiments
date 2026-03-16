# Methodology

## Agent Architecture

All experiments use the Goose agent framework with the `goose-coder` recipe (v4.2.1, dotfiles commit d4ac9e8). The architecture consists of:

- **Orchestrator:** Claude Sonnet 4.6 via GCP Vertex AI, temperature 0.3. Manages task decomposition, delegate spawning, and result aggregation.
- **SCOUT delegate:** Model under test (varies by experiment). Receives lens (isolated coding task), produces synthesis artifact (code, docs, tests).
- **Guard delegate:** Claude Haiku 4.5 (fixed baseline). Validates SCOUT output against rubric (C1-C8 criteria).
- **Scorer subagent:** Blind subagent (no model labels until after scoring). Applies 8-criterion rubric independently.

## Delegate Models

### Experiment 3 (Discovery Phase)

Baseline and three candidate models, each tested n=5:

- **Claude Haiku 4.5 (baseline):** Anthropic, commercial API
- **Qwen3 Coder:** Alibaba Qwen, open-weight (7B), via OpenRouter
- **Gemini 3 Flash:** Google, commercial API
- **Devstral 2512:** Mistral AI, open-weight (7B), via HuggingFace

### Experiment 4 (Validation Phase)

Baseline reused (exp3 runs 1-5) and three new candidates, each n=5 (DeepSeek n=3 due to failures):

- **Claude Haiku 4.5 (baseline):** Reused from exp3 (mean=5.8)
- **MiniMax M2.5:** Chinese Minimax, open-weight via OpenRouter
- **DeepSeek V3.2:** Chinese DeepSeek, commercial API
- **Kimi K2.5:** Chinese Moonshot, commercial API

## Blinding Procedure

1. **Label-map creation:** Before any SCOUT delegate is spawned, a label-map.json file is written: `{run_id: model_name}` (e.g., `{"001": "claude-haiku-4-5", "002": "qwen3-coder"}`). This file is sealed (version controlled but not revealed until after scoring).
2. **Scorer receives numeric labels only:** Scorer subagent receives run data with `run_id` (numeric), scores, timestamps, and error messages—but NO model names.
3. **Post-scoring reveal:** After all scoring is complete and recorded, label-map.json is published in data/{exp}/label-map.json. Scorer then reconciles their independent annotations with actual models.

## Orchestrator Configuration

- **Model:** Claude Sonnet 4.6 (GCP Vertex AI)
- **Temperature:** 0.3 (low entropy for reproducibility)
- **Extensions:** Goose recipe v4.2.1 includes think, delegate, and guard extensions
- **Session timeout:** 15 minutes per run

## Scoring Rubric (C1-C8, Binary 0-1 per Criterion)

| Criterion | Meaning |
|-----------|---------|
| C1 | Correct problem decomposition: does the solution parse the task correctly? |
| C2 | Appropriate tool selection: are chosen tools and approaches suitable for the lens? |
| C3 | Valid syntax: do all code artifacts compile/execute without syntax errors? |
| C4 | Edge case handling: does the solution anticipate and handle boundary conditions? |
| C5 | Error handling: are exceptions, null checks, and error states properly handled? |
| C6 | No circular or redundant logic: is the code free of unnecessary repetition or cycles? |
| C7 | Architecture matches specification: does the design align with the stated requirements? |
| C8 | Code usability and clarity: is the code readable, well-named, and easy to understand? |

**Total score per run:** sum of C1-C8 (range 0-8).

## Gate Criteria (Non-Inferiority)

A candidate passes if ALL four gates are satisfied:

1. **Mean threshold:** candidate_mean > 5.3 (must exceed floor)
2. **Floor criterion:** min(candidate_scores) >= 5 (no single run below 5)
3. **Completeness error rate:** (failed_runs / total_attempted) <= 0.2 (at most 1 failure per 5 runs)
4. **Non-inferiority:** Mann-Whitney U test p > 0.05 (cannot reject equality with baseline) AND rank-biserial r >= -0.5 (effect size acceptable)

**Verdict:** PASS if all four gates met; FAIL otherwise.

## Statistical Test: Mann-Whitney U

- **Null hypothesis:** Candidate and baseline populations have the same distribution.
- **Alternative hypothesis (two-tailed):** Distributions differ.
- **Test:** Mann-Whitney U with exact permutation (n=5 per group, all permutations enumerated).
- **Alpha:** 0.05 (critical p-value).
- **Effect size:** Rank-biserial correlation r (reported alongside p).
- **Interpretation:** p > 0.05 means we fail to reject the null hypothesis (no significant difference from baseline); candidate is non-inferior.

## Limitations

1. **Sample size (n=5):** Underpowered for strong statistical inference. Power analysis indicates ~40% power to detect a 0.5 SD effect size at alpha=0.05. Results are indicative, not definitive; confidence intervals are wide.

2. **No raw conversation logs:** Goose session records (full conversational trace, token counts per turn, model-specific generation parameters) are not included. Only scored outputs and summary handoff metadata are available. Reproducibility is limited to recipe-level replay; model-level debugging is not possible without logs.

3. **Qwen3 Coder exclusion (exp3):** Seven spawn attempts produced zero parseable outputs. Cause unclear: could be infrastructure (API timeouts), model capability (instruction-following), or recipe incompatibility. Excluded from quantitative comparison; classified as "0/7 valid runs."

4. **DeepSeek V3.2 partial sample (exp4):** Two of five runs (27, 30) failed with infrastructure errors. Only n=3 valid runs for DeepSeek. This increases uncertainty in the mean and p-value. Reported with explicit caveat.

5. **Single orchestrator:** All runs used Claude Sonnet 4.6. Generalization to other orchestrators (Haiku, Opus, open-weight) is unknown.

6. **Baseline reuse in exp4:** Exp4 reuses exp3's baseline scores (runs 1-5) rather than collecting new exp4 runs. This preserves baseline reproducibility but introduces potential confounding (exp3 and exp4 context may differ).

7. **Temperature setting:** All runs at temperature 0.3. Sensitivity to temperature variations is not explored.

## Reproducibility

To reproduce these experiments:

1. **Install Goose** with the version noted in Software Versions (README.md).
2. **Load the recipe:** Copy `recipe/goose-coder.yaml` into your local Goose config directory (`~/.config/goose/recipes/`).
3. **Set orchestrator:** Configure Claude Sonnet 4.6 via GCP Vertex AI as the primary orchestrator; temperature 0.3.
4. **Prepare label-map:** Write a `label-map.json` file with run IDs and model assignments before spawning any delegates.
5. **Run SCOUT delegates:** Use the goose coder recipe to spawn SCOUT delegates for each task, recording session IDs and handoff outputs.
6. **Run scorer:** Spawn a blind scorer subagent that receives run data WITHOUT model labels. Scorer applies C1-C8 rubric and records scores.
7. **Post-scoring reveal:** Publish label-map.json; reconcile scores with model identities.
8. **Statistical analysis:** Compute means, error rates, Mann-Whitney U p-values, and apply gate criteria (see gate section above).

## References

- Mann-Whitney U test: https://en.wikipedia.org/wiki/Mann%E2%80%93Whitney_U_test
- Rank-biserial correlation: https://en.wikipedia.org/wiki/Rank_correlation#Rank-biserial_correlation
- Goose agent framework: https://github.com/block/goose
- goose-coder recipe: https://github.com/clouatre-labs/dotfiles/blob/d4ac9e8/config/goose/recipes/goose-coder.yaml
