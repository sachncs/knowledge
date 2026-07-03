"""Scoring passes — compute document quality metrics."""

from __future__ import annotations

from typing import Any

from knowledge.models import KnowledgeGraph
from knowledge.passes.base import (
    VALID_RELATIONSHIP_TYPES,
    CompilerPass,
    KnowledgeScore,
    PassResult,
    Phase,
)


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
        """Compute quality scores for the knowledge graph.

        Args:
            graph: The knowledge graph to score.
            config: Optional configuration dictionary.

        Returns:
            PassResult containing the computed KnowledgeScore.
        """
        score = self.compute_score(graph)
        return PassResult(graph=graph, score=score)

    def compute_score(self, graph: KnowledgeGraph) -> KnowledgeScore:
        """Aggregate sub-scores into a single KnowledgeScore.

        Args:
            graph: The knowledge graph to score.

        Returns:
            A KnowledgeScore with overall and per-dimension scores.
        """
        total_elements = (
            len(graph.entities)
            + len(graph.concepts)
            + len(graph.facts)
            + len(graph.relationships)
            + len(graph.evidence)
        )
        if total_elements == 0:
            return KnowledgeScore()

        completeness = self.score_completeness(graph, total_elements)
        consistency = self.score_consistency(graph, total_elements)
        evidence_quality = self.score_evidence(graph, total_elements)
        ontology_quality = self.score_ontology(graph, total_elements)
        metadata = self.score_metadata(graph, total_elements)

        overall = (
            completeness * 0.25
            + consistency * 0.25
            + evidence_quality * 0.20
            + ontology_quality * 0.15
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
    def score_completeness(graph: KnowledgeGraph, total: int) -> float:
        """Score how complete descriptions and statements are.

        Args:
            graph: The knowledge graph.
            total: Total number of elements.

        Returns:
            Completeness score as a float (0-100).
        """
        has_description = sum(1 for e in graph.entities.values() if e.description)
        has_statement = sum(1 for f in graph.facts.values() if f.statement)
        return ((has_description + has_statement) / max(total, 1)) * 100.0

    @staticmethod
    def score_consistency(graph: KnowledgeGraph, total: int) -> float:
        """Score naming and relationship consistency.

        Args:
            graph: The knowledge graph.
            total: Total number of elements.

        Returns:
            Consistency score as a float (0-100).
        """
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
    def score_evidence(graph: KnowledgeGraph, total: int) -> float:
        """Score evidence coverage and reference validity.

        Args:
            graph: The knowledge graph.
            total: Total number of elements.

        Returns:
            Evidence quality score as a float (0-100).
        """
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
    def score_ontology(graph: KnowledgeGraph, total: int) -> float:
        """Score ontology quality based on valid relationship types.

        Args:
            graph: The knowledge graph.
            total: Total number of elements.

        Returns:
            Ontology quality score as a float (0-100).
        """
        if not graph.relationships:
            return 100.0
        valid = sum(
            1
            for r in graph.relationships.values()
            if r.relationship_type in VALID_RELATIONSHIP_TYPES
        )
        return (valid / len(graph.relationships)) * 100.0

    @staticmethod
    def score_metadata(graph: KnowledgeGraph, total: int) -> float:
        """Score metadata completeness (tags, etc.).

        Args:
            graph: The knowledge graph.
            total: Total number of elements.

        Returns:
            Metadata completeness score as a float (0-100).
        """
        has_metadata = 0
        for e in graph.entities.values():
            if e.metadata and e.metadata.tags:
                has_metadata += 1
        for f in graph.facts.values():
            if f.metadata and f.metadata.tags:
                has_metadata += 1
        return (has_metadata / max(total, 1)) * 100.0
