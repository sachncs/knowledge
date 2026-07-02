"""Verification — semantic and structural validation of knowledge.

The verification module provides passes that evaluate knowledge quality,
check consistency, and validate semantic correctness.
"""

from knowledge.verification.reasoning import (
    ReasoningProvider,
    ReasoningResult,
)

__all__ = [
    "ReasoningProvider",
    "ReasoningResult",
]
