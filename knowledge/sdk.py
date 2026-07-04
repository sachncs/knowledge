"""Public SDK — the primary developer interface for working with OKF documents.

The SDK exposes the lifecycle of an OKF document through two main classes:
- Knowledge: the entry point for creating, loading, and verifying OKF docs
- OKFDocument: the primary object users interact with for operations
"""

from __future__ import annotations

from typing import Any

from knowledge.engine import VerificationEngine, VerificationResult
from knowledge.exceptions import (
    ParseError,
    UnsupportedSourceError,
)
from knowledge.kmd import KMDParser, KMDSerializer
from knowledge.models import KnowledgeGraph
from knowledge.passes import (
    AliasResolutionPass,
    DuplicateDetectionPass,
    ExtractionPass,
    PassManager,
)
from knowledge.passes.base import KnowledgeScore


class OKFDocument:
    """Represents an Open Knowledge Format document.

    This is the primary object users interact with. It wraps a
    KnowledgeGraph and provides lifecycle operations.
    """

    def __init__(
        self,
        graph: KnowledgeGraph,
        source: str | None = None,
        engine: VerificationEngine | None = None,
    ) -> None:
        self._graph = graph
        self.source = source
        self.engine = engine or VerificationEngine()
        self.last_verification: VerificationResult | None = None

    @property
    def graph(self) -> KnowledgeGraph:
        """The underlying KnowledgeGraph (read-only)."""
        return self._graph

    def save(self, path: str) -> None:
        """Serialize to KMD and write to a file.

        Args:
            path: Filesystem path to write the serialized document to.
        """
        serializer = KMDSerializer()
        content = serializer.serialize(self._graph)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)

    def verify(
        self,
        threshold: float = 80.0,
        max_iterations: int = 5,
    ) -> VerificationResult:
        """Run the verification engine on this document.

        Args:
            threshold: Minimum confidence threshold (0-100) for knowledge elements.
            max_iterations: Maximum number of verification iterations.

        Returns:
            VerificationResult containing the verified graph and score.
        """
        result = self.engine.verify(
            self._graph,
            threshold=threshold,
            max_iterations=max_iterations,
        )
        self._graph = result.graph
        self.last_verification = result
        return result

    def inspect(self) -> dict[str, Any]:
        """Return a high-level overview of the document.

        Returns:
            dict with entity_count, concept_count, fact_count,
            relationship_count, evidence_count, verification_score,
            and source.
        """
        g = self._graph
        score = self.last_verification.score if self.last_verification else KnowledgeScore()
        return {
            "entity_count": len(g.entities),
            "concept_count": len(g.concepts),
            "fact_count": len(g.facts),
            "relationship_count": len(g.relationships),
            "evidence_count": len(g.evidence),
            "verification_score": score.overall,
            "source": self.source,
        }

    def score(self) -> KnowledgeScore:
        """Compute document quality scores.

        Returns:
            KnowledgeScore with overall and per-dimension quality metrics.
        """
        from knowledge.passes.scoring import ScoringPass

        result = ScoringPass().execute(self._graph)
        return result.score or KnowledgeScore()

    def diff(self, other: OKFDocument) -> dict[str, list[str]]:
        """Compute semantic differences with another document.

        Args:
            other: The OKFDocument to compare against.

        Returns:
            dict mapping difference categories to lists of element IDs.
        """
        return self._graph.diff(other._graph)

    def merge(self, other: OKFDocument) -> OKFDocument:
        """Merge another document into this one.

        Args:
            other: The OKFDocument whose knowledge elements to merge.

        Returns:
            A new OKFDocument containing the merged graph.
        """
        merged = self._graph.merge(other._graph)
        return OKFDocument(graph=merged, source=self.source, engine=self.engine)

    def update(self, content: str, source: str = "unknown", fmt: str = "text") -> OKFDocument:
        """Extract knowledge from new content and merge it in.

        Args:
            content: Raw text or structured content to extract from.
            source: Label identifying the provenance of the content.
            fmt: Format of the input content (e.g. "text", "markdown").

        Returns:
            A verified OKFDocument with the extracted knowledge merged.
        """
        mgr = PassManager()
        mgr.register(ExtractionPass())
        mgr.register(AliasResolutionPass())
        mgr.register(DuplicateDetectionPass())
        config = {"extraction.pipeline": {"content": content, "source": source, "format": fmt}}
        result = mgr.execute(self._graph, config=config)
        updated = OKFDocument(graph=result.graph, source=self.source, engine=self.engine)
        updated.verify()
        return updated

    def delete(
        self,
        entity_id: str | None = None,
        relationship_id: str | None = None,
        fact_id: str | None = None,
        concept_id: str | None = None,
    ) -> OKFDocument:
        """Remove knowledge elements safely.

        Args:
            entity_id: ID of the entity to remove (and its relationships).
            relationship_id: ID of the relationship to remove.
            fact_id: ID of the fact to remove.
            concept_id: ID of the concept to remove.

        Returns:
            A new OKFDocument with the specified elements removed.
        """
        g = self._graph
        if entity_id:
            g = g.remove_entity(entity_id)
            for rel in list(g.relationships.values()):
                if rel.source_id == entity_id or rel.target_id == entity_id:
                    g = g.remove_relationship(rel.id)
        if relationship_id:
            g = g.remove_relationship(relationship_id)
        if fact_id:
            g = g.remove_fact(fact_id)
        if concept_id:
            g = g.remove_concept(concept_id)
        return OKFDocument(graph=g, source=self.source, engine=self.engine)


