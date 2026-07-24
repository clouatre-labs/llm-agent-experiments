"""Unit tests for gsm8k.py (pure logic, no API calls)."""

import unittest

from gsm8k import extract_gold_answer, extract_predicted_answer


class TestExtractGoldAnswer(unittest.TestCase):
    """Tests for extract_gold_answer."""

    def test_extracts_from_hash_format(self):
        """Extracts numeric answer from '#### 42' format in GSM8K gold solutions."""
        text = "The answer is 42. #### 42"
        self.assertEqual(extract_gold_answer(text), "42")

    def test_extracts_decimal(self):
        """Extracts decimal answer from '#### 3.14' format."""
        text = "The result is 3.14. #### 3.14"
        self.assertEqual(extract_gold_answer(text), "3.14")

    def test_extracts_with_commas(self):
        """Extracts answer with commas stripped."""
        text = "The total is 1,000. #### 1,000"
        self.assertEqual(extract_gold_answer(text), "1000")

    def test_no_hash_returns_empty(self):
        """Returns empty string when no '#### N' pattern is found."""
        text = "The answer is 42."
        self.assertEqual(extract_gold_answer(text), "")

    def test_empty_string(self):
        """Returns empty string for empty input."""
        self.assertEqual(extract_gold_answer(""), "")


class TestExtractPredictedAnswer(unittest.TestCase):
    """Tests for extract_predicted_answer."""

    def test_extracts_last_integer(self):
        """Extracts last standalone integer/decimal from model output text."""
        text = "Step 1: Add 2 and 3 to get 5. Step 2: Multiply by 4 to get 20. The answer is 20."
        self.assertEqual(extract_predicted_answer(text), "20")

    def test_extracts_last_decimal(self):
        """Extracts last standalone decimal number."""
        text = "The result is approximately 3.14159."
        self.assertEqual(extract_predicted_answer(text), "3.14159")

    def test_single_number(self):
        """Extracts the only number in the text."""
        text = "42"
        self.assertEqual(extract_predicted_answer(text), "42")

    def test_no_numbers_returns_empty(self):
        """Model output with no numeric answer returns empty/falsy result."""
        text = "The answer cannot be determined from the given information."
        self.assertEqual(extract_predicted_answer(text), "")

    def test_empty_string(self):
        """Returns empty string for empty input."""
        self.assertEqual(extract_predicted_answer(text=""), "")

    def test_ignores_numbers_in_words(self):
        """Does not match numbers embedded in words."""
        text = "The 1st item costs 5 dollars."
        self.assertEqual(extract_predicted_answer(text), "5")

    def test_negative_number(self):
        """Minus signs are intentionally stripped by extract_predicted_answer.

        The function extracts the last standalone integer/decimal, dropping the
        sign. A negative temperature of -5 is extracted as "5" because the regex
        matches the absolute value only.
        """
        text = "The temperature dropped to -5 degrees."
        self.assertEqual(extract_predicted_answer(text), "5")


if __name__ == "__main__":
    unittest.main()
