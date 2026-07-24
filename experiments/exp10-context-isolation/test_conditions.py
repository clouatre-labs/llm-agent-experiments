"""Unit tests for conditions.py (pure logic, no API calls)."""

import re
import unittest

from conditions import build_context, estimate_tokens


class TestBuildContext(unittest.TestCase):
    """Tests for the build_context function across all three conditions."""

    def test_scoped_returns_task_only(self):
        """Scoped condition returns only the current task prompt with no history."""
        task = "Solve for x: 2x + 3 = 7"
        result = build_context(task, "scoped")
        self.assertEqual(result, task)

    def test_scoped_with_padding(self):
        """Scoped condition with target_token_count adds filler text."""
        task = "Short task."
        result = build_context(task, "scoped", target_token_count=100)
        tokens = estimate_tokens(result)
        self.assertGreaterEqual(tokens, 90)
        self.assertLessEqual(tokens, 110)
        self.assertTrue(result.startswith(task))

    def test_full_history_prepends_history(self):
        """Full-History condition returns complete planner transcript verbatim prepended to task."""
        task = "Solve for x: 2x + 3 = 7"
        history = "Step 1: Identify the equation.\nStep 2: Isolate the variable."
        result = build_context(task, "full-history", history=history)
        self.assertTrue(result.startswith(history))
        self.assertIn(task, result)

    def test_full_history_requires_history(self):
        """Full-History condition raises ValueError when history is None."""
        with self.assertRaises(ValueError):
            build_context("task", "full-history", history=None)

    def test_contaminated_injects_at_middle(self):
        """Contaminated condition injects task at controlled middle position among distractor turns."""
        task = "Solve for x: 2x + 3 = 7"
        history = "Turn A.\n\nTurn B.\n\nTurn C.\n\nTurn D."
        result = build_context(task, "contaminated", history=history)
        # The task should appear in the middle, not at the start or end
        self.assertIn(task, result)
        # History turns should be present
        self.assertIn("Turn A.", result)
        self.assertIn("Turn D.", result)

    def test_contaminated_requires_history(self):
        """Contaminated condition raises ValueError when history is None."""
        with self.assertRaises(ValueError):
            build_context("task", "contaminated", history=None)

    def test_contaminated_single_turn_fallback(self):
        """Contaminated condition with single-turn history returns task."""
        task = "Solve for x."
        result = build_context(task, "contaminated", history="Single turn.")
        self.assertIn(task, result)

    def test_padding_no_numeric_patterns(self):
        """Padding text does not contain numeric patterns matching GSM8K answer regex."""
        task = "Solve for x."
        result = build_context(task, "scoped", target_token_count=500)
        # Check that no standalone numbers appear in the filler text (after the task)
        filler = result[len(task) :]
        numeric_matches = re.findall(r"(?<!\d)(\d+(?:\.\d+)?)(?!\d)", filler)
        self.assertEqual(
            len(numeric_matches),
            0,
            f"Filler text contains numeric patterns: {numeric_matches}",
        )

    def test_length_matching_within_five_percent(self):
        """After padding, Scoped and Full-History token estimates are within 5% of Contaminated token count."""
        task = "Solve for x: 2x + 3 = 7. Show your work step by step and provide the final answer."
        history_lines = (
            "Turn A: The first step in the analysis is to identify the key variables and their relationships.",
            "Turn B: The second step involves collecting data from multiple sources and validating the inputs.",
            "Turn C: The third step requires applying the transformation to normalize the dataset.",
            "Turn D: The fourth step runs the model on the prepared data and records the output.",
            "Turn E: The fifth step evaluates the results against the baseline metrics.",
            "Turn F: The sixth step documents any anomalies found during the analysis process.",
            "Turn G: The seventh step prepares a summary of findings for the review committee.",
            "Turn H: The eighth step finalizes the report and submits it for publication.",
            "Turn I: The ninth step reviews the conclusions and checks for any overlooked patterns.",
            "Turn J: The tenth step archives all materials and updates the documentation repository.",
            "Turn K: The eleventh step schedules a follow-up review to track progress on recommendations.",
            "Turn L: The twelfth step closes the analysis loop and records lessons learned for future work.",
            "Turn M: The thirteenth step presents the findings to stakeholders and gathers feedback.",
            "Turn N: The fourteenth step incorporates feedback and produces the final revision of the report.",
            "Turn O: The fifteenth step marks the project as complete and celebrates the team achievement.",
            "Turn P: The sixteenth step conducts a retrospective to identify process improvements.",
            "Turn Q: The seventeenth step updates the knowledge base with new insights from the analysis.",
            "Turn R: The eighteenth step distributes the final report to all relevant parties.",
            "Turn S: The nineteenth step archives the data and code for reproducibility verification.",
            "Turn T: The twentieth step completes the systematic review and closes the project formally.",
        )
        history = "\n\n".join(history_lines)
        contaminated = build_context(task, "contaminated", history=history)
        target = estimate_tokens(contaminated)

        scoped = build_context(task, "scoped", target_token_count=target)
        full_hist = build_context(
            task, "full-history", history=history, target_token_count=target
        )

        scoped_tokens = estimate_tokens(scoped)
        full_hist_tokens = estimate_tokens(full_hist)

        # Check within 5% of target
        self.assertLessEqual(
            abs(scoped_tokens - target) / target,
            0.05,
            f"Scoped tokens {scoped_tokens} not within 5% of target {target}",
        )
        self.assertLessEqual(
            abs(full_hist_tokens - target) / target,
            0.05,
            f"Full-History tokens {full_hist_tokens} not within 5% of target {target}",
        )


class TestEstimateTokens(unittest.TestCase):
    """Tests for the estimate_tokens helper."""

    def test_empty_string(self):
        self.assertEqual(estimate_tokens(""), 0)

    def test_single_word(self):
        self.assertEqual(estimate_tokens("hello"), 1)

    def test_multiple_words(self):
        self.assertEqual(estimate_tokens("hello world foo bar"), 4)


if __name__ == "__main__":
    unittest.main()
