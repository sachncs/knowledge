"""Exception types for the knowledge SDK."""


class KnowledgeError(Exception):
    """Base exception for all knowledge SDK errors."""


class ParseError(KnowledgeError):
    """Raised when parsing an OKF document fails."""
