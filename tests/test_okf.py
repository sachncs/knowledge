"""Tests for the OKF parser and serializer (round-trip)."""

import pytest

from knowledge.exceptions import ParseError
from knowledge.models import (
    Concept,
    Entity,
    Evidence,
    Fact,
    KnowledgeGraph,
    Relationship,
    VerificationState,
)
from knowledge.okf import OKFParser, OKFSerializer


def make_graph() -> KnowledgeGraph:
    entity = Entity(
        id="python",
        name="Python",
        aliases=["Py", "CPython"],
        description="A programming language.",
        confidence=0.95,
        verification_state=VerificationState.VERIFIED,
    )
    concept = Concept(
        id="dynamic-typing",
        name="Dynamic Typing",
        description="Runtime type checking.",
        confidence=0.9,
    )
    fact = Fact(
        id="python-dynamic",
        statement="Python uses dynamic typing.",
        evidence_refs=["ev-001"],
        confidence=0.9,
    )
    rel = Relationship(
        id="py-uses-dynamic",
        source_id="python",
        target_id="dynamic-typing",
        relationship_type="uses",
        evidence_refs=["ev-001"],
        confidence=0.85,
        verification_state=VerificationState.VERIFIED,
    )
    ev = Evidence(
        id="ev-001",
        content="Python is dynamically typed.",
        source="https://docs.python.org/3/",
    )
    return (
        KnowledgeGraph()
        .add_entity(entity)
        .add_concept(concept)
        .add_fact(fact)
        .add_relationship(rel)
        .add_evidence(ev)
    )


class TestOKFParser:
    def test_parse_empty(self) -> None:
        graph = OKFParser().parse("")
        assert len(graph.entities) == 0
        assert len(graph.concepts) == 0
        assert len(graph.facts) == 0
        assert len(graph.relationships) == 0
        assert len(graph.evidence) == 0

    def test_parse_header_only(self) -> None:
        graph = OKFParser().parse("# Open Knowledge Format\n")
        assert len(graph.entities) == 0

    def test_parse_entity(self) -> None:
        okf = """\
## Entity: python
- **name**: Python
- **aliases**: Py
- **description**: A language.
- **confidence**: 0.95
- **verification**: verified
"""
        graph = OKFParser().parse(okf)
        assert "python" in graph.entities
        entity = graph.entities["python"]
        assert entity.name == "Python"
        assert entity.aliases == ["Py"]
        assert entity.description == "A language."
        assert entity.confidence == 0.95
        assert entity.verification_state == VerificationState.VERIFIED

    def test_parse_concept(self) -> None:
        okf = """\
## Concept: ml
- **name**: Machine Learning
"""
        graph = OKFParser().parse(okf)
        assert "ml" in graph.concepts
        assert graph.concepts["ml"].name == "Machine Learning"

    def test_parse_fact(self) -> None:
        okf = """\
## Fact: f1
- **statement**: A statement.
- **evidence**: ev1, ev2
"""
        graph = OKFParser().parse(okf)
        assert "f1" in graph.facts
        assert graph.facts["f1"].statement == "A statement."
        assert graph.facts["f1"].evidence_refs == ["ev1", "ev2"]

    def test_parse_relationship(self) -> None:
        okf = """\
## Relationship: r1
- **source**: ent1
- **target**: ent2
- **type**: depends_on
- **evidence**: ev1
"""
        graph = OKFParser().parse(okf)
        assert "r1" in graph.relationships
        rel = graph.relationships["r1"]
        assert rel.source_id == "ent1"
        assert rel.target_id == "ent2"
        assert rel.relationship_type == "depends_on"
        assert rel.evidence_refs == ["ev1"]

    def test_parse_evidence(self) -> None:
        okf = """\
## Evidence: ev1
- **content**: Some content.
- **source**: https://example.com
"""
        graph = OKFParser().parse(okf)
        assert "ev1" in graph.evidence
        assert graph.evidence["ev1"].content == "Some content."
        assert graph.evidence["ev1"].source == "https://example.com"

    def test_parse_multi_line_value(self) -> None:
        okf = """\
## Entity: python
- **description**: First line.
  Second line.
  Third line.
"""
        graph = OKFParser().parse(okf)
        assert graph.entities["python"].description == "First line.\nSecond line.\nThird line."

    def test_parse_unknown_section_type(self) -> None:
        okf = """\
## Unknown: something
- **name**: test
"""
        with pytest.raises(ParseError, match="Unknown section type"):
            OKFParser().parse(okf)

    def test_parse_all_types(self) -> None:
        okf = """\
# Open Knowledge Format

## Entity: python
- **name**: Python

## Concept: typing
- **name**: Typing

## Fact: f1
- **statement**: A fact.

## Relationship: r1
- **source**: python
- **target**: typing
- **type**: relates

## Evidence: ev1
- **content**: Content.
- **source**: src
"""
        graph = OKFParser().parse(okf)
        assert "python" in graph.entities
        assert "typing" in graph.concepts
        assert "f1" in graph.facts
        assert "r1" in graph.relationships
        assert "ev1" in graph.evidence

    def test_parse_default_confidence_and_verification(self) -> None:
        okf = """\
## Entity: e1
- **name**: Test
"""
        graph = OKFParser().parse(okf)
        assert graph.entities["e1"].confidence == 0.0
        assert graph.entities["e1"].verification_state == VerificationState.PENDING


