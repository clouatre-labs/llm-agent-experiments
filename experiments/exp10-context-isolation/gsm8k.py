"""GSM8K dataset loading and answer extraction utilities."""

import re
from pathlib import Path

import datasets

EXP10_DIR = Path(__file__).parent


def load_gsm8k_sample(seed: int = 42, n: int = 300) -> list[dict]:
    """Load a fixed-seed sample of n tasks from the GSM8K test split.

    Returns a list of dicts with keys 'question' and 'answer' (gold solution).
    """
    ds = datasets.load_dataset("openai/gsm8k", "main", split="test")
    shuffled = ds.shuffle(seed=seed)
    selected = shuffled.select(range(min(n, len(shuffled))))
    return [{"question": row["question"], "answer": row["answer"]} for row in selected]


def extract_gold_answer(text: str) -> str:
    """Extract the numeric answer from a GSM8K gold solution string.

    GSM8K gold answers follow the pattern '#### N' where N is the answer.
    Returns the matched number as a string, or an empty string if not found.
    """
    match = re.search(r"####\s*([\d.,]+)", text)
    if match:
        return match.group(1).replace(",", "")
    return ""


def extract_predicted_answer(text: str) -> str:
    """Extract the last standalone integer or decimal from model output.

    Returns the matched number as a string, or an empty string if no number found.
    """
    matches = re.findall(r"(?<!\d)(\d+(?:\.\d+)?)(?!\d)", text)
    if matches:
        return matches[-1]
    return ""
