"""Structured exceptions for the SDK."""


class KnowledgeError(Exception):
    """Base exception for all SDK errors."""


class FetchError(KnowledgeError):
    """Raised when a source cannot be fetched (network error, file not found)."""


class ValidationError(KnowledgeError):
    """Raised when bundle validation fails."""