class TestOKFSerializer:
    def test_serialize_empty(self) -> None:
        result = OKFSerializer().serialize(KnowledgeGraph())
        assert result == "# Open Knowledge Format\n"

    def test_serialize_entity(self) -> None:
        graph = KnowledgeGraph().add_entity(Entity(id="python", name="Python", aliases=["Py"]))
        result = OKFSerializer().serialize(graph)
        assert "## Entity: python" in result
        assert "- **name**: Python" in result
        assert "- **aliases**: Py" in result

    def test_serialize_omits_defaults(self) -> None:
        graph = KnowledgeGraph().add_entity(Entity(id="e1", name="Test"))
        result = OKFSerializer().serialize(graph)
        assert "- **confidence**:" not in result
        assert "- **verification**:" not in result
        assert "- **aliases**:" not in result

    def test_serialize_includes_non_defaults(self) -> None:
        graph = KnowledgeGraph().add_entity(
            Entity(
                id="e1",
                name="Test",
                confidence=0.8,
                verification_state=VerificationState.VERIFIED,
                aliases=["A", "B"],
            )
        )
        result = OKFSerializer().serialize(graph)
        assert "- **confidence**: 0.80" in result
        assert "- **verification**: verified" in result
        assert "- **aliases**: A, B" in result

    def test_deterministic_order(self) -> None:
        graph = KnowledgeGraph()
        graph = graph.add_entity(Entity(id="z", name="Z"))
        graph = graph.add_entity(Entity(id="a", name="A"))
        graph = graph.add_entity(Entity(id="m", name="M"))
        result = OKFSerializer().serialize(graph)
        # Entities should appear in ID order: a, m, z
        a_pos = result.index("## Entity: a")
        m_pos = result.index("## Entity: m")
        z_pos = result.index("## Entity: z")
        assert a_pos < m_pos < z_pos

    def test_element_order_by_type(self) -> None:
        graph = KnowledgeGraph()
        graph = graph.add_fact(Fact(id="f1", statement="A fact"))
        graph = graph.add_entity(Entity(id="e1", name="Entity"))
        result = OKFSerializer().serialize(graph)
        # Entities before facts
        e_pos = result.index("## Entity: e1")
        f_pos = result.index("## Fact: f1")
        assert e_pos < f_pos

    def test_multi_line_value(self) -> None:
        graph = KnowledgeGraph().add_entity(
            Entity(
                id="python",
                name="Python",
                description="Line one.\nLine two.\nLine three.",
            )
        )
        result = OKFSerializer().serialize(graph)
        assert "- **description**: Line one." in result
        assert "  Line two." in result
        assert "  Line three." in result


