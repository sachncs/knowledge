"""Repair passes — automatically fix common knowledge issues."""

from __future__ import annotations

from typing import Any

from knowledge.models import KnowledgeGraph, Provenance
from knowledge.normalization.dedup import DuplicateDetector
from knowledge.passes.base import CompilerPass, PassResult, Phase
from knowledge.passes.diagnostics import Diagnostic, Severity


class MergeDuplicateEntitiesPass(CompilerPass):
    """Merges duplicate entities by consolidating aliases."""

    id = "repair.merge_entities"
    phase = Phase.REPAIR
    version = "0.1.0"
    description = "Merge duplicate entities and consolidate aliases"

    def __init__(self) -> None:
        self.detector = DuplicateDetector()

    def execute(
        self,
        graph: KnowledgeGraph,
        config: dict[str, Any] | None = None,
    ) -> PassResult:
        """Merge duplicate entities by consolidating aliases.

        Args:
            graph: The knowledge graph to repair.
            config: Optional configuration dictionary.

        Returns:
            PassResult with the repaired graph.
        """
        entity_count = len(graph.entities)
        new_graph = self.detector.deduplicate_entities(graph)
        merged_count = entity_count - len(new_graph.entities)

        diag = Diagnostic(
            severity=Severity.INFORMATION,
            message=f"Merged {merged_count} duplicate entities",
            location="repair.merge_entities",
        )
        return PassResult(graph=new_graph, diagnostics=[diag])


class AttachProvenancePass(CompilerPass):
    """Attaches provenance to elements missing it where possible."""

    id = "repair.attach_provenance"
    phase = Phase.REPAIR
    version = "0.1.0"
    description = "Attach provenance to knowledge elements missing it"

    def execute(
        self,
        graph: KnowledgeGraph,
        config: dict[str, Any] | None = None,
    ) -> PassResult:
        """Attach provenance to elements missing it where possible.

        Args:
            graph: The knowledge graph to repair.
            config: Optional configuration dictionary.

        Returns:
            PassResult with the repaired graph.
        """
        fixed_count = 0
        new_graph = graph

        for entity in new_graph.entities.values():
            if entity.provenance is None:
                prov = Provenance(
                    source_id="unknown",
                    extractor="repair.attach_provenance",
                )
                new_graph = new_graph.update_entity(entity.model_copy(update={"provenance": prov}))
                fixed_count += 1

        diag = Diagnostic(
            severity=Severity.INFORMATION,
            message=f"Attached provenance to {fixed_count} elements",
            location="repair.attach_provenance",
        )
        return PassResult(graph=new_graph, diagnostics=[diag])


class FixEvidenceRefsPass(CompilerPass):
    """Removes evidence references that point to non-existent evidence."""

    id = "repair.fix_evidence_refs"
    phase = Phase.REPAIR
    version = "0.1.0"
    description = "Remove broken evidence references from facts"

    def execute(
        self,
        graph: KnowledgeGraph,
        config: dict[str, Any] | None = None,
    ) -> PassResult:
        """Remove evidence references that point to non-existent evidence.

        Args:
            graph: The knowledge graph to repair.
            config: Optional configuration dictionary.

        Returns:
            PassResult with the repaired graph.
        """
        fixed_count = 0
        new_graph = graph
        evidence_ids = set(graph.evidence.keys())

        for fact in new_graph.facts.values():
            valid_refs = [ref for ref in fact.evidence_refs if ref in evidence_ids]
            if len(valid_refs) != len(fact.evidence_refs):
                new_graph = new_graph.update_fact(
                    fact.model_copy(update={"evidence_refs": valid_refs})
                )
                fixed_count += 1

        diag = Diagnostic(
            severity=Severity.INFORMATION,
            message=f"Fixed {fixed_count} facts with broken evidence references",
            location="repair.fix_evidence_refs",
        )
        return PassResult(graph=new_graph, diagnostics=[diag])


class NormalizeConfidencePass(CompilerPass):
    """Normalizes confidence scores to valid range."""

    id = "repair.normalize_confidence"
    phase = Phase.REPAIR
    version = "0.1.0"
    description = "Normalize confidence scores to valid 0-1 range"

    def execute(
        self,
        graph: KnowledgeGraph,
        config: dict[str, Any] | None = None,
    ) -> PassResult:
        """Normalize confidence scores to valid 0-1 range.

        Args:
            graph: The knowledge graph to repair.
            config: Optional configuration dictionary.

        Returns:
            PassResult with the repaired graph.
        """
        fixed_count = 0
        new_graph = graph

        def clamp_conf(val: float) -> float:
            return max(0.0, min(1.0, val))

        for entity in new_graph.entities.values():
            if entity.confidence < 0.0 or entity.confidence > 1.0:
                new_graph = new_graph.update_entity(
                    entity.model_copy(update={"confidence": clamp_conf(entity.confidence)})
                )
                fixed_count += 1

        for concept in new_graph.concepts.values():
            if concept.confidence < 0.0 or concept.confidence > 1.0:
                new_graph = new_graph.update_concept(
                    concept.model_copy(update={"confidence": clamp_conf(concept.confidence)})
                )
                fixed_count += 1

        for fact in new_graph.facts.values():
            if fact.confidence < 0.0 or fact.confidence > 1.0:
                new_graph = new_graph.update_fact(
                    fact.model_copy(update={"confidence": clamp_conf(fact.confidence)})
                )
                fixed_count += 1

        for rel in new_graph.relationships.values():
            if rel.confidence < 0.0 or rel.confidence > 1.0:
                new_graph = new_graph.update_relationship(
                    rel.model_copy(update={"confidence": clamp_conf(rel.confidence)})
                )
                fixed_count += 1

        diag = Diagnostic(
            severity=Severity.INFORMATION,
            message=f"Normalized confidence for {fixed_count} elements",
            location="repair.normalize_confidence",
        )
        return PassResult(graph=new_graph, diagnostics=[diag])
