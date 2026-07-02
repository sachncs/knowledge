"""Tests for the compiler pass framework."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from knowledge.models import Entity, KnowledgeGraph
from knowledge.passes import (
    CompilerPass,
    Diagnostic,
    PassManager,
    PassResult,
    Phase,
    Severity,
)


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
