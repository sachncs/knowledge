"""Schema validation pass — checks structural integrity of knowledge elements."""

from __future__ import annotations

from typing import Any

from knowledge.models import KnowledgeGraph
from knowledge.passes.base import CompilerPass, PassResult, Phase
from knowledge.passes.diagnostics import Diagnostic, Severity


class SchemaValidationPass(CompilerPass):
    """Validates the schema of all knowledge elements.

    Checks: required fields, valid identifiers, metadata completeness,
    malformed structures, duplicate identifiers.
    """

    id = "verification.schema"
    phase = Phase.VERIFICATION
    version = "0.1.0"
    description = "Validate schema compliance of all knowledge elements"

    def execute(
        self,
        graph: KnowledgeGraph,
        config: dict[str, Any] | None = None,
    ) -> PassResult:
        """Validate schema compliance of all knowledge elements.

        Args:
            graph: The knowledge graph to validate.
            config: Optional configuration dictionary.

        Returns:
            PassResult with schema validation diagnostics.
        """
        diagnostics: list[Diagnostic] = []
        seen_ids: dict[str, str] = {}

        for eid, entity in graph.entities.items():
            self.check_id(eid, "entity", seen_ids, diagnostics)
            if not entity.name:
                diagnostics.append(
                    Diagnostic(
                        severity=Severity.ERROR,
                        message=f"Entity '{eid}' has empty name",
                        location=f"Entity: {eid}",
                        affected_objects=[eid],
                    )
                )

        for cid, concept in graph.concepts.items():
            self.check_id(cid, "concept", seen_ids, diagnostics)
            if not concept.name:
                diagnostics.append(
                    Diagnostic(
                        severity=Severity.ERROR,
                        message=f"Concept '{cid}' has empty name",
                        location=f"Concept: {cid}",
                        affected_objects=[cid],
                    )
                )

        for fid, fact in graph.facts.items():
            self.check_id(fid, "fact", seen_ids, diagnostics)
            if not fact.statement:
                diagnostics.append(
                    Diagnostic(
                        severity=Severity.ERROR,
                        message=f"Fact '{fid}' has empty statement",
                        location=f"Fact: {fid}",
                        affected_objects=[fid],
                    )
                )

        for rid, rel in graph.relationships.items():
            self.check_id(rid, "relationship", seen_ids, diagnostics)
            if not rel.source_id:
                diagnostics.append(
                    Diagnostic(
                        severity=Severity.ERROR,
                        message=f"Relationship '{rid}' has empty source_id",
                        location=f"Relationship: {rid}",
                        affected_objects=[rid],
                    )
                )
            if not rel.target_id:
                diagnostics.append(
                    Diagnostic(
                        severity=Severity.ERROR,
                        message=f"Relationship '{rid}' has empty target_id",
                        location=f"Relationship: {rid}",
                        affected_objects=[rid],
                    )
                )
            if not rel.relationship_type:
                diagnostics.append(
                    Diagnostic(
                        severity=Severity.ERROR,
                        message=f"Relationship '{rid}' has empty relationship_type",
                        location=f"Relationship: {rid}",
                        affected_objects=[rid],
                    )
                )

        for evid, ev in graph.evidence.items():
            self.check_id(evid, "evidence", seen_ids, diagnostics)
            if not ev.content:
                diagnostics.append(
                    Diagnostic(
                        severity=Severity.ERROR,
                        message=f"Evidence '{evid}' has empty content",
                        location=f"Evidence: {evid}",
                        affected_objects=[evid],
                    )
                )
            if not ev.source:
                diagnostics.append(
                    Diagnostic(
                        severity=Severity.WARNING,
                        message=f"Evidence '{evid}' has empty source",
                        location=f"Evidence: {evid}",
                        affected_objects=[evid],
                    )
                )

        return PassResult(graph=graph, diagnostics=diagnostics)

    @staticmethod
    def check_id(
        eid: str,
        kind: str,
        seen: dict[str, str],
        diagnostics: list[Diagnostic],
    ) -> None:
        """Validate an identifier for emptiness and uniqueness.

        Args:
            eid: The identifier to check.
            kind: Human-readable element type (e.g. "entity", "fact").
            seen: Map of previously seen ids to their element kinds.
            diagnostics: Accumulator for diagnostics.

        Returns:
            None
        """
        if not eid:
            diagnostics.append(
                Diagnostic(
                    severity=Severity.ERROR,
                    message=f"{kind.title()} has empty id",
                )
            )
        elif eid in seen:
            diagnostics.append(
                Diagnostic(
                    severity=Severity.ERROR,
                    message=f"Duplicate id '{eid}' used by {kind} and {seen[eid]}",
                    affected_objects=[eid],
                )
            )
        else:
            seen[eid] = kind
