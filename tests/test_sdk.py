"""Tests for the public SDK — Knowledge and OKFDocument classes."""

import tempfile

import pytest

from knowledge import KMDSerializer, Knowledge, OKFDocument
from knowledge.engine import VerificationResult
from knowledge.exceptions import (
    ParseError,
    UnsupportedSourceError,
)
from knowledge.models import Concept, Entity, Fact, KnowledgeGraph
from knowledge.passes.scoring import KnowledgeScore


class TestKnowledge:
    def test_create_with_text(self) -> None:
        knowledge = Knowledge()
        doc = knowledge.create("Python is a programming language.")
        assert isinstance(doc, OKFDocument)
        assert len(doc.graph.entities) > 0
        assert len(doc.graph.facts) > 0
        assert doc.last_verification is not None

    def test_create_from_file(self) -> None:
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            f.write("# Knowledge\n\nPython is a language.\n")
            fname = f.name
        knowledge = Knowledge()
        doc = knowledge.create(fname)
        assert doc.source is not None
        assert len(doc.graph.entities) > 0

    def test_read_okf(self) -> None:
        graph = KnowledgeGraph()
        graph = graph.add_entity(Entity(name="Python", id="ent_001"))
        serializer = KMDSerializer()
        content = serializer.serialize(graph)
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            f.write(content)
            fname = f.name
        knowledge = Knowledge()
        doc = knowledge.read(fname)
        assert isinstance(doc, OKFDocument)
        assert "ent_001" in doc.graph.entities

    def test_read_invalid_file(self) -> None:
        knowledge = Knowledge()
        with pytest.raises(ParseError):
            knowledge.read("/nonexistent/file.md")

    def test_update(self) -> None:
        knowledge = Knowledge()
        doc = knowledge.create("Python is a language.")
        doc = knowledge.update(doc, "JavaScript is for web development.", fmt="text")
        assert len(doc.graph.entities) > 1

    def test_unsupported_source(self) -> None:
        knowledge = Knowledge()
        with pytest.raises(UnsupportedSourceError):
            knowledge.create("https://example.com")

    def test_verify_delegate(self) -> None:
        knowledge = Knowledge()
        doc = knowledge.create("Python is a language.")
        result = knowledge.verify(doc)
        assert isinstance(result, VerificationResult)

    def test_delete_delegate(self) -> None:
        from knowledge.models import Relationship

        knowledge = Knowledge()
        graph = KnowledgeGraph()
        graph = graph.add_entity(Entity(name="A", id="e1"))
        graph = graph.add_entity(Entity(name="B", id="e2"))
        graph = graph.add_relationship(
            Relationship(source_id="e1", target_id="e2", relationship_type="related", id="r1")
        )
        doc = OKFDocument(graph=graph)
        doc = knowledge.delete(doc, entity_id="e1")
        assert "e1" not in doc.graph.entities
        assert "r1" not in doc.graph.relationships

    def test_inspect_delegate(self) -> None:
        knowledge = Knowledge()
        doc = knowledge.create("Python is a language.")
        info = knowledge.inspect(doc)
        assert info["entity_count"] > 0

    def test_score_delegate(self) -> None:
        knowledge = Knowledge()
        doc = knowledge.create("Python is a language.")
        score = knowledge.score(doc)
        assert isinstance(score, KnowledgeScore)

    def test_diff_delegate(self) -> None:
        knowledge = Knowledge()
        doc_a = knowledge.create("Python is a language.")
        doc_b = knowledge.create("JavaScript is a language.")
        changes = knowledge.diff(doc_a, doc_b)
        assert "entities_added" in changes

    def test_merge_delegate(self) -> None:
        knowledge = Knowledge()
        doc_a = knowledge.create("Python is a language.")
        doc_b = knowledge.create("JavaScript is a language.")
        merged = knowledge.merge(doc_a, doc_b)
        assert isinstance(merged, OKFDocument)
        assert len(merged.graph.entities) >= len(doc_a.graph.entities)

    def test_read_malformed_content(self) -> None:
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            f.write("## Foo: bar\n  id: x\n")
            fname = f.name
        knowledge = Knowledge()
        with pytest.raises(ParseError, match="Failed to parse"):
            knowledge.read(fname)


