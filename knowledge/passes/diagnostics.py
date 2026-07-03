"""Diagnostics framework for compiler passes.

Every compiler pass emits diagnostics using this common API.
Diagnostics are structured, deterministic, and machine-readable.
"""

from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, Field


class Severity(StrEnum):
    """The severity level of a diagnostic.

    Severity levels help consumers filter and prioritize diagnostics:
    - Error:     Must be fixed; document cannot be considered valid.
    - Warning:   Should be reviewed; may indicate a problem.
    - Suggestion: Optional improvement; not required.
    - Information: Informational message; no action required.
    """

    ERROR = "error"
    WARNING = "warning"
    SUGGESTION = "suggestion"
    INFORMATION = "information"


class Diagnostic(BaseModel, frozen=True):
    """A structured message produced by a compiler pass.

    Every diagnostic includes at minimum a severity and a message.
    Optional fields provide additional context for automated or
    human review.
    """

    severity: Severity
    message: str
    explanation: str | None = None
    location: str | None = None
    affected_objects: list[str] = Field(default_factory=list)
    suggested_fix: str | None = None
