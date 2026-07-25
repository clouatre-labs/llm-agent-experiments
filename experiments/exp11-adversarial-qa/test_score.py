"""Unit tests for score.py (pure logic, no API calls)."""

import json
import tempfile
import unittest
from pathlib import Path

from score import compute_scores, read_session_files


class TestComputeScores(unittest.TestCase):
    """Tests for compute_scores."""

    def test_aligns_by_task_id_key(self):
        """Aligns paired records by task_id key, not positional zip, to handle missing tasks gracefully."""
        records = [
            {
                "run_id": "run-001",
                "_condition": "scoped",
                "task_id": "task-001",
                "gold_answer": "Paris",
                "answer": {
                    "normalized_value": "Paris",
                    "normalized_aliases": ["Paris"],
                },
                "response_text": "Paris",
            },
            {
                "run_id": "run-002",
                "_condition": "scoped",
                "task_id": "task-002",
                "gold_answer": "London",
                "answer": {
                    "normalized_value": "London",
                    "normalized_aliases": ["London"],
                },
                "response_text": "London",
            },
            {
                "run_id": "run-003",
                "_condition": "contaminated",
                "task_id": "task-001",
                "gold_answer": "Paris",
                "answer": {
                    "normalized_value": "Paris",
                    "normalized_aliases": ["Paris"],
                },
                "response_text": "London",
            },
            # task-003 only exists in contaminated (missing from scoped)
            {
                "run_id": "run-004",
                "_condition": "contaminated",
                "task_id": "task-003",
                "gold_answer": "Berlin",
                "answer": {
                    "normalized_value": "Berlin",
                    "normalized_aliases": ["Berlin"],
                },
                "response_text": "Berlin",
            },
        ]
        scores = compute_scores(records)
        self.assertEqual(len(scores), 4)

        # Build lookup by task_id
        scoped_scores = {s["task_id"]: s for s in scores if s["condition"] == "scoped"}
        cont_scores = {
            s["task_id"]: s for s in scores if s["condition"] == "contaminated"
        }

        # task-001 should be in both
        self.assertIn("task-001", scoped_scores)
        self.assertIn("task-001", cont_scores)

        # task-002 should only be in scoped
        self.assertIn("task-002", scoped_scores)
        self.assertNotIn("task-002", cont_scores)

        # task-003 should only be in contaminated
        self.assertNotIn("task-003", scoped_scores)
        self.assertIn("task-003", cont_scores)

    def test_correctness_scoring(self):
        """Scores correct=1 when predicted matches gold, 0 otherwise."""
        records = [
            {
                "run_id": "run-001",
                "_condition": "scoped",
                "task_id": "task-001",
                "gold_answer": "Paris",
                "answer": {
                    "normalized_value": "Paris",
                    "normalized_aliases": ["Paris"],
                },
                "response_text": "Paris",
            },
            {
                "run_id": "run-002",
                "_condition": "scoped",
                "task_id": "task-002",
                "gold_answer": "London",
                "answer": {
                    "normalized_value": "London",
                    "normalized_aliases": ["London"],
                },
                "response_text": "Berlin",
            },
        ]
        scores = compute_scores(records)
        self.assertEqual(scores[0]["correct"], 1)
        self.assertEqual(scores[1]["correct"], 0)


class TestReadSessionFiles(unittest.TestCase):
    """Tests for read_session_files."""

    def test_reads_condition_subdirectories(self):
        """Reads session JSON files from condition subdirectories."""
        with tempfile.TemporaryDirectory() as tmpdir:
            sessions_dir = Path(tmpdir)
            scoped_dir = sessions_dir / "scoped"
            scoped_dir.mkdir()
            cont_dir = sessions_dir / "contaminated"
            cont_dir.mkdir()

            with open(scoped_dir / "run-001.json", "w") as f:
                json.dump({"task_id": "task-001", "response_text": "Paris"}, f)
            with open(cont_dir / "run-001.json", "w") as f:
                json.dump({"task_id": "task-001", "response_text": "London"}, f)

            records = read_session_files(sessions_dir)
            self.assertEqual(len(records), 2)
            conditions = {r["_condition"] for r in records}
            self.assertEqual(conditions, {"scoped", "contaminated"})


if __name__ == "__main__":
    unittest.main()
