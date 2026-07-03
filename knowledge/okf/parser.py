"""Deterministic OKF Markdown parser.

Converts OKF Markdown documents into the canonical KnowledgeGraph
representation. Every element type (Entity, Concept, Fact, Relationship,
Evidence) is identified by its section heading and parsed into the
corresponding model.
"""

from __future__ import annotations

import re
from typing import Any, cast

from knowledge.exceptions import ParseError
from knowledge.models import (
    Concept,
    Entity,
    Evidence,
    Fact,
    KnowledgeGraph,
    Metadata,
    Provenance,
    Relationship,
    VerificationState,
)

SECTION_PATTERN = re.compile(r"^## (\w+):\s*(.*)")
FIELD_LINE_PATTERN = re.compile(r"^- \*\*([^*]+)\*\*:\s*(.*)")


class OKFParser:
    """Parses OKF Markdown content into a KnowledgeGraph.

    The parser is fully deterministic. Given the same input, it always
    produces the same output. No semantic reasoning is performed during
    parsing.
    """

    def parse(self, content: str) -> KnowledgeGraph:
        """Parse OKF Markdown content into a KnowledgeGraph.

        Args:
            content: The OKF Markdown string to parse.

        Returns:
            A fully populated KnowledgeGraph.
        """
        lines = content.split("\n")
        sections = self.extract_sections(lines)
        graph = KnowledgeGraph()
        for section_lines, section_type, element_id in sections:
            fields = self.parse_fields(section_lines)
            element = self.build_element(section_type, element_id, fields)
            graph = self.add_to_graph(graph, element)
        return graph

    def extract_sections(self, lines: list[str]) -> list[tuple[list[str], str, str]]:
        """Split lines into sections identified by ``##`` headings.

        Args:
            lines: The file content split into individual lines.

        Returns:
            A list of ``(section_lines, section_type, element_id)`` tuples.
        """
        sections: list[tuple[list[str], str, str]] = []
        current_lines: list[str] = []
        current_type = ""
        current_id = ""

        for line in lines:
            m = SECTION_PATTERN.match(line)
            if m:
                if current_type:
                    sections.append((current_lines, current_type, current_id))
                current_type = m.group(1).lower()
                current_id = m.group(2).strip()
                current_lines = []
            elif current_type:
                current_lines.append(line)

        if current_type:
            sections.append((current_lines, current_type, current_id))

        return sections

    def parse_fields(self, lines: list[str]) -> dict[str, str]:
        """Parse field lines into a key-value dictionary.

        Supports multi-line values via indented continuation lines.

        Args:
            lines: The lines belonging to a single section (excluding the heading).

        Returns:
            A dictionary mapping field names to their string values.
        """
        fields: dict[str, str] = {}
        current_key = ""
        current_values: list[str] = []

        for line in lines:
            m = FIELD_LINE_PATTERN.match(line)
            if m:
                if current_key:
                    fields[current_key] = "\n".join(current_values)
                current_key = m.group(1)
                current_values = [m.group(2)]
            elif current_key and line.startswith("  "):
                stripped = line.strip()
                if stripped:
                    current_values.append(stripped)

        if current_key:
            fields[current_key] = "\n".join(current_values)

        return fields

    def build_element(
        self, section_type: str, element_id: str, fields: dict[str, str]
    ) -> Entity | Concept | Fact | Relationship | Evidence:
        """Build a knowledge graph element from parsed fields.

        Dispatches to the appropriate builder function based on section type.

        Args:
            section_type: The element type (entity, concept, fact, relationship, evidence).
            element_id: The unique identifier for the element.
            fields: The parsed field dictionary.

        Returns:
            The constructed element instance.

        Raises:
            ParseError: If the section type is unknown.
        """
        builder = BUILDERS.get(section_type)
        if builder is None:
            raise ParseError(f"Unknown section type: {section_type}")
        return cast(
            Entity | Concept | Fact | Relationship | Evidence,
            builder(element_id, fields),
        )

    def add_to_graph(
        self,
        graph: KnowledgeGraph,
        element: Entity | Concept | Fact | Relationship | Evidence,
    ) -> KnowledgeGraph:
        """Add an element to the graph using the correct type-specific method.

        Args:
            graph: The graph to add to.
            element: The element to add.

        Returns:
            The graph with the element added (may be a new copy).
        """
        if isinstance(element, Entity):
            return graph.add_entity(element)
        if isinstance(element, Concept):
            return graph.add_concept(element)
        if isinstance(element, Fact):
            return graph.add_fact(element)
        if isinstance(element, Relationship):
            return graph.add_relationship(element)
        if isinstance(element, Evidence):
            return graph.add_evidence(element)
        return graph

    @staticmethod
    def parse_confidence(value: str | None) -> float:
        """Parse a confidence string into a clamped float.

        Args:
            value: The confidence string (e.g. ``"0.85"``) or ``None``.

        Returns:
            A float between 0.0 and 1.0. Returns ``0.0`` if input is
            ``None`` or invalid.
        """
        if value is None or value == "":
            return 0.0
        try:
            return max(0.0, min(1.0, float(value)))
        except ValueError:
            return 0.0

    @staticmethod
    def parse_verification(value: str | None) -> VerificationState:
        """Parse a verification string into a ``VerificationState``.

        Args:
            value: The verification state string (e.g. ``"verified"``,
                ``"pending"``) or ``None``.

        Returns:
            The corresponding ``VerificationState``. Defaults to
            ``PENDING`` on invalid input.
        """
        if value is None or value == "":
            return VerificationState.PENDING
        try:
            return VerificationState(value.lower())
        except ValueError:
            return VerificationState.PENDING

    @staticmethod
    def parse_list(value: str | None) -> list[str]:
        """Parse a comma-separated string into a list of trimmed strings.

        Args:
            value: A comma-separated string or ``None``.

        Returns:
            A list of non-empty trimmed strings. Returns an empty list if
            input is ``None`` or empty.
        """
        if value is None or value == "":
            return []
        return [item.strip() for item in value.split(",") if item.strip()]


