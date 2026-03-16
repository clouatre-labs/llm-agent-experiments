# Experiment 4 Scorer Prompt

Paste this into a new Goose session (no recipe) from the `~/git/dotfiles` directory.
This session must be separate from the runner session to maintain blinding.

---

## Prompt

You are the blind scorer for Experiment 4 (model comparison round 2 for SCOUT delegates).
Score each run output against the rubric. You do not know which model produced which run.

### Setup

```bash
cd ~/git/dotfiles
EXP_DIR=experiments/exp4-model-comparison-r2

# Clone aptu for verification (same as delegates did)
APTU_DIR=$(mktemp -d)
gh repo clone clouatre-labs/aptu $APTU_DIR
echo "aptu cloned to $APTU_DIR"

# List available run outputs
ls $EXP_DIR/sessions/scout-run-*.json | sort
```

### Read the Rubric

Read the rubric carefully before scoring any runs:

```bash
cat experiments/exp3-model-comparison/rubric.md
```

Note: The rubric is in the exp3 directory (shared between exp3 and exp4).

### Scoring Rules

1. **Do NOT read label-map.json** -- you must not know which model produced which run
2. Score each run independently -- do not compare runs to each other
3. Each criterion is binary: 1 (pass) or 0 (fail)
4. For criteria requiring codebase verification (C1, C2, C3, C4, C5), check claims against the cloned aptu repo
5. Write brief justification notes for each criterion
6. If a run output file is missing or not valid JSON, score it as 0/8 with a note

### Scoring Loop

For each run file in `$EXP_DIR/sessions/scout-run-*.json` (sorted numerically):

1. Read the run output:
   ```bash
   cat $EXP_DIR/sessions/scout-run-NN.json | jq .
   ```

2. Score against each criterion (C1-C8) using the rubric. For each criterion:
   - Check the specific evidence required
   - Verify claims against the aptu codebase where required
   - Assign 1 or 0
   - Write a brief justification note

3. Record the total (sum of C1-C8)

### Output

After scoring all runs, write results to `$EXP_DIR/scores.json`:

```json
{
  "scorer": "claude-haiku-4-5-blind",
  "rubric_version": "1.0 (shared with exp3)",
  "timestamp": "<ISO 8601>",
  "notes": "Blind scoring of exp4 runs 21-35. Scorer did not read label-map.json.",
  "runs": {
    "run-21": {
      "C1": 0, "C2": 0, "C3": 0, "C4": 0, "C5": 0, "C6": 0, "C7": 0, "C8": 0,
      "total": 0,
      "notes": {
        "C1": "justification",
        "C2": "justification",
        "C3": "justification",
        "C4": "justification",
        "C5": "justification",
        "C6": "justification",
        "C7": "justification",
        "C8": "justification"
      }
    }
  }
}
```

### After Scoring All Runs

1. Verify scores.json is valid:
   ```bash
   jq . $EXP_DIR/scores.json > /dev/null && echo "VALID" || echo "INVALID"
   ```

2. Print summary table:
   ```bash
   jq -r '.runs | to_entries | sort_by(.key) | .[] | "\(.key): \(.value.total)/8"' $EXP_DIR/scores.json
   ```

3. **STOP.** Do not read label-map.json. Do not group by model. Do not compute statistics.
   Analysis is a separate session.

Say: "Scoring complete. Ready for analysis phase in a separate session."
