# Experiment 9: Scoring Rubric

Scoring criteria for the SCOUT research task on clouatre-labs/aptu#1205 (feat(core): multi-forge support for GitLab, Gitea/Forgejo, and Azure DevOps).

## Criteria

### C1: Forge module implementation files identified

**Criterion:** Delegate identifies the correct files related to forge/provider implementation in the aptu codebase.

**Ground truth:** The forge module lives under `crates/aptu-core/src/forge/` and includes provider implementations (GitHub provider, etc.), trait definitions, and auth modules. Acceptable files include `crates/aptu-core/src/forge.rs`, `crates/aptu-core/src/forge/*.rs`, provider files, and related trait definitions.

**Scoring:** 1 if delegate names at least one specific forge-related file and verifies it exists in the repo. 0 if delegate speaks generically about "the forge module" without naming a file.

**Rationale:** Ensures delegate actually navigated the codebase rather than relying on parametric knowledge.

---

### C2: Provider trait pattern understood

**Criterion:** Delegate demonstrates understanding of how forge providers are implemented -- the trait pattern, provider registration, and dispatch.

**Ground truth:** The forge module uses a trait-based design (e.g., `ForgeProvider` trait) with individual provider structs implementing the trait. The delegate should reference `impl ... for Github`, provider registration, or dispatch logic.

**Scoring:** 1 if delegate references specific provider trait/struct/enum patterns with codebase evidence. 0 if delegate speaks in generalities without evidence.

**Rationale:** Demonstrates code comprehension at the implementation level.

---

### C3: Test coverage for existing forge providers noted

**Criterion:** Delegate identifies at least one relevant test file or test function for forge providers.

**Ground truth:** Look for test files in `crates/aptu-core/tests/` or `crates/aptu-core/src/forge/` with tests exercising provider behaviors.

**Scoring:** 1 if delegate names a test file or test function related to forge/provider functionality. 0 if no test references.

**Rationale:** Tests are critical for safely extending provider support.

---

### C4: Multi-forge architecture references

**Criterion:** Delegate identifies issue #1205 or references multi-forge architecture concerns (forge domain concepts, provider abstraction patterns).

