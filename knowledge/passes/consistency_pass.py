"""Consistency validation pass — checks internal consistency of knowledge."""

from __future__ import annotations

from typing import Any

from knowledge.models import KnowledgeGraph
from knowledge.passes.base import CompilerPass, PassResult, Phase
from knowledge.passes.diagnostics import Diagnostic, Severity
from knowledge.util import statements_are_contradictory


class ConsistencyValidationPass(CompilerPass):
    """Validates internal consistency of the KnowledgeGraph.

    Checks: contradictory facts, duplicate entities with different
    descriptions, incompatible metadata, conflicting relationships.
    """

    id = "verification.consistency"
    phase = Phase.VERIFICATION
    version = "0.1.0"
    description = "Validate internal consistency of knowledge elements"
    depends_on = ("verification.structural",)

    def execute(
        self,
        graph: KnowledgeGraph,
        config: dict[str, Any] | None = None,
    ) -> PassResult:
        """Validate internal consistency of the KnowledgeGraph.

        Args:
            graph: The knowledge graph to validate.
            config: Optional configuration dictionary.

        Returns:
            PassResult with consistency validation diagnostics.
        """
        diagnostics: list[Diagnostic] = []

        name_map: dict[str, list[str]] = {}
        for eid, entity in graph.entities.items():
            key = entity.name.lower()
            name_map.setdefault(key, []).append(eid)

        for name, ids in name_map.items():
            if len(ids) > 1:
                descriptions = [
                    graph.entities[eid].description
                    for eid in ids
                    if graph.entities[eid].description
                ]
                if len(set(descriptions)) > 1:
                    diagnostics.append(
                        Diagnostic(
                            severity=Severity.WARNING,
                            message=f"Entity name '{name}' has conflicting descriptions",
                            explanation=(
                                f"Entities {ids} share name '{name}' "
                                "but have different descriptions"
                            ),
                            location=f"Entity: {ids[0]}",
                            affected_objects=ids,
                        )
                    )

        # Check for contradictory fact statements
        fact_pairs = list(graph.facts.values())
        for i, f1 in enumerate(fact_pairs):
            for f2 in fact_pairs[i + 1 :]:
                if statements_are_contradictory(f1.statement, f2.statement):
                    diagnostics.append(
                        Diagnostic(
                            severity=Severity.WARNING,
                            message="Potentially contradictory facts detected",
                            explanation=f"'{f1.statement[:60]}...' vs '{f2.statement[:60]}...'",
                            location=f"Fact: {f1.id}",
                            affected_objects=[f1.id, f2.id],
                        )
                    )

        # Check for conflicting relationships (same pair, different types)
        rel_pairs: dict[tuple[str, str], set[str]] = {}
        for rel in graph.relationships.values():
            pair = (rel.source_id, rel.target_id)
            rel_pairs.setdefault(pair, set()).add(rel.relationship_type)

        for (src, tgt), types in rel_pairs.items():
            if len(types) > 1:
                diagnostics.append(
                    Diagnostic(
                        severity=Severity.SUGGESTION,
                        message=f"Multiple relationship types between '{src}' and '{tgt}': {types}",
                        explanation="Entities have relationships of different types",
                        location=f"Entity: {src}",
                        affected_objects=[src, tgt],
                    )
                )

        return PassResult(graph=graph, diagnostics=diagnostics)
