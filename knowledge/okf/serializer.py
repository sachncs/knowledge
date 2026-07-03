"""Deterministic OKF Markdown serializer.

Converts a canonical KnowledgeGraph into an OKF Markdown document.
The serializer produces deterministic output — the same KnowledgeGraph
always produces the same Markdown.

Provenance and metadata fields are serialized when present.
"""

from __future__ import annotations

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
        """Serialize a ``KnowledgeGraph`` into OKF Markdown.

        Args:
            graph: The knowledge graph to serialize.

        Returns:
            A deterministic OKF Markdown string.
        """
        parts: list[str] = [OKF_HEADER, ""]

        for entity in sorted(graph.entities.values(), key=lambda e: e.id):
            parts.extend(self.serialize_entity(entity))
            parts.append("")

        for concept in sorted(graph.concepts.values(), key=lambda c: c.id):
            parts.extend(self.serialize_concept(concept))
            parts.append("")

        for fact in sorted(graph.facts.values(), key=lambda f: f.id):
            parts.extend(self.serialize_fact(fact))
            parts.append("")

        for rel in sorted(graph.relationships.values(), key=lambda r: r.id):
            parts.extend(self.serialize_relationship(rel))
            parts.append("")

        for ev in sorted(graph.evidence.values(), key=lambda e: e.id):
            parts.extend(self.serialize_evidence(ev))
            parts.append("")

        return "\n".join(parts).strip() + "\n"

    @staticmethod
    def field(key: str, value: str) -> list[str]:
        """Format a single key-value field as Markdown list lines.

        Supports multi-line values by splitting on newlines.

        Args:
            key: The field name.
            value: The field value (may contain newlines).

        Returns:
            A list of Markdown lines for the field. Empty if value is empty.
        """
        if not value:
            return []
        first, *rest = value.split("\n")
        lines = [f"- **{key}**: {first}"]
        for line in rest:
            lines.append(f"  {line}")
        return lines

    @staticmethod
    def confidence(value: float) -> str:
        """Format a confidence value as a string.

        Args:
            value: The confidence float (``0.0`` to ``1.0``).

        Returns:
            A formatted string (e.g. ``"0.85"``), or empty string if ``0.0``.
        """
        if value == 0.0:
            return ""
        return f"{value:.2f}"

    @staticmethod
    def verification(value: VerificationState) -> str:
        """Format a ``VerificationState`` as a string.

        Args:
            value: The verification state.

        Returns:
            The state value string, or empty string if ``PENDING``.
        """
        if value == VerificationState.PENDING:
            return ""
        return value.value

    @staticmethod
    def list_string(items: list[str]) -> str:
        """Join a list of strings into a comma-separated string.

        Args:
            items: The list of strings.

        Returns:
            A comma-separated string, or empty string if the list is empty.
        """
        if not items:
            return ""
        return ", ".join(items)

    @staticmethod
    def provenance_fields(entity: Entity | Concept | Fact | Relationship | Evidence) -> list[str]:
        """Serialize provenance sub-fields for an element.

        Args:
            entity: The knowledge graph element with optional provenance.

        Returns:
            A list of Markdown lines for provenance fields.
        """
        lines: list[str] = []
        if entity.provenance:
            lines.extend(OKFSerializer.field("provenance_source", entity.provenance.source_id))
            lines.extend(OKFSerializer.field("provenance_extractor", entity.provenance.extractor))
            if entity.provenance.verification_cycle:
                lines.extend(
                    OKFSerializer.field("provenance_cycle", entity.provenance.verification_cycle)
                )
        return [line for line in lines if line]

    @staticmethod
    def metadata_fields(
        entity: Entity | Concept | Fact | Relationship | Evidence,
    ) -> list[str]:
        """Serialize metadata sub-fields for an element.

        Args:
            entity: The knowledge graph element with optional metadata.

        Returns:
            A list of Markdown lines for metadata fields.
        """
        lines: list[str] = []
        if entity.metadata:
            if entity.metadata.tags:
                lines.extend(
                    OKFSerializer.field("tags", OKFSerializer.list_string(entity.metadata.tags))
                )
            if entity.metadata.version != 1:
                lines.extend(OKFSerializer.field("version", str(entity.metadata.version)))
        return [line for line in lines if line]

    def serialize_entity(self, entity: Entity) -> list[str]:
        """Serialize an ``Entity`` into Markdown lines.

        Args:
            entity: The entity to serialize.

        Returns:
            A list of Markdown lines.
        """
        lines = [f"## Entity: {entity.id}"]
        lines.extend(self.field("name", entity.name))
        lines.extend(self.field("aliases", self.list_string(entity.aliases)))
        lines.extend(self.field("description", entity.description or ""))
        lines.extend(self.field("confidence", self.confidence(entity.confidence)))
        lines.extend(self.field("verification", self.verification(entity.verification_state)))
        lines.extend(self.provenance_fields(entity))
        lines.extend(self.metadata_fields(entity))
        return [line for line in lines if line]

    def serialize_concept(self, concept: Concept) -> list[str]:
        """Serialize a ``Concept`` into Markdown lines.

        Args:
            concept: The concept to serialize.

        Returns:
            A list of Markdown lines.
        """
        lines = [f"## Concept: {concept.id}"]
        lines.extend(self.field("name", concept.name))
        lines.extend(self.field("description", concept.description or ""))
        lines.extend(self.field("confidence", self.confidence(concept.confidence)))
        lines.extend(
            self.field(
                "verification",
                self.verification(concept.verification_state),
            )
        )
        lines.extend(self.provenance_fields(concept))
        lines.extend(self.metadata_fields(concept))
        return [line for line in lines if line]

    def serialize_fact(self, fact: Fact) -> list[str]:
        """Serialize a ``Fact`` into Markdown lines.

        Args:
            fact: The fact to serialize.

        Returns:
            A list of Markdown lines.
        """
        lines = [f"## Fact: {fact.id}"]
        lines.extend(self.field("statement", fact.statement))
        lines.extend(self.field("evidence", self.list_string(fact.evidence_refs)))
        lines.extend(self.field("confidence", self.confidence(fact.confidence)))
        lines.extend(self.field("verification", self.verification(fact.verification_state)))
        lines.extend(self.provenance_fields(fact))
        lines.extend(self.metadata_fields(fact))
        return [line for line in lines if line]

    def serialize_relationship(self, rel: Relationship) -> list[str]:
        """Serialize a ``Relationship`` into Markdown lines.

        Args:
            rel: The relationship to serialize.

        Returns:
            A list of Markdown lines.
        """
        lines = [f"## Relationship: {rel.id}"]
        lines.extend(self.field("source", rel.source_id))
        lines.extend(self.field("target", rel.target_id))
        lines.extend(self.field("type", rel.relationship_type))
        lines.extend(self.field("evidence", self.list_string(rel.evidence_refs)))
        lines.extend(self.field("confidence", self.confidence(rel.confidence)))
        lines.extend(
            self.field(
                "verification",
                self.verification(rel.verification_state),
            )
        )
        lines.extend(self.provenance_fields(rel))
        lines.extend(self.metadata_fields(rel))
        return [line for line in lines if line]

    def serialize_evidence(self, evidence: Evidence) -> list[str]:
        """Serialize an ``Evidence`` into Markdown lines.

        Args:
            evidence: The evidence to serialize.

        Returns:
            A list of Markdown lines.
        """
        lines = [f"## Evidence: {evidence.id}"]
        lines.extend(self.field("content", evidence.content))
        lines.extend(self.field("source", evidence.source))
        lines.extend(self.field("confidence", self.confidence(evidence.confidence)))
        lines.extend(
            self.field(
                "verification",
                self.verification(evidence.verification_state),
            )
        )
        lines.extend(self.provenance_fields(evidence))
        lines.extend(self.metadata_fields(evidence))
        return [line for line in lines if line]
