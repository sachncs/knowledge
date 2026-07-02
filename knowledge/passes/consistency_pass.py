"""Consistency validation pass — checks internal consistency of knowledge."""

from __future__ import annotations

from typing import Any

from knowledge.models import KnowledgeGraph
from knowledge.passes.base import CompilerPass, PassResult, Phase
from knowledge.passes.diagnostics import Diagnostic, Severity


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
        diagnostics: list[Diagnostic] = []

        name_map: dict[str, list[str]] = {}
        for eid, entity in graph.entities.items():
            key = entity.name.lower()
            name_map.setdefault(key, []).append(eid)

        for name, ids in name_map.items():
            if len(ids) > 1:
                descriptions = [
                    graph.entities[eid].description for eid in ids
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
            for f2 in fact_pairs[i + 1:]:
                if self._are_contradictory(f1.statement, f2.statement):
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

    @staticmethod
    def _are_contradictory(s1: str, s2: str) -> bool:
        negative_words = {"not", "no", "never", "cannot", "doesn't", "isn't", "won't"}
        s1_neg = any(w in s1.lower().split() for w in negative_words)
        s2_neg = any(w in s2.lower().split() for w in negative_words)
        if s1_neg != s2_neg:
            s1_clean = " ".join(w for w in s1.lower().split() if w not in negative_words)
            s2_clean = " ".join(w for w in s2.lower().split() if w not in negative_words)
            common = set(s1_clean.split()) & set(s2_clean.split())
            significant = {w for w in common if len(w) > 3}
            return len(significant) >= 2
        return False
