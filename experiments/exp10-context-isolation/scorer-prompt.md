# Experiment 10 Scorer Prompt

Paste this into a new Goose session (no recipe) from the `~/git/dotfiles` directory.
Run this AFTER all 900 runs are complete. Do NOT run this in the same session as the runner.

---

## Prompt

You are the blind scorer for Experiment 10 (context isolation for GSM8K). You must score 900 model outputs against a rubric without knowing which condition produced which output.

### Rules

1. You are BLIND. Do not read `experiments/exp10-context-isolation/label-map.json`. Do not attempt to identify which condition produced which run.
2. Score each run independently. Do not compare runs to each other during scoring.
3. Each criterion is binary: 1 (met) or 0 (not met). No partial credit.
4. No emojis in output.

### Setup

```bash
cd ~/git/dotfiles
EXP_DIR=experiments/exp10-context-isolation

# Verify all 900 run files exist
for cond in scoped full-history contaminated; do
  count=$(ls $EXP_DIR/sessions/$cond/run-*.json 2>/dev/null | wc -l)
  echo "$cond: $count runs"
done
# Should be 300 per condition (900 total). If not, STOP and report which runs are missing.
```

### Read the Rubric

```bash
cat $EXP_DIR/rubric.md
```

Understand all criteria before scoring any run.

### Scoring Loop

For each condition in {scoped, full-history, contaminated} and each run NNN in {000..299}:

1. Read the run output:
   ```bash
   cat $EXP_DIR/sessions/<condition>/run-NNN.json | jq .
   ```

2. For each criterion, evaluate the model output:
   - C1: Does the output contain a step-by-step reasoning process?
   - C2: Does the output contain a final answer (standalone number)?
   - C3: Is the final answer a valid integer or decimal?
   - C4: Is the output free of refusal or safety-related disclaimers?

3. Record the score for this run before moving to the next.

### Output

After scoring all 900 runs, write `scores.json`:

```bash
cat > $EXP_DIR/scores.json << 'SCORES_EOF'
{
  "scorer": "claude-haiku-4-5-blind",
  "rubric_version": "exp10-v1.0",
  "timestamp": "<ISO8601>",
  "runs": {
    "scoped/run-000": {
      "C1": 0, "C2": 0, "C3": 0, "C4": 0,
      "total": 0,
      "notes": "Brief justification for each 0 score"
    },
    ...
  }
}
SCORES_EOF
```

Replace placeholder values with actual scores. Every 0 score MUST have a note explaining why.

### After Scoring

1. Verify scores.json is valid JSON: `jq . $EXP_DIR/scores.json > /dev/null && echo "VALID"`
2. Report summary: score distribution (min, max, median, mean) across all 900 runs
3. **STOP.** Do not read label-map.json. Do not compute group statistics. The orchestrator does that in a separate step.

Say: "Scoring complete. 900 runs scored. Ready for analysis phase."
