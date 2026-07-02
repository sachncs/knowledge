"""Tests for the canonical Knowledge Model domain models."""

from datetime import datetime

import pytest
from pydantic import ValidationError

from knowledge.models import (
    Concept,
    Entity,
    Evidence,
    Fact,
    KnowledgeGraph,
    Metadata,
    Provenance,
    Relationship,
    VerificationState,
)
from knowledge.models.base import KnowledgeModel


class TestVerificationState:
    def test_members(self) -> None:
        assert VerificationState.PENDING.value == "pending"
        assert VerificationState.VERIFIED.value == "verified"
        assert VerificationState.INFERRED.value == "inferred"
        assert VerificationState.DEPRECATED.value == "deprecated"
        assert VerificationState.CONFLICTED.value == "conflicted"

    def test_default_is_pending(self) -> None:
        model = KnowledgeModel()
        assert model.verification_state == VerificationState.PENDING


class TestMetadata:
    def test_defaults(self) -> None:
        meta = Metadata()
        assert isinstance(meta.created_at, datetime)
        assert isinstance(meta.updated_at, datetime)
        assert meta.tags == []
        assert meta.version == 1

    def test_immutable(self) -> None:
        meta = Metadata()
        with pytest.raises(ValidationError):
            meta.version = 2

    def test_serialization_round_trip(self) -> None:
        meta = Metadata(tags=["ai", "knowledge"], version=3)
        data = meta.model_dump()
        restored = Metadata.model_validate(data)
        assert restored.tags == ["ai", "knowledge"]
        assert restored.version == 3


class TestProvenance:
    def test_required_source(self) -> None:
        prov = Provenance(source_id="src_001")
        assert prov.source_id == "src_001"
        assert prov.extractor == "unknown"

    def test_immutable(self) -> None:
        prov = Provenance(source_id="src_001")
        with pytest.raises(ValidationError):
            prov.extractor = "custom"


class TestKnowledgeModel:
    def test_default_id_generated(self) -> None:
        a = KnowledgeModel()
        b = KnowledgeModel()
        assert a.id != b.id

    def test_id_is_string(self) -> None:
        model = KnowledgeModel()
        assert isinstance(model.id, str)

    def test_default_confidence(self) -> None:
        model = KnowledgeModel()
        assert model.confidence == 0.0

    def test_confidence_range(self) -> None:
        KnowledgeModel(confidence=0.0)
        KnowledgeModel(confidence=1.0)
        KnowledgeModel(confidence=0.5)
        with pytest.raises(ValidationError):
            KnowledgeModel(confidence=-0.1)
        with pytest.raises(ValidationError):
            KnowledgeModel(confidence=1.1)

    def test_default_verification_state(self) -> None:
        model = KnowledgeModel()
        assert model.verification_state == VerificationState.PENDING

    def test_provenance_optional(self) -> None:
        model = KnowledgeModel()
        assert model.provenance is None
        prov = Provenance(source_id="src_001")
        model_with = KnowledgeModel(provenance=prov)
        assert model_with.provenance is not None

    def test_immutable(self) -> None:
        model = KnowledgeModel()
        with pytest.raises(ValidationError):
            model.confidence = 0.5

    def test_serialization_round_trip(self) -> None:
        prov = Provenance(source_id="src_001", extractor="test")
        meta = Metadata(tags=["test"])
        original = KnowledgeModel(
            id="test_id",
            confidence=0.8,
            verification_state=VerificationState.VERIFIED,
            provenance=prov,
            metadata=meta,
        )
        data = original.model_dump()
        restored = KnowledgeModel.model_validate(data)
        assert restored.id == "test_id"
        assert restored.confidence == 0.8
        assert restored.verification_state == VerificationState.VERIFIED
        assert restored.provenance is not None
        assert restored.provenance.source_id == "src_001"
        assert restored.metadata.tags == ["test"]


