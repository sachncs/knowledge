"""Scoring passes — compute document quality metrics."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel

from knowledge.models import KnowledgeGraph
from knowledge.passes.base import CompilerPass, PassResult, Phase
from knowledge.passes.diagnostics import Diagnostic, Severity


class KnowledgeScore(BaseModel, frozen=True):
    """Quality scores for a KnowledgeGraph."""

    overall: float = 0.0
    completeness: float = 0.0
    consistency: float = 0.0
    evidence_quality: float = 0.0
    ontology_quality: float = 0.0
    metadata_completeness: float = 0.0


class ScoringPass(CompilerPass):
    """Computes quality scores for the KnowledgeGraph.

    Evaluates completeness, consistency, evidence quality,
    ontology quality, and metadata completeness.
    """

    id = "scoring.quality"
    phase = Phase.SCORING
    version = "0.1.0"
    description = "Compute quality scores for the knowledge graph"

    def execute(
        self,
        graph: KnowledgeGraph,
        config: dict[str, Any] | None = None,
    ) -> PassResult:
        score = self._compute_score(graph)
        diag = Diagnostic(
            severity=Severity.INFORMATION,
            message=(
                f"Quality score: overall={score.overall:.1f}%, "
                f"completeness={score.completeness:.1f}%, "
                f"consistency={score.consistency:.1f}%, "
                f"evidence={score.evidence_quality:.1f}%, "
                f"ontology={score.ontology_quality:.1f}%, "
                f"metadata={score.metadata_completeness:.1f}%"
            ),
            location="scoring.quality",
        )
        return PassResult(graph=graph, diagnostics=[diag])

    def _compute_score(self, graph: KnowledgeGraph) -> KnowledgeScore:
        total_elements = (
            len(graph.entities) + len(graph.concepts) + len(graph.facts)
            + len(graph.relationships) + len(graph.evidence)
        )
        if total_elements == 0:
            return KnowledgeScore()

        completeness = self._score_completeness(graph, total_elements)
        consistency = self._score_consistency(graph, total_elements)
        evidence_quality = self._score_evidence(graph, total_elements)
        ontology_quality = self._score_ontology(graph, total_elements)
        metadata = self._score_metadata(graph, total_elements)

        overall = (
            completeness * 0.25 + consistency * 0.25
            + evidence_quality * 0.20 + ontology_quality * 0.15
            + metadata * 0.15
        )

        return KnowledgeScore(
            overall=round(overall, 1),
            completeness=round(completeness, 1),
            consistency=round(consistency, 1),
            evidence_quality=round(evidence_quality, 1),
            ontology_quality=round(ontology_quality, 1),
            metadata_completeness=round(metadata, 1),
        )

    @staticmethod
    def _score_completeness(graph: KnowledgeGraph, total: int) -> float:
        has_description = sum(1 for e in graph.entities.values() if e.description)
        has_statement = sum(1 for f in graph.facts.values() if f.statement)
        return (
            (has_description + has_statement) / max(total, 1)
        ) * 100.0

    @staticmethod
    def _score_consistency(graph: KnowledgeGraph, total: int) -> float:
        # Check for name conflicts
        names = [e.name.lower() for e in graph.entities.values()]
        unique_names = len(set(names))
        if len(names) <= 1:
            name_score = 100.0
        else:
            name_score = (unique_names / len(names)) * 100.0

        type_map: dict[tuple[str, str], int] = {}
        for rel in graph.relationships.values():
            key = (rel.source_id, rel.target_id)
            type_map[key] = type_map.get(key, 0) + 1
        conflicts = sum(1 for c in type_map.values() if c > 1)
        if not type_map:
            rel_score = 100.0
        else:
            rel_score = max(0, 100.0 - (conflicts / len(type_map)) * 50.0)

        return (name_score + rel_score) / 2.0

    @staticmethod
    def _score_evidence(graph: KnowledgeGraph, total: int) -> float:
        facts_with_evidence = sum(1 for f in graph.facts.values() if f.evidence_refs)
        total_facts = len(graph.facts) or 1
        fact_score = (facts_with_evidence / total_facts) * 100.0

        valid_refs = 0
        total_refs = 0
        for fact in graph.facts.values():
            for ref in fact.evidence_refs:
                total_refs += 1
                if ref in graph.evidence:
                    valid_refs += 1
        ref_score = (valid_refs / max(total_refs, 1)) * 100.0

        entities_with_prov = sum(1 for e in graph.entities.values() if e.provenance)
        total_entities = len(graph.entities) or 1
        prov_score = (entities_with_prov / total_entities) * 100.0

        return (fact_score + ref_score + prov_score) / 3.0

    @staticmethod
    def _score_ontology(graph: KnowledgeGraph, total: int) -> float:
        if not graph.relationships:
            return 100.0
        valid_types = {
            "uses", "depends_on", "extends", "implements", "part_of",
            "contains", "creates", "manages", "requires", "supports",
            "provides", "enables", "integrates_with", "references", "related_to",
        }
        valid = sum(1 for r in graph.relationships.values() if r.relationship_type in valid_types)
        return (valid / len(graph.relationships)) * 100.0

    @staticmethod
    def _score_metadata(graph: KnowledgeGraph, total: int) -> float:
        has_metadata = 0
        for e in graph.entities.values():
            if e.metadata and e.metadata.tags:
                has_metadata += 1
        for f in graph.facts.values():
            if f.metadata and f.metadata.tags:
                has_metadata += 1
        return (has_metadata / max(total, 1)) * 100.0
