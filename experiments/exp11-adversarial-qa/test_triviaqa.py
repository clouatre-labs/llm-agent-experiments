"""Unit tests for triviaqa.py (pure logic, no API calls)."""

import unittest

from triviaqa import extract_gold_answer, extract_predicted_answer, is_correct


class TestExtractGoldAnswer(unittest.TestCase):
    """Tests for extract_gold_answer."""

    def test_uses_normalized_value(self):
        """Returns answer.normalized_value when available."""
        answer = {
            "normalized_value": "Paris",
            "normalized_aliases": ["Paris", "City of Light"],
        }
        self.assertEqual(extract_gold_answer(answer), "Paris")

    def test_falls_back_to_first_alias(self):
        """Falls back to first normalized_aliases entry when normalized_value is empty."""
        answer = {
            "normalized_value": "",
            "normalized_aliases": ["London", "Londinium"],
        }
        self.assertEqual(extract_gold_answer(answer), "London")

    def test_both_empty_returns_empty(self):
        """Returns empty string when both normalized_value and aliases are empty."""
        answer = {"normalized_value": "", "normalized_aliases": []}
        self.assertEqual(extract_gold_answer(answer), "")

    def test_normalized_value_with_spaces(self):
        """Strips whitespace from normalized_value."""
        answer = {
            "normalized_value": "  New York  ",
            "normalized_aliases": ["New York"],
        }
        self.assertEqual(extract_gold_answer(answer), "New York")


class TestExtractPredictedAnswer(unittest.TestCase):
    """Tests for extract_predicted_answer."""

    def test_strips_whitespace(self):
        """Extracts predicted answer by stripping whitespace."""
        self.assertEqual(extract_predicted_answer("  Paris  "), "Paris")

    def test_strips_punctuation(self):
        """Strips trailing punctuation from predicted answer."""
        self.assertEqual(extract_predicted_answer("Paris."), "Paris")

    def test_multiple_punctuation(self):
        """Strips multiple punctuation marks."""
        self.assertEqual(extract_predicted_answer("Paris!?"), "Paris")

    def test_empty_string(self):
        """Returns empty string for empty input."""
        self.assertEqual(extract_predicted_answer(""), "")

    def test_only_punctuation(self):
        """Returns empty string for punctuation-only input."""
        self.assertEqual(extract_predicted_answer(".,!?"), "")


class TestIsCorrect(unittest.TestCase):
    """Tests for is_correct."""

    def test_matches_normalized_value(self):
        """Returns True when predicted matches normalized_value case-insensitively."""
        answer = {
            "normalized_value": "Paris",
            "normalized_aliases": ["Paris", "City of Light"],
        }
        self.assertTrue(is_correct("paris", answer))

    def test_matches_alias(self):
        """Returns True when predicted matches a normalized_alias."""
        answer = {
            "normalized_value": "Paris",
            "normalized_aliases": ["Paris", "City of Light"],
        }
        self.assertTrue(is_correct("city of light", answer))

    def test_no_match_returns_false(self):
        """Returns False when predicted matches no alias."""
        answer = {
            "normalized_value": "Paris",
            "normalized_aliases": ["Paris", "City of Light"],
        }
        self.assertFalse(is_correct("London", answer))

    def test_case_insensitive(self):
        """Matching is case-insensitive."""
        answer = {
            "normalized_value": "New York",
            "normalized_aliases": ["New York", "NYC"],
        }
        self.assertTrue(is_correct("new york", answer))
        self.assertTrue(is_correct("nyc", answer))


if __name__ == "__main__":
    unittest.main()
