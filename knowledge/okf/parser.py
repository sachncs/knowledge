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
        lines = content.split("\n")
        sections = self._extract_sections(lines)
        graph = KnowledgeGraph()
        for section_lines, section_type, element_id in sections:
            fields = self._parse_fields(section_lines)
            element = self._build_element(section_type, element_id, fields)
            graph = self._add_to_graph(graph, element)
        return graph

    def _extract_sections(self, lines: list[str]) -> list[tuple[list[str], str, str]]:
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

    def _parse_fields(self, lines: list[str]) -> dict[str, str]:
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

    def _build_element(
        self, section_type: str, element_id: str, fields: dict[str, str]
    ) -> Entity | Concept | Fact | Relationship | Evidence:
        builder = _BUILDERS.get(section_type)
        if builder is None:
            raise ParseError(f"Unknown section type: {section_type}")
        return cast(
            Entity | Concept | Fact | Relationship | Evidence,
            builder(element_id, fields),
        )

    def _add_to_graph(
        self,
        graph: KnowledgeGraph,
        element: Entity | Concept | Fact | Relationship | Evidence,
    ) -> KnowledgeGraph:
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
    def _parse_confidence(value: str | None) -> float:
        if value is None or value == "":
            return 0.0
        try:
            return max(0.0, min(1.0, float(value)))
        except ValueError:
            return 0.0

    @staticmethod
    def _parse_verification(value: str | None) -> VerificationState:
        if value is None or value == "":
            return VerificationState.PENDING
        try:
            return VerificationState(value.lower())
        except ValueError:
            return VerificationState.PENDING

    @staticmethod
    def _parse_list(value: str | None) -> list[str]:
        if value is None or value == "":
            return []
        return [item.strip() for item in value.split(",") if item.strip()]


def _build_entity(element_id: str, fields: dict[str, str]) -> Entity:
    return Entity(
        id=element_id,
        name=fields.get("name", ""),
        aliases=OKFParser._parse_list(fields.get("aliases")),
        description=fields.get("description"),
        confidence=OKFParser._parse_confidence(fields.get("confidence")),
        verification_state=OKFParser._parse_verification(fields.get("verification")),
    )


def _build_concept(element_id: str, fields: dict[str, str]) -> Concept:
    return Concept(
        id=element_id,
        name=fields.get("name", ""),
        description=fields.get("description"),
        confidence=OKFParser._parse_confidence(fields.get("confidence")),
        verification_state=OKFParser._parse_verification(fields.get("verification")),
    )


def _build_fact(element_id: str, fields: dict[str, str]) -> Fact:
    return Fact(
        id=element_id,
        statement=fields.get("statement", ""),
        evidence_refs=OKFParser._parse_list(fields.get("evidence")),
        confidence=OKFParser._parse_confidence(fields.get("confidence")),
        verification_state=OKFParser._parse_verification(fields.get("verification")),
    )


def _build_relationship(element_id: str, fields: dict[str, str]) -> Relationship:
    return Relationship(
        id=element_id,
        source_id=fields.get("source", ""),
        target_id=fields.get("target", ""),
        relationship_type=fields.get("type", ""),
        evidence_refs=OKFParser._parse_list(fields.get("evidence")),
        confidence=OKFParser._parse_confidence(fields.get("confidence")),
        verification_state=OKFParser._parse_verification(fields.get("verification")),
    )


def _build_evidence(element_id: str, fields: dict[str, str]) -> Evidence:
    return Evidence(
        id=element_id,
        content=fields.get("content", ""),
        source=fields.get("source", ""),
        confidence=OKFParser._parse_confidence(fields.get("confidence")),
        verification_state=OKFParser._parse_verification(fields.get("verification")),
    )


_BUILDERS: dict[str, Any] = {
    "entity": _build_entity,
    "concept": _build_concept,
    "fact": _build_fact,
    "relationship": _build_relationship,
    "evidence": _build_evidence,
}