class Knowledge:
    """Primary entry point for the knowledge SDK.

    Responsible for creating, loading, and verifying OKF documents.
    """

    def __init__(self, engine: VerificationEngine | None = None) -> None:
        self.engine = engine or VerificationEngine()

    def create(
        self,
        input: str,
        fmt: str = "text",
    ) -> OKFDocument:
        """Create a new verified OKF document from a source string or file path.

        Args:
            input: Inline content string, file path, or URI.
            fmt: Format of the input ("text", "markdown", etc.).

        Returns:
            A verified OKFDocument.
        """
        content: str
        source: str

        if (
            input.startswith("file://")
            or input.startswith("http://")
            or input.startswith("https://")
        ):
            raise UnsupportedSourceError(f"Remote sources not yet supported: {input}")

        try:
            with open(input, encoding="utf-8") as f:
                content = f.read()
            source = input
            if input.endswith(".md") or input.endswith(".markdown"):
                fmt = "markdown"
        except (FileNotFoundError, IsADirectoryError, OSError):
            content = input
            source = "inline"

        doc = OKFDocument(graph=KnowledgeGraph(), source=source, engine=self.engine)
        doc = doc.update(content, source=source, fmt=fmt)
        return doc

    def read(self, path: str) -> OKFDocument:
        """Load an existing KMD document.

        Args:
            path: Filesystem path to a KMD file.

        Returns:
            An OKFDocument parsed from the file.

        Raises:
            ParseError: If the file cannot be read or parsed.
        """
        try:
            with open(path, encoding="utf-8") as f:
                content = f.read()
        except FileNotFoundError:
            raise ParseError(f"File not found: {path}")

        parser = KMDParser()
        try:
            graph = parser.parse(content)
        except (ParseError, ValueError) as e:
            raise ParseError(f"Failed to parse KMD document: {e}")

        return OKFDocument(graph=graph, source=path, engine=self.engine)

    def verify(
        self, doc: OKFDocument, threshold: float = 80.0, max_iterations: int = 5
    ) -> VerificationResult:
        """Verify an existing document.

        Args:
            doc: The OKFDocument to verify.
            threshold: Minimum quality threshold (0-100).
            max_iterations: Maximum verification iterations.

        Returns:
            VerificationResult with the verified graph and scores.
        """
        return doc.verify(threshold=threshold, max_iterations=max_iterations)

    def delete(
        self,
        doc: OKFDocument,
        entity_id: str | None = None,
        relationship_id: str | None = None,
        fact_id: str | None = None,
        concept_id: str | None = None,
    ) -> OKFDocument:
        """Remove knowledge elements from a document.

        Args:
            doc: The OKFDocument to delete from.
            entity_id: ID of the entity to remove.
            relationship_id: ID of the relationship to remove.
            fact_id: ID of the fact to remove.
            concept_id: ID of the concept to remove.

        Returns:
            A new OKFDocument with the specified elements removed.
        """
        return doc.delete(
            entity_id=entity_id,
            relationship_id=relationship_id,
            fact_id=fact_id,
            concept_id=concept_id,
        )

    def inspect(self, doc: OKFDocument) -> dict[str, Any]:
        """Return a high-level overview of a document.

        Args:
            doc: The OKFDocument to inspect.

        Returns:
            dict with entity_count, concept_count, etc.
        """
        return doc.inspect()

    def score(self, doc: OKFDocument) -> KnowledgeScore:
        """Compute quality scores for a document.

        Args:
            doc: The OKFDocument to score.

        Returns:
            KnowledgeScore with quality metrics.
        """
        return doc.score()

    def diff(self, a: OKFDocument, b: OKFDocument) -> dict[str, list[str]]:
        """Compute semantic differences between two documents.

        Args:
            a: The first OKFDocument.
            b: The second OKFDocument.

        Returns:
            dict mapping difference categories to lists of element IDs.
        """
        return a.diff(b)

    def merge(self, a: OKFDocument, b: OKFDocument) -> OKFDocument:
        """Merge two documents into one.

        Args:
            a: The first OKFDocument (primary).
            b: The second OKFDocument to merge in.

        Returns:
            A new OKFDocument containing merged knowledge.
        """
        return a.merge(b)

    def update(self, doc: OKFDocument, input: str, fmt: str = "text") -> OKFDocument:
        """Update an existing document with new knowledge.

        Args:
            doc: The OKFDocument to update.
            input: Raw content string to extract knowledge from.
            fmt: Format of the input content.

        Returns:
            The updated OKFDocument.
        """
        return doc.update(input, source=doc.source or "unknown", fmt=fmt)
