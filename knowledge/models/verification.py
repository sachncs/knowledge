"""Verification state enum for knowledge elements."""

from enum import StrEnum


class VerificationState(StrEnum):
    """Represents the verification status of a knowledge element.

    Each knowledge element tracks its own verification state independently,
    allowing downstream systems to reason about knowledge quality at
    the element level rather than the document level.
    """

    PENDING = "pending"
    VERIFIED = "verified"
    INFERRED = "inferred"
    DEPRECATED = "deprecated"
    CONFLICTED = "conflicted"
