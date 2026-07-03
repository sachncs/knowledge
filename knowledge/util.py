"""Shared utility functions for the knowledge SDK."""

from __future__ import annotations

NEGATION_WORDS: frozenset[str] = frozenset(
    {
        "not",
        "no",
        "never",
        "cannot",
        "doesn't",
        "isn't",
        "won't",
        "don't",
    }
)
"""Words that negate a statement, used for contradiction detection."""


def statements_are_contradictory(s1: str, s2: str) -> bool:
    """Check if two natural language statements contradict each other.

    Uses negation analysis: if one statement uses negation words and the
    other doesn't, and the remaining content is semantically similar
    (exact match or significant word overlap), they are contradictory.
    """
    s1_neg = any(w in s1.lower().split() for w in NEGATION_WORDS)
    s2_neg = any(w in s2.lower().split() for w in NEGATION_WORDS)

    if s1_neg == s2_neg:
        return False

    s1_clean = " ".join(w for w in s1.lower().split() if w not in NEGATION_WORDS)
    s2_clean = " ".join(w for w in s2.lower().split() if w not in NEGATION_WORDS)

    if s1_clean and s2_clean and s1_clean == s2_clean:
        return True

    common = set(s1_clean.split()) & set(s2_clean.split())
    significant = {w for w in common if len(w) > 3}
    return len(significant) >= 2
