"""Exception types for the knowledge SDK."""


class KnowledgeError(Exception):
    """Base exception for all knowledge SDK errors."""


class ParseError(KnowledgeError):
    """Raised when parsing a KMD document fails."""


class UnsupportedSourceError(KnowledgeError):
    """Raised when a source type is not supported."""
