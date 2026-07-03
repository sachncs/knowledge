"""Relationship model — a typed connection between two knowledge elements."""

from pydantic import Field

from knowledge.models.base import KnowledgeModel


class Relationship(KnowledgeModel):
    """A typed connection between two knowledge elements.

    Relationships connect entities, concepts, or facts through a
    named relationship type such as "implements", "depends_on",
    "extends", "part_of", "uses", or "references".

    The source and target are identified by their stable identifiers.
    """

    source_id: str
    target_id: str
    relationship_type: str
    evidence_refs: list[str] = Field(default_factory=list)
