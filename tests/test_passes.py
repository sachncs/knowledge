"""Tests for the compiler pass framework."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from knowledge.models import (
    Concept,
    Entity,
    Evidence,
    Fact,
    KnowledgeGraph,
    Relationship,
)
from knowledge.passes import (
    CompilerPass,
    Diagnostic,
    PassManager,
    PassResult,
    Phase,
    Severity,
)
from knowledge.passes.scoring_pass import ScoringPass


class TestPhase:
    def test_members(self) -> None:
        assert Phase.PARSER.value == "parser"
        assert Phase.EXTRACTION.value == "extraction"
        assert Phase.NORMALIZATION.value == "normalization"
        assert Phase.ANALYSIS.value == "analysis"
        assert Phase.VERIFICATION.value == "verification"
        assert Phase.REPAIR.value == "repair"
        assert Phase.SCORING.value == "scoring"
        assert Phase.SERIALIZATION.value == "serialization"

    def test_order(self) -> None:
        """Validate the intended pipeline order."""
        order = [
            Phase.PARSER,
            Phase.EXTRACTION,
            Phase.NORMALIZATION,
            Phase.ANALYSIS,
            Phase.VERIFICATION,
            Phase.REPAIR,
            Phase.SCORING,
            Phase.SERIALIZATION,
        ]
        assert list(Phase) == order


class TestSeverity:
    def test_members(self) -> None:
        assert Severity.ERROR.value == "error"
        assert Severity.WARNING.value == "warning"
        assert Severity.SUGGESTION.value == "suggestion"
        assert Severity.INFORMATION.value == "information"


class TestDiagnostic:
    def test_required_fields(self) -> None:
        diag = Diagnostic(severity=Severity.ERROR, message="Something broke")
        assert diag.severity == Severity.ERROR
        assert diag.message == "Something broke"

    def test_defaults(self) -> None:
        diag = Diagnostic(severity=Severity.WARNING, message="Warning")
        assert diag.explanation is None
        assert diag.location is None
        assert diag.affected_objects == []
        assert diag.suggested_fix is None

    def test_all_fields(self) -> None:
        diag = Diagnostic(
            severity=Severity.ERROR,
            message="Missing evidence",
            explanation="Entity 'X' has no supporting evidence.",
            location="Entity: X",
            affected_objects=["X"],
            suggested_fix="Add evidence reference.",
        )
        assert diag.explanation == "Entity 'X' has no supporting evidence."
        assert diag.location == "Entity: X"
        assert diag.affected_objects == ["X"]
        assert diag.suggested_fix == "Add evidence reference."

    def test_immutable(self) -> None:
        diag = Diagnostic(severity=Severity.INFORMATION, message="Info")
        with pytest.raises(ValidationError):
            diag.message = "Changed"

    def test_serialization_round_trip(self) -> None:
        original = Diagnostic(
            severity=Severity.ERROR,
            message="Test",
            location="loc",
        )
        data = original.model_dump()
        restored = Diagnostic.model_validate(data)
        assert restored.severity == Severity.ERROR
        assert restored.message == "Test"
        assert restored.location == "loc"


class TestPassResult:
    def test_requires_graph(self) -> None:
        graph = KnowledgeGraph()
        result = PassResult(graph=graph)
        assert result.graph is graph
        assert result.diagnostics == []

    def test_with_diagnostics(self) -> None:
        graph = KnowledgeGraph()
        diag = Diagnostic(severity=Severity.INFORMATION, message="Info")
        result = PassResult(graph=graph, diagnostics=[diag])
        assert len(result.diagnostics) == 1

    def test_immutable(self) -> None:
        result = PassResult(graph=KnowledgeGraph())
        with pytest.raises(ValidationError):
            result.graph = KnowledgeGraph()


# --- Concrete passes for testing ---


class NoOpPass(CompilerPass):
    id = "test.noop"
    phase = Phase.NORMALIZATION
    description = "Does nothing"

    def execute(self, graph: KnowledgeGraph, config: dict | None = None) -> PassResult:
        return PassResult(graph=graph)


class AddEntityPass(CompilerPass):
    id = "test.add_entity"
    phase = Phase.NORMALIZATION
    description = "Adds an entity to the graph"

    def __init__(self, entity_name: str = "TestEntity") -> None:
        self._entity_name = entity_name

    def execute(self, graph: KnowledgeGraph, config: dict | None = None) -> PassResult:
        entity = Entity(name=self._entity_name)
        return PassResult(graph=graph.add_entity(entity))


class WarningPass(CompilerPass):
    id = "test.warning"
    phase = Phase.VERIFICATION
    description = "Emits a warning diagnostic"

    def execute(self, graph: KnowledgeGraph, config: dict | None = None) -> PassResult:
        diag = Diagnostic(
            severity=Severity.WARNING,
            message="Test warning",
        )
        return PassResult(graph=graph, diagnostics=[diag])


class DependentPass(CompilerPass):
    id = "test.dependent"
    phase = Phase.VERIFICATION
    depends_on = ("test.noop",)
    description = "Depends on NoOpPass"

    def execute(self, graph: KnowledgeGraph, config: dict | None = None) -> PassResult:
        return PassResult(graph=graph)


class MultiDepPass(CompilerPass):
    id = "test.multi_dep"
    phase = Phase.ANALYSIS
    depends_on = ("test.noop", "test.add_entity")
    description = "Depends on two passes"

    def execute(self, graph: KnowledgeGraph, config: dict | None = None) -> PassResult:
        return PassResult(graph=graph)


class CountingPass(CompilerPass):
    id = "test.counting"
    phase = Phase.ANALYSIS
    description = "Records entity count as metadata"

    def execute(self, graph: KnowledgeGraph, config: dict | None = None) -> PassResult:
        # No metadata field on PassResult, just return graph
        return PassResult(graph=graph)


class TestCompilerPass:
    def test_id_and_phase_required(self) -> None:
        """Concrete passes must define id and phase."""
        noop = NoOpPass()
        assert noop.id == "test.noop"
        assert noop.phase == Phase.NORMALIZATION

    def test_default_version(self) -> None:
        assert NoOpPass().version == "0.1.0"

    def test_execute_noop(self) -> None:
        graph = KnowledgeGraph()
        result = NoOpPass().execute(graph)
        assert result.graph is graph
        assert result.diagnostics == []

    def test_execute_adds_entity(self) -> None:
        graph = KnowledgeGraph()
        result = AddEntityPass("MyEntity").execute(graph)
        assert "MyEntity" in [e.name for e in result.graph.entities.values()]
        assert len(result.graph.entities) == 1

    def test_execute_with_diagnostics(self) -> None:
        graph = KnowledgeGraph()
        result = WarningPass().execute(graph)
        assert len(result.diagnostics) == 1
        assert result.diagnostics[0].severity == Severity.WARNING


class TestPassManager:
    def test_empty_registration(self) -> None:
        mgr = PassManager()
        assert mgr.registered_ids == []

    def test_register(self) -> None:
        mgr = PassManager()
        mgr.register(NoOpPass())
        assert "test.noop" in mgr.registered_ids

    def test_register_duplicate(self) -> None:
        mgr = PassManager()
        mgr.register(NoOpPass())
        with pytest.raises(ValueError, match="already registered"):
            mgr.register(NoOpPass())

    def test_register_empty_id(self) -> None:
        class BadPass(CompilerPass):
            id = ""
            phase = Phase.NORMALIZATION

            def execute(self, graph, config=None):
                return PassResult(graph=graph)

        mgr = PassManager()
        with pytest.raises(ValueError, match="non-empty id"):
            mgr.register(BadPass())

    def test_resolve_order_no_deps(self) -> None:
        mgr = PassManager()
        mgr.register(NoOpPass())
        mgr.register(WarningPass())
        order = mgr.resolve_order()
        assert len(order) == 2
        assert "test.noop" in order
        assert "test.warning" in order

    def test_resolve_order_with_deps(self) -> None:
        mgr = PassManager()
        mgr.register(NoOpPass())
        mgr.register(DependentPass())
        order = mgr.resolve_order()
        assert order.index("test.noop") < order.index("test.dependent")

    def test_resolve_order_multi_dep(self) -> None:
        mgr = PassManager()
        mgr.register(NoOpPass())
        mgr.register(AddEntityPass())
        mgr.register(MultiDepPass())
        order = mgr.resolve_order()
        assert order.index("test.noop") < order.index("test.multi_dep")
        assert order.index("test.add_entity") < order.index("test.multi_dep")

    def test_resolve_order_filter_by_phase(self) -> None:
        mgr = PassManager()
        mgr.register(NoOpPass())  # NORMALIZATION
        mgr.register(WarningPass())  # VERIFICATION
        order = mgr.resolve_order(phases=[Phase.NORMALIZATION])
        assert order == ["test.noop"]

    def test_resolve_order_empty_when_no_match(self) -> None:
        mgr = PassManager()
        mgr.register(NoOpPass())
        order = mgr.resolve_order(phases=[Phase.PARSER])
        assert order == []

    def test_unknown_dependency(self) -> None:
        class BadPass(CompilerPass):
            id = "bad"
            phase = Phase.NORMALIZATION
            depends_on = ("nonexistent",)

            def execute(self, graph, config=None):
                return PassResult(graph=graph)

        mgr = PassManager()
        mgr.register(NoOpPass())
        mgr.register(BadPass())
        with pytest.raises(ValueError, match="Unknown dependency"):
            mgr.resolve_order()

    def test_circular_dependency(self) -> None:
        class PassA(CompilerPass):
            id = "a"
            phase = Phase.NORMALIZATION
            depends_on = ("b",)

            def execute(self, graph, config=None):
                return PassResult(graph=graph)

        class PassB(CompilerPass):
            id = "b"
            phase = Phase.NORMALIZATION
            depends_on = ("a",)

            def execute(self, graph, config=None):
                return PassResult(graph=graph)

        mgr = PassManager()
        mgr.register(PassA())
        mgr.register(PassB())
        with pytest.raises(ValueError, match="Circular dependency"):
            mgr.resolve_order()

    def test_execute_single_pass(self) -> None:
        mgr = PassManager()
        mgr.register(AddEntityPass("MyEntity"))
        result = mgr.execute(KnowledgeGraph())
        assert len(result.graph.entities) == 1
        assert "MyEntity" in [e.name for e in result.graph.entities.values()]
        assert result.executed == ["test.add_entity"]

    def test_execute_multiple_passes(self) -> None:
        mgr = PassManager()
        mgr.register(NoOpPass())
        mgr.register(WarningPass())
        result = mgr.execute(KnowledgeGraph())
        # NoOpPass runs first, then WarningPass
        assert len(result.diagnostics) == 1
        assert result.diagnostics[0].message == "Test warning"

    def test_execute_collects_diagnostics(self) -> None:
        mgr = PassManager()
        mgr.register(WarningPass())

        class InfoPass(CompilerPass):
            id = "test.info"
            phase = Phase.VERIFICATION

            def execute(self, graph, config=None):
                diag = Diagnostic(severity=Severity.INFORMATION, message="Info")
                return PassResult(graph=graph, diagnostics=[diag])

        mgr.register(InfoPass())
        result = mgr.execute(KnowledgeGraph())
        assert len(result.diagnostics) == 2
        severities = {d.severity for d in result.diagnostics}
        assert severities == {Severity.WARNING, Severity.INFORMATION}

    def test_execute_pipeline_metadata(self) -> None:
        mgr = PassManager()
        mgr.register(NoOpPass())
        mgr.register(WarningPass())
        result = mgr.execute(KnowledgeGraph())
        assert len(result.execution_order) == 2
        assert result.execution_order == result.executed

    def test_execute_with_config(self) -> None:
        class ConfigurablePass(CompilerPass):
            id = "test.configurable"
            phase = Phase.NORMALIZATION

            def execute(self, graph, config=None):
                cfg = config or {}
                name = cfg.get("name", "default")
                entity = Entity(name=name)
                return PassResult(graph=graph.add_entity(entity))

        mgr = PassManager()
        mgr.register(ConfigurablePass())
        config = {"test.configurable": {"name": "ConfiguredEntity"}}
        result = mgr.execute(KnowledgeGraph(), config=config)
        names = [e.name for e in result.graph.entities.values()]
        assert "ConfiguredEntity" in names

    def test_execute_preserves_order_with_deps(self) -> None:
        mgr = PassManager()
        mgr.register(NoOpPass())
        mgr.register(DependentPass())
        result = mgr.execute(KnowledgeGraph())
        assert result.executed == ["test.noop", "test.dependent"]
        assert result.execution_order == ["test.noop", "test.dependent"]

    def test_execute_filters_by_phase(self) -> None:
        mgr = PassManager()
        mgr.register(NoOpPass())  # NORMALIZATION
        mgr.register(WarningPass())  # VERIFICATION
        result = mgr.execute(KnowledgeGraph(), phases=[Phase.NORMALIZATION])
        assert result.executed == ["test.noop"]

    def test_execute_empty_pipeline(self) -> None:
        mgr = PassManager()
        result = mgr.execute(KnowledgeGraph())
        assert result.executed == []
        assert result.execution_order == []
        assert len(result.diagnostics) == 0
        assert len(result.graph.entities) == 0

    def test_execute_is_idempotent(self) -> None:
        mgr = PassManager()
        mgr.register(NoOpPass())
        r1 = mgr.execute(KnowledgeGraph())
        r2 = mgr.execute(KnowledgeGraph())
        assert r1.execution_order == r2.execution_order

    def test_registered_ids_property(self) -> None:
        mgr = PassManager()
        assert mgr.registered_ids == []
        mgr.register(NoOpPass())
        mgr.register(WarningPass())
        assert sorted(mgr.registered_ids) == [
            "test.noop",
            "test.warning",
        ]

    def test_dependency_chain(self) -> None:
        """A longer dependency chain resolves correctly."""

        class Pass1(CompilerPass):
            id = "pass1"
            phase = Phase.NORMALIZATION

            def execute(self, graph, config=None):
                return PassResult(graph=graph)

        class Pass2(CompilerPass):
            id = "pass2"
            phase = Phase.NORMALIZATION
            depends_on = ("pass1",)

            def execute(self, graph, config=None):
                return PassResult(graph=graph)

        class Pass3(CompilerPass):
            id = "pass3"
            phase = Phase.NORMALIZATION
            depends_on = ("pass2",)

            def execute(self, graph, config=None):
                return PassResult(graph=graph)

        mgr = PassManager()
        mgr.register(Pass3())
        mgr.register(Pass1())
        mgr.register(Pass2())
        order = mgr.resolve_order()
        assert order.index("pass1") < order.index("pass2") < order.index("pass3")


class TestGraphStatisticsPass:
    def test_empty_graph(self) -> None:
        from knowledge.passes.analysis_pass import GraphStatisticsPass

        result = GraphStatisticsPass().execute(KnowledgeGraph())
        info = [d for d in result.diagnostics if "0 total elements" in d.message]
        assert len(info) == 1

    def test_reports_counts(self) -> None:
        from knowledge.passes.analysis_pass import GraphStatisticsPass

        graph = KnowledgeGraph()
        graph = graph.add_entity(Entity(name="Python", id="e1"))
        graph = graph.add_entity(Entity(name="Java", id="e2"))
        result = GraphStatisticsPass().execute(graph)
        info = [d for d in result.diagnostics if "total elements" in d.message]
        assert len(info) == 1
        assert "2 entities" in info[0].message

    def test_detects_isolated_entities(self) -> None:
        from knowledge.models import Relationship
        from knowledge.passes.analysis_pass import GraphStatisticsPass

        graph = KnowledgeGraph()
        graph = graph.add_entity(Entity(name="Python", id="e1"))
        graph = graph.add_entity(Entity(name="Java", id="e2"))
        graph = graph.add_relationship(
            Relationship(source_id="e1", target_id="e2", relationship_type="uses", id="r1")
        )
        graph = graph.add_entity(Entity(name="Rust", id="e3"))
        result = GraphStatisticsPass().execute(graph)
        isolated = [d for d in result.diagnostics if "no relationships" in d.message]
        assert len(isolated) == 1
        assert "1 of 3" in isolated[0].message


class TestSchemaValidationPass:
    def test_empty_entity_name(self) -> None:
        from knowledge.passes.schema_pass import SchemaValidationPass

        graph = KnowledgeGraph().add_entity(Entity(name="", id="e1"))
        result = SchemaValidationPass().execute(graph)
        errors = [d for d in result.diagnostics if d.severity == Severity.ERROR]
        assert any("empty name" in d.message for d in errors)

    def test_empty_concept_name(self) -> None:
        from knowledge.passes.schema_pass import SchemaValidationPass

        graph = KnowledgeGraph().add_concept(Concept(name="", id="c1"))
        result = SchemaValidationPass().execute(graph)
        errors = [d for d in result.diagnostics if d.severity == Severity.ERROR]
        assert any("empty name" in d.message for d in errors)

    def test_empty_fact_statement(self) -> None:
        from knowledge.passes.schema_pass import SchemaValidationPass

        graph = KnowledgeGraph().add_fact(Fact(statement="", id="f1"))
        result = SchemaValidationPass().execute(graph)
        errors = [d for d in result.diagnostics if d.severity == Severity.ERROR]
        assert any("empty statement" in d.message for d in errors)

    def test_empty_relationship_fields(self) -> None:
        from knowledge.passes.schema_pass import SchemaValidationPass

        r1 = Relationship(source_id="", target_id="b", relationship_type="uses", id="r1")
        r2 = Relationship(source_id="a", target_id="", relationship_type="uses", id="r2")
        r3 = Relationship(source_id="a", target_id="b", relationship_type="", id="r3")
        graph = KnowledgeGraph().add_relationship(r1).add_relationship(r2).add_relationship(r3)
        result = SchemaValidationPass().execute(graph)
        errors = [d for d in result.diagnostics if d.severity == Severity.ERROR]
        assert any("empty source_id" in d.message for d in errors)
        assert any("empty target_id" in d.message for d in errors)
        assert any("empty relationship_type" in d.message for d in errors)

    def test_empty_evidence_fields(self) -> None:
        from knowledge.passes.schema_pass import SchemaValidationPass

        graph = (
            KnowledgeGraph()
            .add_evidence(Evidence(content="", source="doc.md", id="ev1"))
            .add_evidence(Evidence(content="text", source="", id="ev2"))
        )
        result = SchemaValidationPass().execute(graph)
        errors = [d for d in result.diagnostics if d.severity == Severity.ERROR]
        assert any("empty content" in d.message for d in errors)
        warnings = [d for d in result.diagnostics if d.severity == Severity.WARNING]
        assert any("empty source" in d.message for d in warnings)

    def test_cross_collection_duplicate_ids(self) -> None:
        from knowledge.passes.schema_pass import SchemaValidationPass

        graph = (
            KnowledgeGraph()
            .add_entity(Entity(id="dup", name="Entity"))
            .add_concept(Concept(id="dup", name="Concept"))
        )
        result = SchemaValidationPass().execute(graph)
        errors = [d for d in result.diagnostics if d.severity == Severity.ERROR]
        assert any("Duplicate id" in d.message for d in errors)

    def test_valid_graph_passes_clean(self) -> None:
        from knowledge.passes.schema_pass import SchemaValidationPass

        rel = Relationship(source_id="e1", target_id="e1", relationship_type="uses", id="r1")
        graph = (
            KnowledgeGraph()
            .add_entity(Entity(name="Python", id="e1"))
            .add_concept(Concept(name="Language", id="c1"))
            .add_fact(Fact(statement="Python is a language.", id="f1"))
            .add_relationship(rel)
            .add_evidence(Evidence(content="Some text.", source="doc.md", id="ev1"))
        )
        result = SchemaValidationPass().execute(graph)
        assert len(result.diagnostics) == 0


class TestStructuralValidationPass:
    def test_orphaned_relationship_source(self) -> None:
        from knowledge.passes.structural_pass import StructuralValidationPass

        rel = Relationship(source_id="ghost", target_id="e1", relationship_type="uses", id="r1")
        graph = KnowledgeGraph().add_entity(Entity(name="Python", id="e1")).add_relationship(rel)
        result = StructuralValidationPass().execute(graph)
        errors = [d for d in result.diagnostics if d.severity == Severity.ERROR]
        assert any("source" in d.message and "not found" in d.message for d in errors)

    def test_orphaned_relationship_target(self) -> None:
        from knowledge.passes.structural_pass import StructuralValidationPass

        rel = Relationship(source_id="e1", target_id="ghost", relationship_type="uses", id="r1")
        graph = KnowledgeGraph().add_entity(Entity(name="Python", id="e1")).add_relationship(rel)
        result = StructuralValidationPass().execute(graph)
        errors = [d for d in result.diagnostics if d.severity == Severity.ERROR]
        assert any("target" in d.message and "not found" in d.message for d in errors)

    def test_duplicate_aliases(self) -> None:
        from knowledge.passes.structural_pass import StructuralValidationPass

        graph = KnowledgeGraph().add_entity(
            Entity(name="Py", aliases=["python", "Python"], id="e1")
        )
        result = StructuralValidationPass().execute(graph)
        warnings = [d for d in result.diagnostics if d.severity == Severity.WARNING]
        assert any("duplicate aliases" in d.message for d in warnings)

    def test_circular_dependency(self) -> None:
        from knowledge.passes.structural_pass import StructuralValidationPass

        r1 = Relationship(source_id="a", target_id="b", relationship_type="uses", id="r1")
        r2 = Relationship(source_id="b", target_id="c", relationship_type="uses", id="r2")
        r3 = Relationship(source_id="c", target_id="a", relationship_type="uses", id="r3")
        graph = (
            KnowledgeGraph()
            .add_entity(Entity(name="A", id="a"))
            .add_entity(Entity(name="B", id="b"))
            .add_entity(Entity(name="C", id="c"))
            .add_relationship(r1)
            .add_relationship(r2)
            .add_relationship(r3)
        )
        result = StructuralValidationPass().execute(graph)
        warnings = [d for d in result.diagnostics if d.severity == Severity.WARNING]
        assert any("circular" in d.message.lower() for d in warnings)

    def test_clean_graph_passes(self) -> None:
        from knowledge.passes.structural_pass import StructuralValidationPass

        rel = Relationship(source_id="a", target_id="b", relationship_type="uses", id="r1")
        graph = (
            KnowledgeGraph()
            .add_entity(Entity(name="A", id="a"))
            .add_entity(Entity(name="B", id="b"))
            .add_relationship(rel)
        )
        result = StructuralValidationPass().execute(graph)
        assert len(result.diagnostics) == 0


class TestConsistencyValidationPass:
    def test_conflicting_entity_descriptions(self) -> None:
        from knowledge.passes.consistency_pass import ConsistencyValidationPass

        graph = (
            KnowledgeGraph()
            .add_entity(Entity(name="Python", description="A language", id="e1"))
            .add_entity(Entity(name="Python", description="A snake", id="e2"))
        )
        result = ConsistencyValidationPass().execute(graph)
        warnings = [d for d in result.diagnostics if d.severity == Severity.WARNING]
        assert any("conflicting descriptions" in d.message.lower() for d in warnings)

    def test_contradictory_facts(self) -> None:
        from knowledge.passes.consistency_pass import ConsistencyValidationPass

        graph = (
            KnowledgeGraph()
            .add_fact(Fact(statement="Python is dynamically typed.", id="f1"))
            .add_fact(Fact(statement="Python is not dynamically typed.", id="f2"))
        )
        result = ConsistencyValidationPass().execute(graph)
        warnings = [d for d in result.diagnostics if d.severity == Severity.WARNING]
        assert any("contradictory" in d.message.lower() for d in warnings)

    def test_conflicting_relationship_types(self) -> None:
        from knowledge.passes.consistency_pass import ConsistencyValidationPass

        r1 = Relationship(source_id="a", target_id="b", relationship_type="uses", id="r1")
        r2 = Relationship(source_id="a", target_id="b", relationship_type="depends_on", id="r2")
        graph = (
            KnowledgeGraph()
            .add_entity(Entity(name="A", id="a"))
            .add_entity(Entity(name="B", id="b"))
            .add_relationship(r1)
            .add_relationship(r2)
        )
        result = ConsistencyValidationPass().execute(graph)
        suggestions = [d for d in result.diagnostics if d.severity == Severity.SUGGESTION]
        assert any("multiple relationship types" in d.message.lower() for d in suggestions)

    def test_consistent_graph_passes(self) -> None:
        from knowledge.passes.consistency_pass import ConsistencyValidationPass

        graph = (
            KnowledgeGraph()
            .add_entity(Entity(name="Python", id="e1"))
            .add_fact(Fact(statement="Python is dynamically typed.", id="f1"))
        )
        result = ConsistencyValidationPass().execute(graph)
        assert len(result.diagnostics) == 0


class TestScoringPass:
    def test_scoring_pass_with_relationships(self) -> None:
        rel = Relationship(source_id="a", target_id="b", relationship_type="uses", id="r1")
        graph = (
            KnowledgeGraph()
            .add_entity(Entity(name="A", id="a"))
            .add_entity(Entity(name="B", id="b"))
            .add_relationship(rel)
        )
        result = ScoringPass().execute(graph)
        assert result.score is not None
        assert result.score.overall > 0

    def test_ontology_score_penalizes_invalid_types(self) -> None:
        r1 = Relationship(source_id="a", target_id="b", relationship_type="uses", id="r1")
        r2 = Relationship(source_id="a", target_id="b", relationship_type="magical_power", id="r2")
        graph = (
            KnowledgeGraph()
            .add_entity(Entity(name="A", id="a"))
            .add_entity(Entity(name="B", id="b"))
            .add_relationship(r1)
            .add_relationship(r2)
        )
        score = ScoringPass().compute_score(graph)
        assert score.ontology_quality == 50.0

    def test_consistency_score_penalizes_duplicate_pairs(self) -> None:
        r1 = Relationship(source_id="a", target_id="b", relationship_type="uses", id="r1")
        r2 = Relationship(source_id="a", target_id="b", relationship_type="uses", id="r2")
        graph = (
            KnowledgeGraph()
            .add_entity(Entity(name="A", id="a"))
            .add_entity(Entity(name="B", id="b"))
            .add_relationship(r1)
            .add_relationship(r2)
        )
        score = ScoringPass().compute_score(graph)
        assert score.consistency < 100.0


class TestNormalizeConfidencePass:
    def test_normalize_pass_with_valid_confidences(self) -> None:
        from knowledge.passes.repair_passes import NormalizeConfidencePass

        graph = (
            KnowledgeGraph()
            .add_entity(Entity(name="Python", confidence=0.5, id="e1"))
            .add_fact(Fact(statement="Fact.", confidence=0.8, id="f1"))
        )
        result = NormalizeConfidencePass().execute(graph)
        assert result.repairs_applied == 0
        assert len(result.diagnostics) == 1
        assert "0 elements" in result.diagnostics[0].message

    def test_normalize_clamps_out_of_range_confidence(self) -> None:
        from knowledge.passes.repair_passes import NormalizeConfidencePass

        entity = Entity.model_construct(id="e1", name="Low", confidence=-0.5)
        concept = Concept.model_construct(id="c1", name="High", confidence=1.5)
        fact = Fact.model_construct(id="f1", statement="Test.", confidence=-0.1)
        rel = Relationship.model_construct(
            id="r1", source_id="e1", target_id="c1", relationship_type="related", confidence=2.0
        )
        graph = KnowledgeGraph().model_copy(
            update={
                "entities": {"e1": entity},
                "concepts": {"c1": concept},
                "facts": {"f1": fact},
                "relationships": {"r1": rel},
            }
        )
        result = NormalizeConfidencePass().execute(graph)
        assert result.graph.entities["e1"].confidence == 0.0
        assert result.graph.concepts["c1"].confidence == 1.0
        assert result.graph.facts["f1"].confidence == 0.0
        assert result.graph.relationships["r1"].confidence == 1.0
        assert "Normalized confidence for 4 elements" in result.diagnostics[0].message
