"""Context window builders and length-matching padding for the three conditions.

Conditions:
  - Scoped: Only the current task prompt, no history.
  - Full-History: Complete planner transcript verbatim prepended to the task.
  - Contaminated: Task injected at a controlled middle position among distractor
    turns (simulating context contamination).

Token count uses a whitespace-split approximation. This is documented as
approximate -- it is not equivalent to tiktoken or Claude's internal tokenizer.
"""

import math
import random
from typing import Literal

Condition = Literal["scoped", "full-history", "contaminated"]

# Padding filler text: lorem-style prose with no numeric patterns.
# Must not contain any digits or numeric sequences to avoid false-positive
# GSM8K answer extraction.
_FILLER_SENTENCES = [
    "The quick brown fox jumps over the lazy dog near the riverbank.",
    "A systematic review of the literature reveals several important patterns in the data.",
    "Researchers have long debated the implications of these findings for future work.",
    "The methodology employed in this study follows established best practices in the field.",
    "It is important to consider the broader context when interpreting these results.",
    "Further analysis is needed to confirm the validity of these observations.",
    "The experimental design was carefully constructed to minimize potential sources of bias.",
    "These findings contribute to a growing body of evidence supporting the hypothesis.",
    "A thorough examination of the underlying assumptions reveals several key insights.",
    "The implications of this work extend beyond the immediate scope of the investigation.",
    "Previous studies have documented similar patterns across different experimental conditions.",
    "The theoretical framework provides a solid foundation for interpreting these observations.",
    "Careful consideration of alternative explanations strengthens the overall argument.",
    "The data suggest a complex interplay between multiple factors that warrant further study.",
    "This approach offers a novel perspective on a long-standing question in the field.",
    "The results are consistent with predictions derived from the theoretical model.",
    "Future research should explore the generalizability of these findings to other domains.",
    "A comprehensive analysis of the available evidence supports the proposed interpretation.",
    "The methodological choices were guided by principles of transparency and reproducibility.",
    "These observations raise important questions about the underlying mechanisms at play.",
]


def estimate_tokens(text: str) -> int:
    """Estimate token count using whitespace-split approximation.

    NOTE: This is a rough approximation. Claude models use a subword tokenizer
    (similar to tiktoken) that may produce different counts. This estimate is
    suitable for length-matching purposes but should not be treated as exact.
    """
    return len(text.split())


def _build_filler(target_tokens: int, rng: random.Random) -> str:
    """Build filler text of approximately target_tokens tokens with no numeric patterns."""
    words_per_sentence = len(_FILLER_SENTENCES[0].split())
    sentences_needed = math.ceil(target_tokens / words_per_sentence)
    filler_sentences = [
        _FILLER_SENTENCES[i % len(_FILLER_SENTENCES)] for i in range(sentences_needed)
    ]
    rng.shuffle(filler_sentences)
    return " ".join(filler_sentences)


def build_context(
    task: str,
    condition: Condition,
    history: str | None = None,
    target_token_count: int | None = None,
    seed: int = 42,
) -> str:
    """Build the context window for the given condition.

    Args:
        task: The current task/question prompt.
        condition: One of 'scoped', 'full-history', 'contaminated'.
        history: Full planner transcript (required for full-history and contaminated).
        target_token_count: Target token count for length-matching padding
            (used for scoped and full-history to match contaminated length).
        seed: Random seed for reproducible padding and distractor ordering.

    Returns:
        The constructed context string.
    """
    rng = random.Random(seed)

    if condition == "scoped":
        context = task
        if target_token_count is not None:
            current_tokens = estimate_tokens(context)
            if current_tokens < target_token_count:
                padding = _build_filler(target_token_count - current_tokens, rng)
                context = context + "\n\n" + padding
        return context

    if condition == "full-history":
        if history is None:
            raise ValueError("history is required for full-history condition")
        context = history + "\n\n" + task
        if target_token_count is not None:
            current_tokens = estimate_tokens(context)
            if current_tokens < target_token_count:
                padding = _build_filler(target_token_count - current_tokens, rng)
                context = context + "\n\n" + padding
        return context

    if condition == "contaminated":
        if history is None:
            raise ValueError("history is required for contaminated condition")
        # Split history into turns (paragraphs)
        turns = [t.strip() for t in history.split("\n\n") if t.strip()]
        if not turns:
            return task
        # Inject task at a controlled middle position
        mid = len(turns) // 2
        contaminated_turns = turns[:mid] + [task] + turns[mid:]
        context = "\n\n".join(contaminated_turns)
        if target_token_count is not None:
            current_tokens = estimate_tokens(context)
            if current_tokens < target_token_count:
                padding = _build_filler(target_token_count - current_tokens, rng)
                context = context + "\n\n" + padding
        return context

    raise ValueError(f"Unknown condition: {condition}")
