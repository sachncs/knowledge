"""Compiler passes for knowledge normalization.

These passes run in the NORMALIZATION phase and transform the
KnowledgeGraph into a canonical form: resolving aliases, detecting
duplicates, and generating stable identifiers.
"""

from __future__ import annotations

from typing import Any

from knowledge.models import KnowledgeGraph
from knowledge.normalization.dedup import DuplicateDetector
from knowledge.passes.base import CompilerPass, PassResult, Phase
from knowledge.passes.diagnostics import Diagnostic, Severity


class AliasResolutionPass(CompilerPass):
    """Resolves entity aliases by consolidating entities with equivalent names."""

    id = "normalization.aliases"
    phase = Phase.NORMALIZATION
    version = "0.1.0"
    description = "Resolve entity aliases and consolidate equivalent entities"

    def __init__(self) -> None:
        self.detector = DuplicateDetector()

    def execute(
        self,
        graph: KnowledgeGraph,
        config: dict[str, Any] | None = None,
    ) -> PassResult:
        """Resolve entity aliases and consolidate equivalent entities.

        Args:
            graph: The current KnowledgeGraph to process.
            config: Optional pass-specific configuration.

        Returns:
            A PassResult with a graph where equivalent entities have
            been merged, and an informational diagnostic.
        """
        if not graph.entities:
            return PassResult(graph=graph)

        entity_count = len(graph.entities)
        new_graph = self.detector.deduplicate_entities(graph)

        new_count = len(new_graph.entities)
        diag = Diagnostic(
            severity=Severity.INFORMATION,
            message=f"Alias resolution: {entity_count} entities → {new_count} canonical entities",
            location="normalization.aliases",
        )
        return PassResult(graph=new_graph, diagnostics=[diag])


class DuplicateDetectionPass(CompilerPass):
    """Detects and merges duplicate entities and concepts."""

    id = "normalization.dedup"
    phase = Phase.NORMALIZATION
    version = "0.1.0"
    description = "Detect and merge duplicate entities and concepts"
    depends_on = ("normalization.aliases",)

    def __init__(self) -> None:
        self.detector = DuplicateDetector()

    def execute(
        self,
        graph: KnowledgeGraph,
        config: dict[str, Any] | None = None,
    ) -> PassResult:
        """Detect and merge duplicate entities and concepts.

        Args:
            graph: The current KnowledgeGraph to process.
            config: Optional pass-specific configuration.

        Returns:
            A PassResult with a deduplicated graph and an informational
            diagnostic summarising the changes.
        """
        entity_count = len(graph.entities)
        concept_count = len(graph.concepts)

        new_graph = self.detector.deduplicate_all(graph)

        diag = Diagnostic(
            severity=Severity.INFORMATION,
            message=f"Deduplication: {entity_count} entities → {len(new_graph.entities)}, "
            f"{concept_count} concepts → {len(new_graph.concepts)}",
            location="normalization.dedup",
        )
        return PassResult(graph=new_graph, diagnostics=[diag])
