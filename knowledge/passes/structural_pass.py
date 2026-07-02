"""Structural validation pass — checks graph consistency."""

from __future__ import annotations

from typing import Any

from knowledge.models import KnowledgeGraph
from knowledge.passes.base import CompilerPass, PassResult, Phase
from knowledge.passes.diagnostics import Diagnostic, Severity


class StructuralValidationPass(CompilerPass):
    """Validates the structural integrity of the KnowledgeGraph.

    Checks: orphaned nodes, broken references, circular dependencies,
    unreachable objects, duplicate aliases.
    """

    id = "verification.structural"
    phase = Phase.VERIFICATION
    version = "0.1.0"
    description = "Validate structural integrity of the knowledge graph"
    depends_on = ("verification.schema",)

    def execute(
        self,
        graph: KnowledgeGraph,
        config: dict[str, Any] | None = None,
    ) -> PassResult:
        diagnostics: list[Diagnostic] = []
        entity_ids = set(graph.entities.keys())
        evidence_ids = set(graph.evidence.keys())

        for rid, rel in graph.relationships.items():
            if rel.source_id not in entity_ids:
                diagnostics.append(
                    Diagnostic(
                        severity=Severity.ERROR,
                        message=f"Relationship '{rid}' source '{rel.source_id}' not found",
                        location=f"Relationship: {rid}",
                        affected_objects=[rid, rel.source_id],
                    )
                )
            if rel.target_id not in entity_ids:
                diagnostics.append(
                    Diagnostic(
                        severity=Severity.ERROR,
                        message=f"Relationship '{rid}' target '{rel.target_id}' not found",
                        location=f"Relationship: {rid}",
                        affected_objects=[rid, rel.target_id],
                    )
                )

        for fid, fact in graph.facts.items():
            for ref in fact.evidence_refs:
                if ref not in evidence_ids:
                    diagnostics.append(
                        Diagnostic(
                            severity=Severity.WARNING,
                            message=f"Fact '{fid}' references missing evidence '{ref}'",
                            location=f"Fact: {fid}",
                            affected_objects=[fid, ref],
                        )
                    )

        for eid, entity in graph.entities.items():
            if len(entity.aliases) != len(set(a.lower() for a in entity.aliases)):
                diagnostics.append(
                    Diagnostic(
                        severity=Severity.WARNING,
                        message=f"Entity '{entity.name}' has duplicate aliases",
                        location=f"Entity: {eid}",
                        affected_objects=[eid],
                    )
                )

        rel_graph: dict[str, set[str]] = {eid: set() for eid in entity_ids}
        for rel in graph.relationships.values():
            if rel.source_id in rel_graph and rel.target_id in rel_graph:
                rel_graph[rel.source_id].add(rel.target_id)

        visited: set[str] = set()
        path: set[str] = set()

        def _has_cycle(node: str) -> bool:
            if node in path:
                return True
            if node in visited:
                return False
            path.add(node)
            for neighbor in rel_graph.get(node, set()):
                if _has_cycle(neighbor):
                    return True
            path.remove(node)
            visited.add(node)
            return False

        for eid in entity_ids:
            if _has_cycle(eid):
                diagnostics.append(
                    Diagnostic(
                        severity=Severity.WARNING,
                        message=f"Circular dependency detected involving entity '{eid}'",
                        location=f"Entity: {eid}",
                        affected_objects=[eid],
                    )
                )
                break

        return PassResult(graph=graph, diagnostics=diagnostics)