class TestOKFRoundTrip:
    def test_round_trip_empty(self) -> None:
        original = KnowledgeGraph()
        serializer = OKFSerializer()
        parser = OKFParser()
        okf = serializer.serialize(original)
        restored = parser.parse(okf)
        assert len(restored.entities) == 0
        assert len(restored.concepts) == 0
        assert len(restored.facts) == 0
        assert len(restored.relationships) == 0
        assert len(restored.evidence) == 0

    def test_round_trip_full(self) -> None:
        original = make_graph()
        serializer = OKFSerializer()
        parser = OKFParser()
        okf = serializer.serialize(original)
        restored = parser.parse(okf)

        # Entities
        assert "python" in restored.entities
        e = restored.entities["python"]
        assert e.name == "Python"
        assert e.aliases == ["Py", "CPython"]
        assert e.description == "A programming language."
        assert e.confidence == 0.95
        assert e.verification_state == VerificationState.VERIFIED

        # Concepts
        assert "dynamic-typing" in restored.concepts
        c = restored.concepts["dynamic-typing"]
        assert c.name == "Dynamic Typing"
        assert c.description == "Runtime type checking."

        # Facts
        assert "python-dynamic" in restored.facts
        f = restored.facts["python-dynamic"]
        assert f.statement == "Python uses dynamic typing."
        assert f.evidence_refs == ["ev-001"]

        # Relationships
        assert "py-uses-dynamic" in restored.relationships
        r = restored.relationships["py-uses-dynamic"]
        assert r.source_id == "python"
        assert r.target_id == "dynamic-typing"
        assert r.relationship_type == "uses"
        assert r.evidence_refs == ["ev-001"]

        # Evidence
        assert "ev-001" in restored.evidence
        ev = restored.evidence["ev-001"]
        assert ev.content == "Python is dynamically typed."
        assert ev.source == "https://docs.python.org/3/"

    def test_round_trip_single_entity(self) -> None:
        original = KnowledgeGraph().add_entity(
            Entity(id="e1", name="Test", description="Desc.", confidence=0.5)
        )
        okf = OKFSerializer().serialize(original)
        restored = OKFParser().parse(okf)
        assert restored.entities["e1"].name == "Test"
        assert restored.entities["e1"].description == "Desc."
        assert restored.entities["e1"].confidence == 0.5

    def test_round_trip_multi_line(self) -> None:
        original = KnowledgeGraph().add_entity(
            Entity(
                id="e1",
                name="Multi",
                description="Line 1\nLine 2\nLine 3",
            )
        )
        okf = OKFSerializer().serialize(original)
        restored = OKFParser().parse(okf)
        assert restored.entities["e1"].description == "Line 1\nLine 2\nLine 3"

    def test_round_trip_fact_with_multiple_evidence(self) -> None:
        original = KnowledgeGraph().add_fact(
            Fact(
                id="f1",
                statement="A fact with multiple sources.",
                evidence_refs=["ev1", "ev2", "ev3"],
            )
        )
        okf = OKFSerializer().serialize(original)
        restored = OKFParser().parse(okf)
        assert restored.facts["f1"].evidence_refs == ["ev1", "ev2", "ev3"]

    def test_round_trip_preserves_verification_state(self) -> None:
        for state in VerificationState:
            original = KnowledgeGraph().add_entity(
                Entity(id="e1", name="Test", verification_state=state)
            )
            okf = OKFSerializer().serialize(original)
            restored = OKFParser().parse(okf)
            assert restored.entities["e1"].verification_state == state

    def test_round_trip_preserves_confidence(self) -> None:
        for conf in [0.0, 0.25, 0.5, 0.75, 1.0]:
            original = KnowledgeGraph().add_entity(Entity(id="e1", name="Test", confidence=conf))
            okf = OKFSerializer().serialize(original)
            restored = OKFParser().parse(okf)
            assert restored.entities["e1"].confidence == conf

    def test_serialize_is_idempotent(self) -> None:
        """Serializing the same graph twice produces identical output."""
        graph = make_graph()
        serializer = OKFSerializer()
        first = serializer.serialize(graph)
        second = serializer.serialize(graph)
        assert first == second

    def test_parse_is_deterministic(self) -> None:
        """Parsing the same OKF twice produces semantically equivalent graphs."""
        graph = make_graph()
        okf = OKFSerializer().serialize(graph)
        parser = OKFParser()
        first = parser.parse(okf)
        second = parser.parse(okf)
        assert semantic_eq(first, second)

    def test_cycle_detection_invalid_type(self) -> None:
        """Parser raises ParseError for invalid section types."""
        with pytest.raises(ParseError):
            OKFParser().parse("## Widget: w1\n- **name**: test\n")