**Ground truth:** The issue is about adding support for GitLab, Gitea/Forgejo, and Azure DevOps as forge providers. Acceptable references include the issue number (#1205) or domain-specific terms like 'forge', 'gitlab', 'gitea', 'forgejo', 'azure devops', 'multi-forge', combined with structural references like 'trait', 'aptu-core', 'impl', 'backend', 'provider'.

**Scoring:** 1 if delegate references #1205 directly OR references multi-forge domain terms combined with structural code terms. 0 if delegate makes no connection to multi-forge architecture.

**Rationale:** Ensures delegate engaged with the specific issue's domain and considered architectural implications.

---

### C5: Provider-specific patterns identified

**Criterion:** Delegate identifies at least 2 specific patterns or approaches that differ across forge providers (GitLab vs GitHub vs Gitea/Forgejo vs Azure DevOps).

**Ground truth:** Different forges have different API patterns: GitLab uses project IDs vs GitHub uses owner/repo, Azure DevOps uses organization/project/repo paths, Gitea/Forgejo use similar patterns to GitHub but with different API endpoints, auth mechanisms differ (personal access tokens vs OAuth vs Azure AD).

**Scoring:** 1 if delegate identifies at least 2 specific provider-specific differences with codebase evidence or API comparison. 0 if delegate treats all providers as identical or mentions only generic patterns.

**Rationale:** Demonstrates understanding that providers are not drop-in replacements.

---

### C6: Auth flow differences noted

**Criterion:** Delegate identifies that different forge providers have different authentication mechanisms and notes the implications for the existing auth code.

**Ground truth:** GitHub uses personal access tokens (classic and fine-grained), GitLab uses personal/project/group access tokens, Azure DevOps uses Azure AD / PAT, Gitea/Forgejo use their own token types. The existing auth code may need to be extended or abstracted.

**Scoring:** 1 if delegate makes an explicit statement about auth flow differences across providers and how they impact the codebase. 0 if auth is not mentioned or is dismissed as trivial.

**Rationale:** Auth is often the most complex part of multi-provider support. Demonstrates architectural maturity.

---

### C7: Non-obvious architectural implication requiring code synthesis

**Criterion:** Delegate identifies a non-obvious architectural implication that requires reading and synthesizing code, not just summarizing the issue.

**Ground truth:** Examples of acceptable responses:
- Recognizing that the existing `ForgeProvider` trait may need new methods (e.g., for repo discovery, webhook management) that not all providers can implement
- Identifying that provider-specific URL parsing (SSH vs HTTPS, different path formats) requires a new abstraction layer
- Noting that rate-limiting and API versioning differ per provider and proposing a strategy
- Recognizing that existing tests that mock GitHub will not port directly to other providers
- Identifying that CI/CD integrations (GitHub Actions vs GitLab CI vs Azure Pipelines) may require separate handling

**Scoring:** 1 if delegate identifies at least one non-obvious implication that requires synthesis beyond the issue text. 0 if all points are direct summaries of the issue or generic advice.

**Rationale:** Prevents ceiling effect. Requires delegate to think beyond the issue description.

---

### C8: Valid JSON output per handoff schema

**Criterion:** Delegate produces a valid JSON file matching the handoff schema specified in the orchestration instructions.

**Ground truth:** Output file must be valid JSON (parseable by `jq`), must contain required fields per the SCOUT handoff schema: `session_id`, `lens`, `relevant_files`, `conventions`, `patterns`, `related_issues`, `constraints`, `test_coverage`, `library_findings`, `approaches`, `recommendation`. Must not contain syntax errors.

**Scoring:** 1 if output file is valid JSON and contains all required fields per the handoff schema. 0 if file is missing, is not valid JSON, or is missing required fields.

**Rationale:** Ensures delegate followed instructions and produced machine-readable output. Non-negotiable for downstream processing.

---

## Scoring Procedure

1. **Scorer receives:** 30 run files (`run-86.json` through `run-115.json`), this rubric, and no other metadata
2. **Scorer does not receive:** `label-map.json`, model names, run order, or any information that would reveal which model produced which run
3. **For each run:** Score each criterion independently (1 or 0)
4. **Total score:** Sum of all 8 criteria (0-8)
5. **Output:** Write `scores.jsonl` with run ID, individual criterion scores, total score, and brief justification for each criterion
6. **After scoring:** Orchestrator reveals `label-map.json` and computes group statistics

---

## Justification Format

For each criterion, scorer provides a brief justification (1-2 sentences) explaining why the criterion was met or not met. Examples:

- **C1 met:** "Delegate explicitly names `crates/aptu-core/src/forge.rs` and verifies it exists in the repo."
- **C1 not met:** "Delegate mentions 'the forge module' but does not name a specific file or verify its location."
- **C7 met:** "Delegate recognizes that provider-specific URL parsing requires a new abstraction layer and proposes concrete handling strategy."
- **C7 not met:** "Delegate summarizes the issue but does not propose any non-obvious architectural implications."

---

## Amendments vs exp8

Compared to Experiment 8 rubric (which was adapted from exp3), this rubric makes three changes:

1. **Domain shift:** All criteria now reference forge/multi-forge architecture (Issue #1205) instead of SecurityScanner/tree-sitter (Issue #737).
2. **C4 broadened:** Issue reference OR multi-forge domain keywords combined with structural code keywords, instead of old #735/#736/#737 check.
3. **C8 unchanged:** Same handoff schema validation (11 required JSON fields).

---

## References

- Target issue: https://github.com/clouatre-labs/aptu/issues/1205
- Forge module context: `crates/aptu-core/src/forge.rs`, provider implementations in `crates/aptu-core/src/forge/`
- Experiment 8 rubric: `experiments/exp8-openrouter-evaluation/`