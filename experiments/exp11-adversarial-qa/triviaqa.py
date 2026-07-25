"""TriviaQA dataset loading and answer extraction utilities."""

from pathlib import Path

import datasets

EXP11_DIR = Path(__file__).parent


def load_triviaqa_sample(seed: int = 42, n: int = 300) -> list[dict]:
    """Load a fixed-seed sample of n tasks from the TriviaQA Wikipedia test split.

    Returns a list of dicts with keys 'question', 'answer' (the full answer dict),
    'gold_answer' (normalized value string), and 'task_id' (unique identifier).
    """
    ds = datasets.load_dataset("mandarjoshi/trivia_qa", "rc.wikipedia", split="validation")
    shuffled = ds.shuffle(seed=seed)
    selected = shuffled.select(range(min(n, len(shuffled))))
    results = []
    for i, row in enumerate(selected):
        answer = row["answer"]
        gold = extract_gold_answer(answer)
        results.append(
            {
                "question": row["question"],
                "answer": answer,
                "gold_answer": gold,
                "task_id": f"task-{i:04d}",
            }
        )
    return results


def extract_gold_answer(answer: dict) -> str:
    """Extract the gold answer from a TriviaQA answer dict.

    Uses answer.normalized_value as the primary key, falling back to
    the first entry in normalized_aliases if normalized_value is empty.
    """
    if answer.get("normalized_value", "").strip():
        return answer["normalized_value"].strip()
    aliases = answer.get("normalized_aliases", [])
    if aliases and aliases[0].strip():
        return aliases[0].strip()
    return ""


def extract_predicted_answer(text: str) -> str:
    """Extract the predicted answer from model output.

    Returns the cleaned text, stripped of whitespace and punctuation.
    """
    text = text.strip()
    # Remove leading/trailing punctuation
    text = text.strip(".,!?;:\"'")
    return text.strip()


def _normalize_response(text: str) -> str:
    """Strip markdown formatting and normalize whitespace for matching."""
    import re
    # Remove bold/italic markers
    text = re.sub(r"\*+([^*]+)\*+", r"\1", text)
    # Remove other markdown (headers, backticks)
    text = re.sub(r"[`#]", "", text)
    return text.lower().strip()


def is_correct(predicted: str, answer: dict) -> bool:
    """Check if the predicted answer matches any normalized alias.

    Strips markdown formatting, then checks whether any normalized alias
    appears as a substring of the response (standard TriviaQA eval approach).
    """
    normalized = _normalize_response(predicted)
    candidates = []
    nv = answer.get("normalized_value", "").strip().lower()
    if nv:
        candidates.append(nv)
    for alias in answer.get("normalized_aliases", []):
        a = alias.strip().lower()
        if a:
            candidates.append(a)
    for candidate in candidates:
        if candidate in normalized:
            return True
    return False
