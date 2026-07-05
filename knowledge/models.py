"""Simplified models — Concept and KnowledgeGraph only."""

from __future__ import annotations

from pydantic import BaseModel, Field

__all__ = [
    "Concept",
    "KnowledgeGraph",
]


class Concept(BaseModel):
    """A section or concept extracted from a source document."""

    id: str = Field(description="Stable identifier (slug)")
    name: str = Field(description="Canonical name / heading text")
    description: str | None = Field(default=None, description="Section plain-text content")
    tags: list[str] = Field(default_factory=list, description="Category tags for grouping")


class KnowledgeGraph(BaseModel, frozen=True):
    """Container for a collection of concepts."""

    concepts: dict[str, Concept] = Field(default_factory=dict)

    def add_concept(self, concept: Concept) -> KnowledgeGraph:
        return self.model_copy(update={"concepts": {**self.concepts, concept.id: concept}})

    def remove_concept(self, concept_id: str) -> KnowledgeGraph:
        return self.model_copy(
            update={"concepts": {k: v for k, v in self.concepts.items() if k != concept_id}}
        )
