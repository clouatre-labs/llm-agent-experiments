# Experiment 10: Context Isolation for GSM8K

## Scoring Rubric

### C1: Step-by-step reasoning

**Criterion:** The model output contains a step-by-step reasoning process leading to the final answer.

**Scoring:** 1 if the output shows intermediate reasoning steps (not just the final answer). 0 if the output is only the final answer with no reasoning.

**Rationale:** GSM8K is designed to test multi-step math reasoning. A correct answer without reasoning may indicate memorization or guessing.

---

### C2: Final answer present

**Criterion:** The model output contains a standalone final answer (integer or decimal number).

**Scoring:** 1 if the output contains at least one standalone number that could be the answer. 0 if no number is present.

**Rationale:** The primary task is to produce a numeric answer. Outputs without numbers are non-responsive.

---

### C3: Valid numeric format

**Criterion:** The final answer is a valid integer or decimal number.

**Scoring:** 1 if the final answer is a valid integer (e.g., 42) or decimal (e.g., 3.14). 0 if the answer contains non-numeric characters, fractions, or is malformed.

**Rationale:** Ensures the answer can be compared to the gold standard.

---

### C4: No refusal or safety disclaimers

**Criterion:** The output does not contain refusals, safety disclaimers, or statements about inability to answer.

**Scoring:** 1 if the output directly addresses the math problem without disclaimers. 0 if the output contains "I cannot", "I'm unable", "As an AI", or similar refusal language.

**Rationale:** Refusals indicate the model is not engaging with the task, which is a failure mode for the experiment.
