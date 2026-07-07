# Experiment 9 Scorer Prompt

Paste this into a new Goose session (no recipe) from the `~/git/dotfiles` directory.
Run this AFTER all 30 runs are complete. Do NOT run this in the same session as the runner.

---

## Prompt

You are the blind scorer for Experiment 9 (model comparison for SCOUT delegates, round 2). You must score 30 SCOUT delegate outputs against a rubric without knowing which model produced which output.

### Rules

1. You are BLIND. Do not read `experiments/exp9-openrouter-evaluation-r2/label-map.json`. Do not attempt to identify which model produced which run.
2. Score each run independently. Do not compare runs to each other during scoring.
3. Each criterion is binary: 1 (met) or 0 (not met). No partial credit.
4. You must verify claims against the actual aptu codebase before scoring. Clone clouatre-labs/aptu to a temp directory for verification.
5. No emojis in output.

### Setup

```bash
cd ~/git/dotfiles
EXP_DIR=experiments/exp9-openrouter-evaluation-r2

# Verify all 30 run files exist
ls $EXP_DIR/sessions/run-*.json | wc -l
# Should be 30 (run-86 to run-115). If not, STOP and report which runs are missing.

# Clone aptu for verification
APTU_DIR=$(mktemp -d)
gh repo clone clouatre-labs/aptu $APTU_DIR -- --quiet
echo "aptu cloned to $APTU_DIR"
```

### Read the Rubric

```bash
cat $EXP_DIR/rubric.md
```

Understand all 8 criteria (C1-C8) before scoring any run.

### Scoring Loop

For each run NN in {86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115}:

1. Read the run output:
   ```bash
   cat $EXP_DIR/sessions/run-NN.json | jq .
   ```

2. For each criterion C1-C8, verify the claim against the aptu codebase:
   - C1: Does the run identify the correct forge module file path? Verify with `rg` in $APTU_DIR.
   - C2: Does the run reference provider trait/struct patterns with codebase evidence? Verify the cited code exists.
   - C3: Does the run identify test files for forge providers? Verify the test files exist.
   - C4: Does the run reference issue #1205 or multi-forge architecture with structural code terms? Verify the claim.
   - C5: Does the run identify provider-specific differences? Verify the patterns exist in the codebase.
   - C6: Does the run note auth flow differences across providers? Verify the claim is technically accurate.
   - C7: Does the run identify a non-obvious architectural implication with specific evidence? Verify the evidence.
   - C8: Is the output valid JSON with all 11 required schema fields? Validate with `jq`.

3. Record the score for this run before moving to the next.

### Output

After scoring all 30 runs, write `scores.json`:

```bash
cat > $EXP_DIR/scores.json << 'SCORES_EOF'
{
  "scorer": "claude-haiku-4-5-blind",
  "rubric_version": "exp9-v1.0",
  "timestamp": "<ISO8601>",
  "runs": {
    "run-86": {
      "C1": 0, "C2": 0, "C3": 0, "C4": 0, "C5": 0, "C6": 0, "C7": 0, "C8": 0,
      "total": 0,
      "notes": "Brief justification for each 0 score"
    },
    "run-87": { "..." : "..." }
  }
}
SCORES_EOF
```

Replace placeholder values with actual scores. Every 0 score MUST have a note explaining why.

### After Scoring

1. Verify scores.json is valid JSON: `jq . $EXP_DIR/scores.json > /dev/null && echo "VALID"`
2. Report summary: score distribution (min, max, median, mean) across all 30 runs
3. **STOP.** Do not read label-map.json. Do not compute group statistics. The orchestrator does that in a separate step.

Say: "Scoring complete. 30 runs scored. Ready for analysis phase."