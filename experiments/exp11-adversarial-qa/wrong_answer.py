"""Wrong answer generation for adversarial context contamination.

Generates plausible-but-incorrect answers from the same category
as the gold answer, for use in contaminated condition history.
"""

import random


def generate_wrong_answer(
    gold_answer: str,
    answer_type: str | None,
    dataset: list[dict],
    rng: random.Random,
) -> str:
    """Generate a wrong answer that belongs to the same category as the gold answer.

    Category-matches by answer.type when available. Falls back to random
    sampling from the dataset when type is empty or None.
    Always excludes the gold answer from candidates.

    Args:
        gold_answer: The correct answer string to avoid.
        answer_type: The answer type/category (may be None or empty).
        dataset: Full list of task dicts with 'answer' keys.
        rng: Seeded random number generator for reproducibility.

    Returns:
        A wrong answer string from the same category.
    """
    candidates: list[str] = []

    if answer_type and answer_type.strip():
        # Try to find same-category answers
        for task in dataset:
            task_answer = task.get("answer", {})
            task_type = task_answer.get("type", "")
            if task_type and task_type.strip() == answer_type.strip():
                task_gold = (
                    task_answer.get("normalized_value", "")
                    or (task_answer.get("normalized_aliases", [""])[0])
                )
                if (
                    task_gold
                    and task_gold.strip().lower() != gold_answer.strip().lower()
                ):
                    candidates.append(task_gold.strip())

    # Fall back to random sampling if no same-category candidates found
    if not candidates:
        for task in dataset:
            task_answer = task.get("answer", {})
            task_gold = (
                task_answer.get("normalized_value", "")
                or (task_answer.get("normalized_aliases", [""])[0])
            )
            if task_gold and task_gold.strip().lower() != gold_answer.strip().lower():
                candidates.append(task_gold.strip())

    if not candidates:
        return "unknown"

    return rng.choice(candidates)