class TestProvenanceMetadataRoundTrip:
    def test_round_trip_provenance(self) -> None:
        from knowledge.models import Provenance

        prov = Provenance(
            source_id="src_001", extractor="test_extractor", verification_cycle="vc_1"
        )
        entity = Entity(id="e1", name="Test", provenance=prov)
        graph = KnowledgeGraph().add_entity(entity)
        okf = OKFSerializer().serialize(graph)
        restored = OKFParser().parse(okf)
        rp = restored.entities["e1"].provenance
        assert rp is not None
        assert rp.source_id == "src_001"
        assert rp.extractor == "test_extractor"
        assert rp.verification_cycle == "vc_1"

    def test_round_trip_metadata_tags(self) -> None:
        from knowledge.models import Metadata

        meta = Metadata(tags=["ai", "knowledge"], version=2)
        entity = Entity(id="e1", name="Test", metadata=meta)
        graph = KnowledgeGraph().add_entity(entity)
        okf = OKFSerializer().serialize(graph)
        restored = OKFParser().parse(okf)
        rm = restored.entities["e1"].metadata
        assert rm.tags == ["ai", "knowledge"]
        assert rm.version == 2

    def test_round_trip_provenance_and_metadata(self) -> None:
        from knowledge.models import Metadata, Provenance

        prov = Provenance(source_id="src_001", extractor="ext")
        meta = Metadata(tags=["test"])
        entity = Entity(id="e1", name="Test", provenance=prov, metadata=meta)
        graph = KnowledgeGraph().add_entity(entity)
        okf = OKFSerializer().serialize(graph)
        restored = OKFParser().parse(okf)
        assert restored.entities["e1"].provenance is not None
        assert restored.entities["e1"].provenance.source_id == "src_001"
        assert restored.entities["e1"].metadata.tags == ["test"]

    def test_omits_provenance_when_missing(self) -> None:
        entity = Entity(id="e1", name="Test")
        graph = KnowledgeGraph().add_entity(entity)
        okf = OKFSerializer().serialize(graph)
        assert "provenance_source" not in okf
        restored = OKFParser().parse(okf)
        assert restored.entities["e1"].provenance is None


def semantic_dump(graph: KnowledgeGraph) -> dict:
    """Strip ephemeral timestamp fields for semantic comparison."""
    data = graph.model_dump()
    for collection in data.values():
        for obj in collection.values():
            if "metadata" in obj and obj["metadata"] is not None:
                obj["metadata"].pop("created_at", None)
                obj["metadata"].pop("updated_at", None)
            if "provenance" in obj and obj["provenance"] is not None:
                obj["provenance"].pop("extracted_at", None)
    return data


def semantic_eq(a: KnowledgeGraph, b: KnowledgeGraph) -> bool:
    return semantic_dump(a) == semantic_dump(b)


@pytest.fixture
def complex_okf() -> str:
    return """\
# Open Knowledge Format

## Entity: python
- **name**: Python
- **aliases**: Py, CPython
- **description**: A high-level programming language.
  It supports multiple paradigms.
- **confidence**: 0.95
- **verification**: verified

## Concept: dynamic-typing
- **name**: Dynamic Typing
- **description**: Type checking at runtime.

## Fact: python-dynamic
- **statement**: Python uses dynamic typing.
- **evidence**: ev-001
- **confidence**: 0.90

## Relationship: py-uses-dynamic
- **source**: python
- **target**: dynamic-typing
- **type**: uses
- **evidence**: ev-001

## Evidence: ev-001
- **content**: Python is a dynamically typed language.
- **source**: https://docs.python.org/3/
"""


class TestComplexOKF:
    def test_parse_complex(self, complex_okf: str) -> None:
        graph = OKFParser().parse(complex_okf)
        assert len(graph.entities) == 1
        assert len(graph.concepts) == 1
        assert len(graph.facts) == 1
        assert len(graph.relationships) == 1
        assert len(graph.evidence) == 1

        entity = graph.entities["python"]
        desc = "A high-level programming language.\nIt supports multiple paradigms."
        assert entity.description == desc
        assert entity.confidence == 0.95
        assert entity.verification_state == VerificationState.VERIFIED

    def test_round_trip_complex(self, complex_okf: str) -> None:
        original = OKFParser().parse(complex_okf)
        okf = OKFSerializer().serialize(original)
        restored = OKFParser().parse(okf)
        assert semantic_eq(original, restored)
