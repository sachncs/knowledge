"""Exception types for the knowledge SDK."""


class KnowledgeError(Exception):
    """Base exception for all knowledge SDK errors."""


class ParseError(KnowledgeError):
    """Raised when parsing an OKF document fails."""


class SchemaValidationError(KnowledgeError):
    """Raised when an OKF document fails schema validation."""


class SemanticValidationError(KnowledgeError):
    """Raised when an OKF document fails semantic validation."""


class VerificationError(KnowledgeError):
    """Raised when verification fails critically."""


class MergeConflictError(KnowledgeError):
    """Raised when a merge operation encounters unresolvable conflicts."""


class UnsupportedSourceError(KnowledgeError):
    """Raised when a source type is not supported."""
