"""Deterministic OKF Markdown serializer.

Converts a canonical KnowledgeGraph into an OKF Markdown document.
The serializer produces deterministic output — the same KnowledgeGraph
always produces the same Markdown.
"""

from __future__ import annotations

from typing import cast

from knowledge.models import (
    Concept,
    Entity,
    Evidence,
    Fact,
    KnowledgeGraph,
    Relationship,
    VerificationState,
)

OKF_HEADER = "# Open Knowledge Format"


class OKFSerializer:
    """Serializes a KnowledgeGraph into OKF Markdown.

    Elements are written in a fixed order: entities, concepts, facts,
    relationships, evidence. Within each group, elements are ordered by
    their stable identifier for reproducibility.
    """

    def serialize(self, graph: KnowledgeGraph) -> str:
        parts: list[str] = [OKF_HEADER, ""]

        for entity in sorted(graph.entities.values(), key=lambda e: e.id):
            parts.extend(self._serialize_entity(entity))
            parts.append("")

        for concept in sorted(graph.concepts.values(), key=lambda c: c.id):
            parts.extend(self._serialize_concept(concept))
            parts.append("")

        for fact in sorted(graph.facts.values(), key=lambda f: f.id):
            parts.extend(self._serialize_fact(fact))
            parts.append("")

        for rel in sorted(graph.relationships.values(), key=lambda r: r.id):
            parts.extend(self._serialize_relationship(rel))
            parts.append("")

        for ev in sorted(graph.evidence.values(), key=lambda e: e.id):
            parts.extend(self._serialize_evidence(ev))
            parts.append("")

        return "\n".join(parts).strip() + "\n"

    @staticmethod
    def _field(key: str, value: str) -> list[str]:
        if not value:
            return []
        first, *rest = value.split("\n")
        lines = [f"- **{key}**: {first}"]
        for line in rest:
            lines.append(f"  {line}")
        return lines

    @staticmethod
    def _confidence(value: float) -> str:
        if value == 0.0:
            return ""
        return f"{value:.2f}"

    @staticmethod
    def _verification(value: VerificationState) -> str:
        if value == VerificationState.PENDING:
            return ""
        return cast(str, value.value)

    @staticmethod
    def _list_string(items: list[str]) -> str:
        if not items:
            return ""
        return ", ".join(items)

    def _serialize_entity(self, entity: Entity) -> list[str]:
        lines = [f"## Entity: {entity.id}"]
        lines.extend(self._field("name", entity.name))
        lines.extend(self._field("aliases", self._list_string(entity.aliases)))
        lines.extend(self._field("description", entity.description or ""))
        lines.extend(self._field("confidence", self._confidence(entity.confidence)))
        lines.extend(self._field("verification", self._verification(entity.verification_state)))
        return [line for line in lines if line]

    def _serialize_concept(self, concept: Concept) -> list[str]:
        lines = [f"## Concept: {concept.id}"]
        lines.extend(self._field("name", concept.name))
        lines.extend(self._field("description", concept.description or ""))
        lines.extend(self._field("confidence", self._confidence(concept.confidence)))
        lines.extend(
            self._field(
                "verification",
                self._verification(concept.verification_state),
            )
        )
        return [line for line in lines if line]

    def _serialize_fact(self, fact: Fact) -> list[str]:
        lines = [f"## Fact: {fact.id}"]
        lines.extend(self._field("statement", fact.statement))
        lines.extend(self._field("evidence", self._list_string(fact.evidence_refs)))
        lines.extend(self._field("confidence", self._confidence(fact.confidence)))
        lines.extend(self._field("verification", self._verification(fact.verification_state)))
        return [line for line in lines if line]

    def _serialize_relationship(self, rel: Relationship) -> list[str]:
        lines = [f"## Relationship: {rel.id}"]
        lines.extend(self._field("source", rel.source_id))
        lines.extend(self._field("target", rel.target_id))
        lines.extend(self._field("type", rel.relationship_type))
        lines.extend(self._field("evidence", self._list_string(rel.evidence_refs)))
        lines.extend(self._field("confidence", self._confidence(rel.confidence)))
        lines.extend(
            self._field(
                "verification",
                self._verification(rel.verification_state),
            )
        )
        return [line for line in lines if line]

    def _serialize_evidence(self, evidence: Evidence) -> list[str]:
        lines = [f"## Evidence: {evidence.id}"]
        lines.extend(self._field("content", evidence.content))
        lines.extend(self._field("source", evidence.source))
        lines.extend(self._field("confidence", self._confidence(evidence.confidence)))
        lines.extend(
            self._field(
                "verification",
                self._verification(evidence.verification_state),
            )
        )
        return [line for line in lines if line]
