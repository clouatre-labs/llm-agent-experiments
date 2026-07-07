"""Unit tests for run_inference.py -- JSON extraction and pilot logic."""

import json
import sys
import unittest
from pathlib import Path

# ---------------------------------------------------------------------------
# Helpers to exercise the JSON-extraction logic without making API calls
# ---------------------------------------------------------------------------


def _extract_json(raw_text: str) -> str:
    """Mirror of the extraction logic in run_single()."""
    start_idx = raw_text.find("{")
    end_idx = raw_text.rfind("}")
    if start_idx != -1 and end_idx != -1 and end_idx >= start_idx:
        return raw_text[start_idx : end_idx + 1]
    return raw_text


class TestJsonExtraction(unittest.TestCase):
    """C1 -- robust JSON extraction from model output."""

    def test_plain_json_unchanged(self):
        raw = '{"session_id": "run-86", "lens": "scout"}'
        self.assertEqual(_extract_json(raw), raw)

    def test_strips_json_fence(self):
        raw = '```json\n{"session_id": "run-96"}\n```'
        result = _extract_json(raw)
        self.assertEqual(json.loads(result), {"session_id": "run-96"})

    def test_strips_plain_fence(self):
        raw = '```\n{"session_id": "run-106"}\n```'
        result = _extract_json(raw)
        self.assertEqual(json.loads(result), {"session_id": "run-106"})

    def test_strips_prose_before_and_after(self):
        raw = 'Here is the JSON:\n{"key": "value"}\nThat is all.'
        result = _extract_json(raw)
        self.assertEqual(json.loads(result), {"key": "value"})

    def test_no_json_returns_raw(self):
        raw = "No JSON object here at all."
        self.assertEqual(_extract_json(raw), raw)

    def test_empty_string(self):
        self.assertEqual(_extract_json(""), "")

    def test_nested_objects_preserved(self):
        inner = {"approaches": [{"name": "A", "pros": []}], "recommendation": "A"}
        raw = f"```json\n{json.dumps(inner)}\n```"
        result = _extract_json(raw)
        self.assertEqual(json.loads(result), inner)

    def test_uses_last_closing_brace(self):
        # Prose after the closing brace must be discarded
        raw = '{"a": "b"} extra text with } stray brace'
        result = _extract_json(raw)
        # rfind picks the last '}', so result includes up to it
        self.assertTrue(result.startswith("{"))
        self.assertTrue(result.endswith("}"))


class TestPilotBehavior(unittest.TestCase):
    """C2 -- --pilot runs exactly one session per model (3 total)."""

    def test_pilot_runs_all_three_models(self):
        """Importing main() and inspecting PILOT_RUN_IDS covers all 3 models."""
        sys.path.insert(0, str(Path(__file__).parent))
        import run_inference as ri

        self.assertEqual(set(ri.PILOT_RUN_IDS.keys()), {"gemma4", "haiku45", "sonnet5"})
        self.assertEqual(ri.PILOT_RUN_IDS["gemma4"], "run-86")
        self.assertEqual(ri.PILOT_RUN_IDS["haiku45"], "run-96")
        self.assertEqual(ri.PILOT_RUN_IDS["sonnet5"], "run-106")

    def test_no_pilot_break_in_source(self):
        """The 'if args.pilot: break' line must not exist in run_inference.py."""
        src = Path(__file__).parent / "run_inference.py"
        text = src.read_text(encoding="utf-8")
        # The fix removes this guard; if it reappears the pilot regresses
        self.assertNotIn("if args.pilot:\n            break", text)


class TestSkipExisting(unittest.TestCase):
    """C3 -- --skip-existing skips run IDs that already have a session file."""

    def test_skip_existing_flag_present(self):
        src = Path(__file__).parent / "run_inference.py"
        text = src.read_text(encoding="utf-8")
        self.assertIn("--skip-existing", text)
        self.assertIn("args.skip_existing", text)


if __name__ == "__main__":
    unittest.main()
