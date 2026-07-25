"""Unit tests for wrong_answer.py (pure logic, no API calls)."""

import random
import unittest

from wrong_answer import generate_wrong_answer


class TestGenerateWrongAnswer(unittest.TestCase):
    """Tests for generate_wrong_answer."""

    def setUp(self):
        self.rng = random.Random(42)
        self.dataset = [
            {
                "answer": {
                    "normalized_value": "Paris",
                    "normalized_aliases": ["Paris"],
                    "type": "city",
                }
            },
            {
                "answer": {
                    "normalized_value": "London",
                    "normalized_aliases": ["London"],
                    "type": "city",
                }
            },
            {
                "answer": {
                    "normalized_value": "42",
                    "normalized_aliases": ["42"],
                    "type": "number",
                }
            },
        ]

    def test_same_category_not_equal_to_gold(self):
        """Generated wrong answer is not equal to gold answer and belongs to same category."""
        result = generate_wrong_answer(
            gold_answer="Paris",
            answer_type="city",
            dataset=self.dataset,
            rng=self.rng,
        )
        self.assertNotEqual(result.lower(), "paris")
        # Should return London (same city category)
        self.assertEqual(result, "London")

    def test_falls_back_to_random_when_type_empty(self):
        """Falls back to random sampling when answer.type is empty or None."""
        result = generate_wrong_answer(
            gold_answer="Paris",
            answer_type=None,
            dataset=self.dataset,
            rng=self.rng,
        )
        self.assertNotEqual(result.lower(), "paris")
        # Should return a non-gold answer from the dataset
        self.assertIn(result, ["London", "42"])

    def test_excludes_gold_answer(self):
        """Always excludes gold answer from wrong-answer candidates."""
        dataset = [
            {
                "answer": {
                    "normalized_value": "Paris",
                    "normalized_aliases": ["Paris"],
                    "type": "city",
                }
            }
        ]
        # With only one entry, no candidates should exist
        result = generate_wrong_answer(
            gold_answer="Paris",
            answer_type="city",
            dataset=dataset,
            rng=self.rng,
        )
        self.assertEqual(result, "unknown")

    def test_empty_type_string(self):
        """Falls back to random when answer.type is empty string."""
        result = generate_wrong_answer(
            gold_answer="Paris",
            answer_type="",
            dataset=self.dataset,
            rng=self.rng,
        )
        self.assertNotEqual(result.lower(), "paris")


if __name__ == "__main__":
    unittest.main()
