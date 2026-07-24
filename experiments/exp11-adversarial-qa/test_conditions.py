"""Unit tests for conditions.py (pure logic, no API calls)."""

import unittest

from conditions import build_context, estimate_tokens


class TestBuildContext(unittest.TestCase):
    """Tests for build_context."""

    def test_scoped_returns_only_task(self):
        """Scoped condition returns only the passage as context when no target tokens."""
        task = "What is the capital of France?"
        result = build_context(task, "scoped")
        self.assertEqual(result, task)

    def test_contaminated_prepends_synthetic_turns(self):
        """Contaminated condition prepends 2-3 synthetic prior-session turns before the passage."""
        task = "What is the capital of France?"
        history = "Turn A.\n\nTurn B.\n\nTurn C.\n\nTurn D."
        result = build_context(task, "contaminated", history=history)
        # Task should appear in the middle, not at the start or end
        self.assertIn(task, result)
        self.assertIn("Turn A.", result)
        self.assertIn("Turn D.", result)
        # Task should not be at the very start
        self.assertFalse(result.startswith(task))

    def test_full_history_includes_all_prior_turns(self):
        """Full-history condition includes all prior session turns verbatim before the passage."""
        task = "What is the capital of France?"
        history = "Turn A.\n\nTurn B.\n\nTurn C."
        result = build_context(task, "full-history", history=history)
        self.assertTrue(result.startswith("Turn A."))
        self.assertIn("Turn B.", result)
        self.assertIn("Turn C.", result)
        self.assertIn(task, result)
        # Task should be at the end
        self.assertTrue(result.endswith(task))

    def test_scoped_requires_no_history(self):
        """Scoped condition works without history."""
        result = build_context("task", "scoped")
        self.assertEqual(result, "task")

    def test_contaminated_requires_history(self):
        """Contaminated condition raises ValueError when history is None."""
        with self.assertRaises(ValueError):
            build_context("task", "contaminated", history=None)

    def test_full_history_requires_history(self):
        """Full-history condition raises ValueError when history is None."""
        with self.assertRaises(ValueError):
            build_context("task", "full-history", history=None)

    def test_contaminated_single_turn_fallback(self):
        """Contaminated condition with single-turn history returns task."""
        task = "What is the capital of France?"
        result = build_context(task, "contaminated", history="Single turn.")
        self.assertIn(task, result)

    def test_unknown_condition_raises(self):
        """Unknown condition raises ValueError."""
        with self.assertRaises(ValueError):
            build_context("task", "invalid")  # type: ignore[arg-type]


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
