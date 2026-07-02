"""Reasoning provider interface for semantic verification.

The SDK should remain functional even when no reasoning provider is
configured. Deterministic fallbacks are preferred; reasoning engines
should only be introduced when semantic judgment is genuinely required.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class ReasoningResult:
    """The result of a reasoning operation.

    Contains a judgment about semantic correctness along with an
    explanation and optional suggested fixes.
    """

    is_valid: bool
    explanation: str
    confidence: float = 1.0
    suggestions: list[str] = field(default_factory=list)


class ReasoningProvider(ABC):
    """Abstract interface for semantic reasoning providers.

    Implementations may be deterministic (rule-based) or use AI models.
    The interface is kept intentionally small to support both approaches.
    """

    @abstractmethod
    def validate_consistency(
        self,
        statements: list[str],
        context: dict[str, Any] | None = None,
    ) -> ReasoningResult:
        """Check whether a set of statements is internally consistent.

        Args:
            statements: The statements to evaluate.
            context: Optional contextual information.

        Returns:
            A ReasoningResult indicating whether the statements are
            consistent and any suggested improvements.
        """
        ...

    @abstractmethod
    def validate_claim(
        self,
        claim: str,
        evidence: list[str],
        context: dict[str, Any] | None = None,
    ) -> ReasoningResult:
        """Check whether a claim is supported by the provided evidence.

        Args:
            claim: The claim to validate.
            evidence: Supporting evidence statements.
            context: Optional contextual information.

        Returns:
            A ReasoningResult indicating whether the claim is supported.
        """
        ...


class DeterministicReasoningProvider(ReasoningProvider):
    """A fully deterministic reasoning provider that uses rule-based checks.

    This is the default provider. It performs basic consistency and
    evidence checks without requiring any AI model.
    """

    def validate_consistency(
        self,
        statements: list[str],
        context: dict[str, Any] | None = None,
    ) -> ReasoningResult:
        contradictions: list[str] = []

        for i, s1 in enumerate(statements):
            for s2 in statements[i + 1:]:
                if self._are_contradictory(s1, s2):
                    contradictions.append(f"'{s1}' contradicts '{s2}'")

        if contradictions:
            return ReasoningResult(
                is_valid=False,
                explanation="; ".join(contradictions),
                confidence=0.9,
                suggestions=["Review the contradictory statements and resolve the conflict."],
            )
        return ReasoningResult(
            is_valid=True,
            explanation="All statements appear consistent.",
            confidence=0.8,
        )

    def validate_claim(
        self,
        claim: str,
        evidence: list[str],
        context: dict[str, Any] | None = None,
    ) -> ReasoningResult:
        if not evidence:
            return ReasoningResult(
                is_valid=False,
                explanation="No evidence provided to support the claim.",
                confidence=1.0,
                suggestions=["Add supporting evidence for this claim."],
            )

        claim_lower = claim.lower()
        claim_words = {w for w in claim_lower.split() if len(w) > 3}
        supporting = 0
        for ev in evidence:
            ev_lower = ev.lower()
            overlap = sum(1 for w in claim_words if w in ev_lower)
            if overlap >= 2:
                supporting += 1

        if supporting == 0:
            return ReasoningResult(
                is_valid=False,
                explanation=f"No evidence directly supports the claim: '{claim[:80]}...'",
                confidence=0.7,
                suggestions=["Add more specific evidence for this claim."],
            )

        return ReasoningResult(
            is_valid=True,
            explanation=f"Claim is supported by {supporting} of {len(evidence)} evidence sources.",
            confidence=min(0.5 + 0.1 * supporting, 1.0),
        )

    @staticmethod
    def _are_contradictory(s1: str, s2: str) -> bool:
        negativity_words = {"not", "no", "never", "cannot", "doesn't", "isn't", "won't", "don't"}
        s1_negative = any(w in s1.lower().split() for w in negativity_words)
        s2_negative = any(w in s2.lower().split() for w in negativity_words)

        if s1_negative != s2_negative:
            s1_clean = " ".join(w for w in s1.lower().split() if w not in negativity_words)
            s2_clean = " ".join(w for w in s2.lower().split() if w not in negativity_words)
            if s1_clean and s2_clean and s1_clean == s2_clean:
                return True
        return False
