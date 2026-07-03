"""Fact model — a statement supported by evidence."""

from pydantic import Field

from knowledge.models.base import KnowledgeModel


class Fact(KnowledgeModel):
    """A statement supported by evidence.

    Facts represent verifiable claims derived from source material.
    Every fact should have supporting evidence referenced through
    evidence reference identifiers.

    A fact should never exist without provenance, though this is
    enforced by convention rather than by the model itself.
    """

    statement: str
    evidence_refs: list[str] = Field(default_factory=list)
