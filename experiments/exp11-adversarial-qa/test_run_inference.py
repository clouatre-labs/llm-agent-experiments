"""Unit tests for run_inference.py (mocked API calls)."""

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from run_inference import main


class TestMainPilotGate(unittest.TestCase):
    """Tests for main() pilot gate logic."""

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.sessions_dir = Path(self.temp_dir.name) / "sessions"
        self.results_dir = Path(self.temp_dir.name) / "results"
        self.sessions_dir.mkdir(parents=True)
        self.results_dir.mkdir(parents=True)

    def tearDown(self):
        self.temp_dir.cleanup()

    def _write_session(self, condition: str, run_id: str, correct: bool) -> None:
        """Write a mock session file."""
        cond_dir = self.sessions_dir / condition
        cond_dir.mkdir(parents=True, exist_ok=True)
        with open(cond_dir / f"{run_id}.json", "w") as f:
            json.dump(
                {
                    "run_id": run_id,
                    "condition": condition,
                    "task_id": run_id.replace("run-", "task-"),
                    "correct": correct,
                    "response_text": "Paris",
                    "gold_answer": "Paris",
                    "answer": {
                        "normalized_value": "Paris",
                        "normalized_aliases": ["Paris"],
                    },
                },
                f,
            )

    @patch("run_inference.call_openrouter")
    @patch("run_inference.load_triviaqa_sample")
    def test_pilot_gate_stops_when_gap_below_8pp(self, mock_load, mock_call_openrouter):
        """Computes contaminated-vs-scoped accuracy gap and exits with stop message when gap < 8pp."""
        # Create pre-existing sessions for comparison
        for i in range(5):
            self._write_session("scoped", f"run-{i:03d}", True)
        for i in range(5):
            self._write_session("contaminated", f"run-{i:03d}", True)

        mock_load.return_value = [
            {
                "question": "What is the capital of France?",
                "answer": {
                    "normalized_value": "Paris",
                    "normalized_aliases": ["Paris"],
                },
                "gold_answer": "Paris",
                "task_id": f"task-{i:04d}",
            }
            for i in range(5)
        ]
        mock_call_openrouter.return_value = MagicMock(
            content="Paris",
            input_tokens=10,
            output_tokens=5,
            stop_reason="end_turn",
            success=True,
        )

        with (
            patch("run_inference.EXP11_DIR", Path(self.temp_dir.name)),
            patch(
                "sys.argv",
                ["run_inference.py", "--pilot", "--condition", "contaminated"],
            ),
            patch("builtins.print") as mock_print,
        ):
            main()
            printed = " ".join(
                str(a) for call in mock_print.call_args_list for a in call.args
            )
            self.assertIn("STOP", printed, "Expected STOP message in pilot gate output")

    @patch("run_inference.call_openrouter")
    @patch("run_inference.load_triviaqa_sample")
    def test_pilot_gate_proceeds_when_gap_above_8pp(
        self, mock_load, mock_call_openrouter
    ):
        """Proceeds to full scale when gap >= 8pp."""
        # Create pre-existing sessions for comparison
        for i in range(5):
            self._write_session("scoped", f"run-{i:03d}", True)
        for i in range(5):
            self._write_session("contaminated", f"run-{i:03d}", False)

        mock_load.return_value = [
            {
                "question": "What is the capital of France?",
                "answer": {
                    "normalized_value": "Paris",
                    "normalized_aliases": ["Paris"],
                },
                "gold_answer": "Paris",
                "task_id": f"task-{i:04d}",
            }
            for i in range(5)
        ]
        # Mock returns a wrong answer so contaminated run records correct=False
        mock_call_openrouter.return_value = MagicMock(
            content="London",
            input_tokens=10,
            output_tokens=5,
            stop_reason="end_turn",
            success=True,
        )

        with (
            patch("run_inference.EXP11_DIR", Path(self.temp_dir.name)),
            patch(
                "sys.argv",
                ["run_inference.py", "--pilot", "--condition", "contaminated"],
            ),
            patch("builtins.print") as mock_print,
        ):
            main()
            printed = " ".join(
                str(a) for call in mock_print.call_args_list for a in call.args
            )
            self.assertIn(
                "PROCEED", printed, "Expected PROCEED message in pilot gate output"
            )


if __name__ == "__main__":
    unittest.main()