class TestEntity:
    def test_required_name(self) -> None:
        entity = Entity(name="Python")
        assert entity.name == "Python"

    def test_name_empty_string(self) -> None:
        Entity(name="")

    def test_default_aliases(self) -> None:
        entity = Entity(name="Python")
        assert entity.aliases == []

    def test_with_aliases(self) -> None:
        entity = Entity(name="Python", aliases=["Py", "CPython"])
        assert len(entity.aliases) == 2

    def test_description_optional(self) -> None:
        entity = Entity(name="Python")
        assert entity.description is None
        entity_with = Entity(name="Python", description="A programming language")
        assert entity_with.description == "A programming language"

    def test_immutable(self) -> None:
        entity = Entity(name="Python")
        with pytest.raises(ValidationError):
            entity.name = "Java"

    def test_serialization_round_trip(self) -> None:
        original = Entity(
            name="Python",
            aliases=["Py"],
            description="A programming language",
            confidence=0.9,
        )
        data = original.model_dump()
        restored = Entity.model_validate(data)
        assert restored.name == "Python"
        assert restored.aliases == ["Py"]
        assert restored.description == "A programming language"
        assert restored.confidence == 0.9

    def test_inherits_base_fields(self) -> None:
        entity = Entity(name="Python")
        assert entity.id is not None
        assert isinstance(entity.confidence, float)
        assert isinstance(entity.verification_state, VerificationState)


class TestConcept:
    def test_required_name(self) -> None:
        concept = Concept(name="Machine Learning")
        assert concept.name == "Machine Learning"

    def test_description_optional(self) -> None:
        concept = Concept(name="ML")
        assert concept.description is None

    def test_immutable(self) -> None:
        concept = Concept(name="ML")
        with pytest.raises(ValidationError):
            concept.name = "Deep Learning"

    def test_serialization_round_trip(self) -> None:
        original = Concept(name="Ontology", description="A formal naming")
        data = original.model_dump()
        restored = Concept.model_validate(data)
        assert restored.name == "Ontology"
        assert restored.description == "A formal naming"


class TestFact:
    def test_required_statement(self) -> None:
        fact = Fact(statement="Python supports async programming.")
        assert fact.statement is not None

    def test_default_evidence_refs(self) -> None:
        fact = Fact(statement="Python supports async.")
        assert fact.evidence_refs == []

    def test_with_evidence_refs(self) -> None:
        fact = Fact(
            statement="Python supports async.",
            evidence_refs=["ev_001", "ev_002"],
        )
        assert len(fact.evidence_refs) == 2

    def test_immutable(self) -> None:
        fact = Fact(statement="A fact.")
        with pytest.raises(ValidationError):
            fact.statement = "Changed."

    def test_serialization_round_trip(self) -> None:
        original = Fact(
            statement="Python is dynamically typed.",
            evidence_refs=["ev_001"],
        )
        data = original.model_dump()
        restored = Fact.model_validate(data)
        assert restored.statement == "Python is dynamically typed."
        assert restored.evidence_refs == ["ev_001"]


class TestRelationship:
    def test_required_fields(self) -> None:
        rel = Relationship(
            source_id="ent_001",
            target_id="ent_002",
            relationship_type="depends_on",
        )
        assert rel.source_id == "ent_001"
        assert rel.target_id == "ent_002"
        assert rel.relationship_type == "depends_on"

    def test_default_evidence_refs(self) -> None:
        rel = Relationship(
            source_id="a", target_id="b", relationship_type="uses"
        )
        assert rel.evidence_refs == []

    def test_immutable(self) -> None:
        rel = Relationship(
            source_id="a", target_id="b", relationship_type="uses"
        )
        with pytest.raises(ValidationError):
            rel.relationship_type = "extends"

    def test_serialization_round_trip(self) -> None:
        original = Relationship(
            source_id="ent_001",
            target_id="ent_002",
            relationship_type="implements",
            evidence_refs=["ev_001"],
        )
        data = original.model_dump()
        restored = Relationship.model_validate(data)
        assert restored.source_id == "ent_001"
        assert restored.target_id == "ent_002"
        assert restored.relationship_type == "implements"
        assert restored.evidence_refs == ["ev_001"]


