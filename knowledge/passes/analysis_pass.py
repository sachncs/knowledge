"""Analysis passes — compute graph statistics and metadata.

These passes run in the ANALYSIS phase and compute summary
statistics about the KnowledgeGraph without modifying it.
"""

from __future__ import annotations

from typing import Any

from knowledge.models import KnowledgeGraph
from knowledge.passes.base import CompilerPass, PassResult, Phase
from knowledge.passes.diagnostics import Diagnostic, Severity


class GraphStatisticsPass(CompilerPass):
    """Computes summary statistics about the KnowledgeGraph.

    Reports element counts, connectivity density, and other
    structural properties as informational diagnostics.
    """

    id = "analysis.statistics"
    phase = Phase.ANALYSIS
    version = "0.1.0"
    description = "Compute graph statistics and structural summaries"

    def execute(
        self,
        graph: KnowledgeGraph,
        config: dict[str, Any] | None = None,
    ) -> PassResult:
        """Compute summary statistics about the KnowledgeGraph.

        Args:
            graph: The knowledge graph to analyze.
            config: Optional configuration dictionary.

        Returns:
            PassResult with informational statistics diagnostics.
        """
        diagnostics: list[Diagnostic] = []

        entity_count = len(graph.entities)
        concept_count = len(graph.concepts)
        fact_count = len(graph.facts)
        rel_count = len(graph.relationships)
        evidence_count = len(graph.evidence)
        total = entity_count + concept_count + fact_count + rel_count + evidence_count

        diagnostics.append(
            Diagnostic(
                severity=Severity.INFORMATION,
                message=f"KnowledgeGraph has {total} total elements: "
                f"{entity_count} entities, {concept_count} concepts, "
                f"{fact_count} facts, {rel_count} relationships, "
                f"{evidence_count} evidence blocks",
                location="analysis.statistics",
            )
        )

        if entity_count > 0 and rel_count > 0:
            isolated = sum(
                1
                for eid in graph.entities
                if not any(
                    r.source_id == eid or r.target_id == eid for r in graph.relationships.values()
                )
            )
            if isolated > 0:
                diagnostics.append(
                    Diagnostic(
                        severity=Severity.SUGGESTION,
                        message=f"{isolated} of {entity_count} entities have no relationships",
                        explanation=(
                            "Isolated entities may indicate incomplete knowledge extraction."
                        ),
                        location="analysis.statistics",
                    )
                )

        return PassResult(graph=graph, diagnostics=diagnostics)