class TestOKFDocument:
    def test_save_and_read(self) -> None:
        doc = OKFDocument(graph=KnowledgeGraph())
        doc = doc.update("Python is a language.", "test.md")
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            fname = f.name
        doc.save(fname)
        with open(fname) as f:
            content = f.read()
        assert "## Entity:" in content
        assert "## Fact:" in content

    def test_verify(self) -> None:
        doc = OKFDocument(graph=KnowledgeGraph())
        doc = doc.update("Python is great.")
        result = doc.verify()
        assert isinstance(result, VerificationResult)
        assert result.score.overall >= 0

    def test_inspect(self) -> None:
        doc = OKFDocument(graph=KnowledgeGraph())
        doc = doc.update("Python is a language.")
        info = doc.inspect()
        assert info["entity_count"] > 0
        assert info["fact_count"] > 0
        assert info["verification_score"] > 0  # verified after update

    def test_score(self) -> None:
        doc = OKFDocument(graph=KnowledgeGraph())
        doc = doc.update("Python is a language.")
        score = doc.score()
        assert isinstance(score, KnowledgeScore)
        assert score.overall >= 0

    def test_diff(self) -> None:
        doc_a = OKFDocument(graph=KnowledgeGraph())
        doc_a = doc_a.update("Python is a language.")
        doc_b = OKFDocument(graph=KnowledgeGraph())
        doc_b = doc_b.update("JavaScript is a language.")
        changes = doc_a.diff(doc_b)
        assert isinstance(changes, dict)
        assert "entities_added" in changes

    def test_merge(self) -> None:
        doc_a = OKFDocument(graph=KnowledgeGraph())
        doc_a = doc_a.update("Python is a language.", "a.md")
        doc_b = OKFDocument(graph=KnowledgeGraph())
        doc_b = doc_b.update("JavaScript is a language.", "b.md")
        merged = doc_a.merge(doc_b)
        assert len(merged.graph.entities) >= len(doc_a.graph.entities)

    def test_delete_entity(self) -> None:
        graph = KnowledgeGraph()
        graph = graph.add_entity(Entity(name="Python", id="ent_001"))
        graph = graph.add_entity(Entity(name="Java", id="ent_002"))
        doc = OKFDocument(graph=graph)
        doc = doc.delete(entity_id="ent_001")
        assert "ent_001" not in doc.graph.entities
        assert "ent_002" in doc.graph.entities

    def test_delete_relationship(self) -> None:
        from knowledge.models import Relationship

        graph = KnowledgeGraph()
        graph = graph.add_relationship(
            Relationship(source_id="a", target_id="b", relationship_type="uses", id="rel_001")
        )
        doc = OKFDocument(graph=graph)
        doc = doc.delete(relationship_id="rel_001")
        assert "rel_001" not in doc.graph.relationships

    def test_delete_fact(self) -> None:
        graph = KnowledgeGraph()
        graph = graph.add_fact(Fact(statement="Python is a language.", id="f1"))
        doc = OKFDocument(graph=graph)
        doc = doc.delete(fact_id="f1")
        assert "f1" not in doc.graph.facts

    def test_delete_concept(self) -> None:
        graph = KnowledgeGraph()
        graph = graph.add_concept(Concept(name="Programming", id="c1"))
        doc = OKFDocument(graph=graph)
        doc = doc.delete(concept_id="c1")
        assert "c1" not in doc.graph.concepts

    def test_delete_entity_removes_related_relationships(self) -> None:
        from knowledge.models import Relationship

        graph = KnowledgeGraph()
        graph = graph.add_entity(Entity(name="Python", id="ent_001"))
        graph = graph.add_entity(Entity(name="Java", id="ent_002"))
        graph = graph.add_relationship(
            Relationship(
                source_id="ent_001", target_id="ent_002", relationship_type="uses", id="rel_001"
            )
        )
        doc = OKFDocument(graph=graph)
        doc = doc.delete(entity_id="ent_001")
        assert "rel_001" not in doc.graph.relationships

    def test_graph_property(self) -> None:
        doc = OKFDocument(graph=KnowledgeGraph())
        assert isinstance(doc.graph, KnowledgeGraph)

    def test_source_property(self) -> None:
        doc = OKFDocument(graph=KnowledgeGraph(), source="test.md")
        assert doc.source == "test.md"