def parse_provenance(fields: dict[str, str]) -> Provenance | None:
    """Extract a ``Provenance`` object from parsed fields.

    Args:
        fields: The parsed field dictionary.

    Returns:
        A ``Provenance`` instance if ``provenance_source`` is present,
        otherwise ``None``.
    """
    source_id = fields.get("provenance_source")
    if not source_id:
        return None
    return Provenance(
        source_id=source_id,
        extractor=fields.get("provenance_extractor", "unknown"),
        verification_cycle=fields.get("provenance_cycle"),
    )


def parse_metadata(fields: dict[str, str]) -> Metadata:
    """Extract a ``Metadata`` object from parsed fields.

    Args:
        fields: The parsed field dictionary.

    Returns:
        A ``Metadata`` instance with tags and version populated.
    """
    return Metadata(
        tags=OKFParser.parse_list(fields.get("tags")),
        version=int(fields["version"]) if "version" in fields and fields["version"].strip() else 1,
    )


def build_entity(element_id: str, fields: dict[str, str]) -> Entity:
    """Build an ``Entity`` from parsed fields.

    Args:
        element_id: The entity identifier.
        fields: The parsed field dictionary.

    Returns:
        A new ``Entity`` instance.
    """
    return Entity(
        id=element_id,
        name=fields.get("name", ""),
        aliases=OKFParser.parse_list(fields.get("aliases")),
        description=fields.get("description"),
        confidence=OKFParser.parse_confidence(fields.get("confidence")),
        verification_state=OKFParser.parse_verification(fields.get("verification")),
        provenance=parse_provenance(fields),
        metadata=parse_metadata(fields),
    )


def build_concept(element_id: str, fields: dict[str, str]) -> Concept:
    """Build a ``Concept`` from parsed fields.

    Args:
        element_id: The concept identifier.
        fields: The parsed field dictionary.

    Returns:
        A new ``Concept`` instance.
    """
    return Concept(
        id=element_id,
        name=fields.get("name", ""),
        description=fields.get("description"),
        confidence=OKFParser.parse_confidence(fields.get("confidence")),
        verification_state=OKFParser.parse_verification(fields.get("verification")),
        provenance=parse_provenance(fields),
        metadata=parse_metadata(fields),
    )


def build_fact(element_id: str, fields: dict[str, str]) -> Fact:
    """Build a ``Fact`` from parsed fields.

    Args:
        element_id: The fact identifier.
        fields: The parsed field dictionary.

    Returns:
        A new ``Fact`` instance.
    """
    return Fact(
        id=element_id,
        statement=fields.get("statement", ""),
        evidence_refs=OKFParser.parse_list(fields.get("evidence")),
        confidence=OKFParser.parse_confidence(fields.get("confidence")),
        verification_state=OKFParser.parse_verification(fields.get("verification")),
        provenance=parse_provenance(fields),
        metadata=parse_metadata(fields),
    )


def build_relationship(element_id: str, fields: dict[str, str]) -> Relationship:
    """Build a ``Relationship`` from parsed fields.

    Args:
        element_id: The relationship identifier.
        fields: The parsed field dictionary.

    Returns:
        A new ``Relationship`` instance.
    """
    return Relationship(
        id=element_id,
        source_id=fields.get("source", ""),
        target_id=fields.get("target", ""),
        relationship_type=fields.get("type", ""),
        evidence_refs=OKFParser.parse_list(fields.get("evidence")),
        confidence=OKFParser.parse_confidence(fields.get("confidence")),
        verification_state=OKFParser.parse_verification(fields.get("verification")),
        provenance=parse_provenance(fields),
        metadata=parse_metadata(fields),
    )


def build_evidence(element_id: str, fields: dict[str, str]) -> Evidence:
    """Build an ``Evidence`` from parsed fields.

    Args:
        element_id: The evidence identifier.
        fields: The parsed field dictionary.

    Returns:
        A new ``Evidence`` instance.
    """
    return Evidence(
        id=element_id,
        content=fields.get("content", ""),
        source=fields.get("source", ""),
        confidence=OKFParser.parse_confidence(fields.get("confidence")),
        verification_state=OKFParser.parse_verification(fields.get("verification")),
        provenance=parse_provenance(fields),
        metadata=parse_metadata(fields),
    )


BUILDERS: dict[str, Any] = {
    "entity": build_entity,
    "concept": build_concept,
    "fact": build_fact,
    "relationship": build_relationship,
    "evidence": build_evidence,
}
