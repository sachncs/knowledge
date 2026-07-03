"""Tests for the Verification Engine."""

from knowledge.engine import VerificationEngine, VerificationResult
from knowledge.models import Entity, Evidence, Fact, KnowledgeGraph
from knowledge.passes import (
    ConsistencyValidationPass,
    SchemaValidationPass,
    ScoringPass,
    StructuralValidationPass,
)
from knowledge.passes.repair_passes import (
    AttachProvenancePass,
    FixEvidenceRefsPass,
    MergeDuplicateEntitiesPass,
)


class TestVerificationResult:
    def test_defaults(self) -> None:
        result = VerificationResult(graph=KnowledgeGraph())
        assert result.score.overall == 0.0
        assert result.diagnostics == []
        assert result.repairs_applied == 0
        assert result.iteration_count == 1
        assert result.converged is True

    def test_with_data(self) -> None:
        graph = KnowledgeGraph()
        graph = graph.add_entity(Entity(name="Python", id="ent_001"))
        result = VerificationResult(
            graph=graph,
            repairs_applied=3,
            iteration_count=2,
            converged=False,
            threshold_met=False,
        )
        assert result.repairs_applied == 3
        assert result.iteration_count == 2
        assert "ent_001" in result.graph.entities


class TestVerificationEngine:
    def test_verify_empty_graph(self) -> None:
        engine = VerificationEngine()
        result = engine.verify(KnowledgeGraph())
        assert isinstance(result, VerificationResult)
        assert result.converged is True

    def test_verify_detects_missing_evidence(self) -> None:
        graph = KnowledgeGraph()
        graph = graph.add_fact(Fact(statement="Python is great.", id="f_001"))
        engine = VerificationEngine()
        result = engine.verify(graph)
        assert len(result.diagnostics) > 0
        evidence_warnings = [d for d in result.diagnostics if "evidence" in d.message.lower()]
        assert len(evidence_warnings) > 0

    def test_verify_with_repair_attaches_provenance(self) -> None:
        graph = KnowledgeGraph()
        graph = graph.add_entity(Entity(name="Python", id="ent_001"))
        engine = VerificationEngine()
        engine.pass_manager.register(AttachProvenancePass())
        engine.pass_manager.register(SchemaValidationPass())
        engine.pass_manager.register(StructuralValidationPass())
        engine.pass_manager.register(ConsistencyValidationPass())
        engine.pass_manager.register(ScoringPass())
        result = engine.verify(graph)
        # The entity should now have provenance
        for entity in result.graph.entities.values():
            if entity.name == "Python":
                assert entity.provenance is not None

    def test_verify_with_repair_merges_duplicates(self) -> None:
        graph = KnowledgeGraph()
        graph = graph.add_entity(Entity(name="Python", id="ent_001"))
        graph = graph.add_entity(Entity(name="Python", id="ent_002"))
        engine = VerificationEngine()
        engine.pass_manager.register(MergeDuplicateEntitiesPass())
        engine.pass_manager.register(SchemaValidationPass())
        engine.pass_manager.register(StructuralValidationPass())
        engine.pass_manager.register(ConsistencyValidationPass())
        engine.pass_manager.register(ScoringPass())
        result = engine.verify(graph)
        assert len(result.graph.entities) == 1

    def test_verify_fixes_broken_evidence_refs(self) -> None:
        graph = KnowledgeGraph()
        graph = graph.add_evidence(
            Evidence(content="Python is a language.", source="doc.md", id="ev_001")
        )
        graph = graph.add_fact(
            Fact(
                statement="Python is a language.",
                evidence_refs=["ev_001", "ev_missing"],
                id="f_001",
            )
        )
        engine = VerificationEngine()
        engine.pass_manager.register(FixEvidenceRefsPass())
        engine.pass_manager.register(SchemaValidationPass())
        engine.pass_manager.register(StructuralValidationPass())
        engine.pass_manager.register(ConsistencyValidationPass())
        engine.pass_manager.register(ScoringPass())
        result = engine.verify(graph)
        for fact in result.graph.facts.values():
            assert "ev_missing" not in fact.evidence_refs
            assert "ev_001" in fact.evidence_refs

    def test_verify_uses_default_passes(self) -> None:
        engine = VerificationEngine()
        assert engine.pass_manager.registered_ids == []
        engine.verify(KnowledgeGraph())
        # Default passes should be registered automatically
        assert len(engine.pass_manager.registered_ids) > 0
        assert "verification.schema" in engine.pass_manager.registered_ids
        assert "scoring.quality" in engine.pass_manager.registered_ids
        assert "repair.merge_entities" in engine.pass_manager.registered_ids

    def test_verify_threshold(self) -> None:
        engine = VerificationEngine()
        result = engine.verify(KnowledgeGraph(), threshold=0.0)
        assert result.threshold_met is True

    def test_verify_max_iterations(self) -> None:
        graph = KnowledgeGraph()
        graph = graph.add_entity(Entity(name="Python", id="ent_001"))
        engine = VerificationEngine()
        result = engine.verify(graph, max_iterations=1)
        assert result.iteration_count <= 1