class TestEvidence:
    def test_required_fields(self) -> None:
        ev = Evidence(content="Some text.", source="doc.md")
        assert ev.content == "Some text."
        assert ev.source == "doc.md"

    def test_immutable(self) -> None:
        ev = Evidence(content="Text.", source="doc.md")
        with pytest.raises(ValidationError):
            ev.content = "Changed."

    def test_serialization_round_trip(self) -> None:
        original = Evidence(
            content="API documentation section.",
            source="https://example.com/api",
        )
        data = original.model_dump()
        restored = Evidence.model_validate(data)
        assert restored.content == "API documentation section."
        assert restored.source == "https://example.com/api"


class TestKnowledgeGraph:
    def test_empty_graph(self) -> None:
        graph = KnowledgeGraph()
        assert graph.entities == {}
        assert graph.concepts == {}
        assert graph.facts == {}
        assert graph.relationships == {}
        assert graph.evidence == {}

    def test_add_entity(self) -> None:
        graph = KnowledgeGraph()
        entity = Entity(name="Python")
        updated = graph.add_entity(entity)
        assert entity.id in updated.entities
        assert updated.entities[entity.id].name == "Python"
        assert entity.id not in graph.entities  # original unchanged

    def test_add_concept(self) -> None:
        graph = KnowledgeGraph()
        concept = Concept(name="ML")
        updated = graph.add_concept(concept)
        assert concept.id in updated.concepts

    def test_add_fact(self) -> None:
        graph = KnowledgeGraph()
        fact = Fact(statement="A statement.")
        updated = graph.add_fact(fact)
        assert fact.id in updated.facts

    def test_add_relationship(self) -> None:
        graph = KnowledgeGraph()
        rel = Relationship(
            source_id="a", target_id="b", relationship_type="uses"
        )
        updated = graph.add_relationship(rel)
        assert rel.id in updated.relationships

    def test_add_evidence(self) -> None:
        graph = KnowledgeGraph()
        ev = Evidence(content="Text.", source="doc.md")
        updated = graph.add_evidence(ev)
        assert ev.id in updated.evidence

    def test_remove_entity(self) -> None:
        entity = Entity(name="Python")
        graph = KnowledgeGraph().add_entity(entity)
        updated = graph.remove_entity(entity.id)
        assert entity.id not in updated.entities
        assert entity.id in graph.entities  # original unchanged

    def test_remove_concept(self) -> None:
        concept = Concept(name="ML")
        graph = KnowledgeGraph().add_concept(concept)
        updated = graph.remove_concept(concept.id)
        assert concept.id not in updated.concepts

    def test_remove_fact(self) -> None:
        fact = Fact(statement="A fact.")
        graph = KnowledgeGraph().add_fact(fact)
        updated = graph.remove_fact(fact.id)
        assert fact.id not in updated.facts

    def test_remove_relationship(self) -> None:
        rel = Relationship(
            source_id="a", target_id="b", relationship_type="uses"
        )
        graph = KnowledgeGraph().add_relationship(rel)
        updated = graph.remove_relationship(rel.id)
        assert rel.id not in updated.relationships

    def test_remove_evidence(self) -> None:
        ev = Evidence(content="Text.", source="doc.md")
        graph = KnowledgeGraph().add_evidence(ev)
        updated = graph.remove_evidence(ev.id)
        assert ev.id not in updated.evidence

    def test_immutable(self) -> None:
        graph = KnowledgeGraph()
        with pytest.raises(ValidationError):
            graph.entities = {}

    def test_multiple_additions(self) -> None:
        graph = KnowledgeGraph()
        e1 = Entity(name="Python")
        e2 = Entity(name="Java")
        graph = graph.add_entity(e1).add_entity(e2)
        assert len(graph.entities) == 2

    def test_serialization_round_trip(self) -> None:
        entity = Entity(name="Python")
        concept = Concept(name="Programming")
        graph = KnowledgeGraph().add_entity(entity).add_concept(concept)
        data = graph.model_dump()
        restored = KnowledgeGraph.model_validate(data)
        assert entity.id in restored.entities
        assert concept.id in restored.concepts
        assert restored.entities[entity.id].name == "Python"
