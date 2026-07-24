"""Unit tests for providers.py (mocked API calls)."""

import unittest
from unittest.mock import MagicMock, patch

from providers import call_bedrock


class TestCallBedrock(unittest.TestCase):
    """Tests for call_bedrock with mocked boto3 client."""

    def setUp(self):
        self.prompt = "What is the capital of France?"
        self.system = "You are a helpful assistant."
        self.model_id = "anthropic.claude-haiku-4-5-20251001-v1:0"
        self.config = {"max_tokens": 4096, "temperature": 0.5}

    def _mock_bedrock(self, return_value: dict) -> MagicMock:
        """Create a mock boto3 Session that returns a client with the given converse return value."""
        mock_client = MagicMock()
        mock_client.converse.return_value = return_value
        mock_session = MagicMock()
        mock_session.client.return_value = mock_client
        return mock_session

    def test_empty_content_list_returns_failure(self):
        """Bedrock Converse response with empty content list returns failure ChatResult."""
        mock_session = self._mock_bedrock(
            {
                "output": {"message": {"content": []}},
                "stopReason": "end_turn",
                "usage": {"inputTokens": 10, "outputTokens": 0},
            }
        )
        with patch("providers.boto3.Session", return_value=mock_session):
            result = call_bedrock(self.prompt, self.system, self.model_id, self.config)
        self.assertFalse(result.success)
        self.assertEqual(result.content, "")
        self.assertEqual(result.stop_reason, "end_turn")

    def test_content_filtered_is_failure(self):
        """Bedrock Converse response with stopReason='content_filtered' is marked as failure."""
        mock_session = self._mock_bedrock(
            {
                "output": {"message": {"content": [{"text": "I cannot answer that."}]}},
                "stopReason": "content_filtered",
                "usage": {"inputTokens": 10, "outputTokens": 5},
            }
        )
        with patch("providers.boto3.Session", return_value=mock_session):
            result = call_bedrock(self.prompt, self.system, self.model_id, self.config)
        self.assertFalse(result.success)
        self.assertEqual(result.content, "I cannot answer that.")
        self.assertEqual(result.stop_reason, "content_filtered")

    def test_max_tokens_is_failure(self):
        """Bedrock Converse response with stopReason='max_tokens' is marked as failure."""
        mock_session = self._mock_bedrock(
            {
                "output": {"message": {"content": [{"text": "Partial answer..."}]}},
                "stopReason": "max_tokens",
                "usage": {"inputTokens": 10, "outputTokens": 100},
            }
        )
        with patch("providers.boto3.Session", return_value=mock_session):
            result = call_bedrock(self.prompt, self.system, self.model_id, self.config)
        self.assertFalse(result.success)
        self.assertEqual(result.content, "Partial answer...")
        self.assertEqual(result.stop_reason, "max_tokens")

    def test_successful_response(self):
        """Bedrock Converse response with end_turn is marked as success."""
        mock_session = self._mock_bedrock(
            {
                "output": {"message": {"content": [{"text": "Paris"}]}},
                "stopReason": "end_turn",
                "usage": {"inputTokens": 10, "outputTokens": 5},
            }
        )
        with patch("providers.boto3.Session", return_value=mock_session):
            result = call_bedrock(self.prompt, self.system, self.model_id, self.config)
        self.assertTrue(result.success)
        self.assertEqual(result.content, "Paris")
        self.assertEqual(result.stop_reason, "end_turn")


if __name__ == "__main__":
    unittest.main()
