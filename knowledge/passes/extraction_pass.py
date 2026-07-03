"""Compiler passes for knowledge extraction.

These passes run in the EXTRACTION phase and populate the
KnowledgeGraph with knowledge elements discovered from source content.
"""

from __future__ import annotations

from typing import Any

from knowledge.extraction.extractors import ExtractionPipeline
from knowledge.extraction.sources import MarkdownSourceReader, SourceDocument, TextSourceReader
from knowledge.models import KnowledgeGraph
from knowledge.passes.base import CompilerPass, PassResult, Phase
from knowledge.passes.diagnostics import Diagnostic, Severity


class ExtractionPass(CompilerPass):
    """Extracts knowledge elements from raw source content.

    Reads source content attached to the graph as evidence, runs the
    deterministic extraction pipeline, and populates the graph with
    discovered entities, concepts, facts, relationships, and evidence.
    """

    id = "extraction.pipeline"
    phase = Phase.EXTRACTION
    version = "0.1.0"
    description = "Extract entities, concepts, facts, and relationships from source content"

    def __init__(self) -> None:
        self.pipeline = ExtractionPipeline()

    def execute(
        self,
        graph: KnowledgeGraph,
        config: dict[str, Any] | None = None,
    ) -> PassResult:
        """Run the extraction pipeline on source content.

        Reads content from the config, runs the extraction pipeline,
        and populates the graph with discovered entities, concepts,
        facts, relationships, and evidence.

        Args:
            graph: The current KnowledgeGraph to process.
            config: Optional configuration with keys ``content``,
                ``source``, and ``format`` (``"text"`` or ``"markdown"``).

        Returns:
            A PassResult with the enriched graph and an informational
            diagnostic summarising extracted elements.
        """
        cfg = config or {}
        content: str = cfg.get("content", "")
        source: str = cfg.get("source", "unknown")
        source_format: str = cfg.get("format", "text")

        if not content:
            diag = Diagnostic(
                severity=Severity.WARNING,
                message="No source content provided for extraction",
                location="extraction.pipeline",
            )
            return PassResult(graph=graph, diagnostics=[diag])

        doc: SourceDocument
        if source_format == "markdown":
            doc = MarkdownSourceReader().read(content, source)
        else:
            doc = TextSourceReader().read(content, source)
        result = self.pipeline.extract(doc.content, source)

        new_graph = graph
        for entity in result.entities:
            new_graph = new_graph.add_entity(entity)
        for concept in result.concepts:
            new_graph = new_graph.add_concept(concept)
        for fact in result.facts:
            new_graph = new_graph.add_fact(fact)
        for rel in result.relationships:
            new_graph = new_graph.add_relationship(rel)
        for ev in result.evidence:
            new_graph = new_graph.add_evidence(ev)

        diag = Diagnostic(
            severity=Severity.INFORMATION,
            message=f"Extracted {len(result.entities)} entities, {len(result.concepts)} concepts, "
            f"{len(result.facts)} facts, {len(result.relationships)} relationships, "
            f"{len(result.evidence)} evidence blocks from '{source}'",
            location="extraction.pipeline",
        )

        return PassResult(graph=new_graph, diagnostics=[diag])
