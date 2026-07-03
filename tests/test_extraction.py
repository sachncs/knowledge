"""Tests for knowledge extraction — sources, extractors, and extraction passes."""

from __future__ import annotations

from knowledge.extraction.extractors import (
    ConceptExtractor,
    EntityExtractor,
    EvidenceExtractor,
    ExtractionPipeline,
    ExtractionResult,
    FactExtractor,
    RelationshipExtractor,
)
from knowledge.extraction.sources import MarkdownSourceReader, SourceDocument, TextSourceReader
from knowledge.models import KnowledgeGraph
from knowledge.passes import ExtractionPass, PassManager, Phase


class TestSourceReaders:
    def test_text_source_reader(self) -> None:
        reader = TextSourceReader()
        doc = reader.read("Hello world", "test.txt")
        assert isinstance(doc, SourceDocument)
        assert doc.content == "Hello world"
        assert doc.source == "test.txt"
        assert doc.metadata["format"] == "text"

    def test_markdown_source_reader_strips_formatting(self) -> None:
        reader = MarkdownSourceReader()
        md = "# Heading\n\nThis has **bold** and *italic* and `code` and [link](url)."
        doc = reader.read(md, "test.md")
        assert "**bold**" not in doc.content
        assert "bold" in doc.content
        assert "*italic*" not in doc.content
        assert "italic" in doc.content
        assert "`code`" not in doc.content
        assert "code" in doc.content
        assert "[link](url)" not in doc.content
        assert "link" in doc.content

    def test_markdown_source_reader_preserves_headings(self) -> None:
        reader = MarkdownSourceReader()
        md = "# Title\n\n## Section 1\n\nSome text.\n\n### Subsection\n\nMore text."
        doc = reader.read(md, "test.md")
        assert "Title" in doc.metadata["headings"]
        assert "Section 1" in doc.metadata["headings"]


class TestEntityExtractor:
    def test_extracts_capitalized_phrases(self) -> None:
        extractor = EntityExtractor()
        content = (
            "Python is a language. JavaScript is also a language. Both are used in Web Development."
        )
        entities = extractor.extract(content, "test.md")
        names = [e.name for e in entities]
        assert "Python" in names
        assert "JavaScript" in names
        assert "Web Development" in names

    def test_deduplicates_entities(self) -> None:
        extractor = EntityExtractor()
        content = "Python is great. Python is also versatile."
        entities = extractor.extract(content, "test.md")
        names = [e.name for e in entities]
        assert names.count("Python") == 1

    def test_empty_content(self) -> None:
        extractor = EntityExtractor()
        entities = extractor.extract("", "test.md")
        assert entities == []

    def test_provenance_attached(self) -> None:
        extractor = EntityExtractor()
        entities = extractor.extract("Hello World System", "doc.md")
        assert all(e.provenance is not None for e in entities)
        assert all(e.provenance.extractor == "entity_extractor" for e in entities)


class TestConceptExtractor:
    def test_extracts_concepts(self) -> None:
        extractor = ConceptExtractor()
        content = (
            "Machine Learning is a subset of artificial intelligence. "
            "Deep Learning involves neural networks."
        )
        concepts = extractor.extract(content, "test.md")
        names = [c.name for c in concepts]
        assert "Machine Learning" in names
        assert "Deep Learning" in names

    def test_empty_content(self) -> None:
        extractor = ConceptExtractor()
        assert extractor.extract("") == []


class TestFactExtractor:
    def test_extracts_sentences(self) -> None:
        extractor = FactExtractor()
        content = "Python supports asynchronous programming. It is widely used in data science."
        facts = extractor.extract(content, ["ev_001"], "test.md")
        assert len(facts) >= 2

    def test_facts_have_evidence_refs(self) -> None:
        extractor = FactExtractor()
        content = "Python is dynamically typed."
        facts = extractor.extract(content, ["ev_001"], "test.md")
        assert all("ev_001" in f.evidence_refs for f in facts)

    def test_empty_content(self) -> None:
        extractor = FactExtractor()
        assert extractor.extract("", []) == []


class TestEvidenceExtractor:
    def test_extracts_paragraphs(self) -> None:
        extractor = EvidenceExtractor()
        content = "First paragraph with some content.\n\nSecond paragraph with more details."
        evidence = extractor.extract(content, "test.md")
        assert len(evidence) >= 2

    def test_skips_short_paragraphs(self) -> None:
        extractor = EvidenceExtractor()
        content = (
            "Short.\n\nThis is a longer paragraph with meaningful content for evidence extraction."
        )
        evidence = extractor.extract(content, "test.md")
        assert all(len(e.content) >= 20 for e in evidence)


class TestRelationshipExtractor:
    def test_extracts_relationships(self) -> None:
        extractor = RelationshipExtractor()
        content = "Python uses dynamic typing. Python supports object orientation."
        entity_names = {"Python", "dynamic typing", "object orientation"}
        rels = extractor.extract(content, entity_names, "test.md")
        assert len(rels) >= 1

    def test_empty_content(self) -> None:
        extractor = RelationshipExtractor()
        assert extractor.extract("", set()) == []


class TestExtractionPipeline:
    def test_full_pipeline(self) -> None:
        pipeline = ExtractionPipeline()
        content = """
Python is a programming language. Python supports asynchronous programming.

JavaScript is used for web development. Node.js is a JavaScript runtime.

Machine Learning is transforming technology.
"""
        result = pipeline.extract(content, "test.md")
        assert isinstance(result, ExtractionResult)
        assert len(result.entities) > 0
        assert len(result.concepts) > 0
        assert len(result.facts) > 0
        assert len(result.evidence) > 0

    def test_deterministic(self) -> None:
        pipeline = ExtractionPipeline()
        content = "Python is a programming language."
        r1 = pipeline.extract(content, "test.md")
        r2 = pipeline.extract(content, "test.md")
        assert [e.name for e in r1.entities] == [e.name for e in r2.entities]
        assert [f.statement for f in r1.facts] == [f.statement for f in r2.facts]


class TestExtractionPass:
    def test_execute_with_content(self) -> None:
        passer = PassManager()
        passer.register(ExtractionPass())
        config = {
            "extraction.pipeline": {
                "content": "Python is a programming language. JavaScript is another language.",
                "source": "test.md",
                "format": "text",
            }
        }
        result = passer.execute(KnowledgeGraph(), config=config)
        assert len(result.graph.entities) > 0
        assert len(result.graph.facts) > 0

    def test_execute_empty_content(self) -> None:
        passer = PassManager()
        passer.register(ExtractionPass())
        config = {"extraction.pipeline": {"content": ""}}
        result = passer.execute(KnowledgeGraph(), config=config)
        assert len(result.diagnostics) == 1
        assert "warning" in result.diagnostics[0].severity.value

    def test_execute_markdown_content(self) -> None:
        passer = PassManager()
        passer.register(ExtractionPass())
        config = {
            "extraction.pipeline": {
                "content": (
                    "# Knowledge\n\nPython is a language. **JavaScript** is also a language."
                ),
                "source": "test.md",
                "format": "markdown",
            }
        }
        result = passer.execute(KnowledgeGraph(), config=config)
        assert len(result.graph.entities) > 0

    def test_execute_filters_by_phase(self) -> None:
        passer = PassManager()
        passer.register(ExtractionPass())
        result = passer.execute(KnowledgeGraph(), phases=[Phase.NORMALIZATION])
        # ExtractionPass is in EXTRACTION phase, so nothing runs
        assert len(result.executed) == 0
        assert result.graph == KnowledgeGraph()
