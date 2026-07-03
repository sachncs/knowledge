"""Tests for verification — semantic validation, ontology, and reasoning."""

from __future__ import annotations

from knowledge.models import (
    Entity,
    Evidence,
    Fact,
    KnowledgeGraph,
    Provenance,
    Relationship,
)
from knowledge.passes import (
    EvidenceValidationPass,
    OntologyValidationPass,
    PassManager,
    Phase,
    SemanticValidationPass,
)
from knowledge.passes.diagnostics import Severity
from knowledge.verification.reasoning import (
    DeterministicReasoningProvider,
)


class TestDeterministicReasoningProvider:
    def test_consistent_statements(self) -> None:
        provider = DeterministicReasoningProvider()
        result = provider.validate_consistency(
            [
                "Python supports async programming.",
                "Python is dynamically typed.",
            ]
        )
        assert result.is_valid is True

    def test_contradictory_statements(self) -> None:
        provider = DeterministicReasoningProvider()
        result = provider.validate_consistency(
            [
                "Python is dynamically typed.",
                "Python is not dynamically typed.",
            ]
        )
        assert result.is_valid is False

    def test_claim_supported_by_evidence(self) -> None:
        provider = DeterministicReasoningProvider()
        result = provider.validate_claim(
            "Python supports async programming.",
            ["Python has async and await keywords for concurrent programming."],
        )
        assert result.is_valid is True

    def test_claim_unsupported_by_evidence(self) -> None:
        provider = DeterministicReasoningProvider()
        result = provider.validate_claim(
            "Python supports quantum computing.",
            ["Python is a general-purpose programming language."],
        )
        assert result.is_valid is False

    def test_claim_no_evidence(self) -> None:
        provider = DeterministicReasoningProvider()
        result = provider.validate_claim("Python is fast.", [])
        assert result.is_valid is False
        assert "No evidence" in result.explanation

    def test_contradiction_via_significant_word_overlap(self) -> None:
        from knowledge.util import statements_are_contradictory

        result = statements_are_contradictory(
            "Python is dramatically slow",
            "Python is not dramatically fast",
        )
        assert result is True

    def test_no_contradiction_without_shared_words(self) -> None:
        from knowledge.util import statements_are_contradictory

        result = statements_are_contradictory(
            "Python is fast",
            "Python is not blue",
        )
        assert result is False

    def test_reasoning_detects_word_overlap_contradiction(self) -> None:
        provider = DeterministicReasoningProvider()
        result = provider.validate_consistency(
            [
                "Python is dramatically slow",
                "Python is not dramatically fast",
            ]
        )
        assert result.is_valid is False


class TestSemanticValidationPass:
    def test_fact_without_evidence(self) -> None:
        graph = KnowledgeGraph()
        graph = graph.add_fact(Fact(statement="Python is great.", id="f_001"))
        passer = PassManager()
        passer.register(SemanticValidationPass())
        result = passer.execute(graph, phases=[Phase.VERIFICATION])
        warnings = [d for d in result.diagnostics if d.severity == Severity.WARNING]
        assert any("no supporting evidence" in d.message for d in warnings)

    def test_broken_evidence_refs(self) -> None:
        graph = KnowledgeGraph()
        graph = graph.add_fact(
            Fact(statement="Python is great.", evidence_refs=["ev_missing"], id="f_001")
        )
        passer = PassManager()
        passer.register(SemanticValidationPass())
        result = passer.execute(graph, phases=[Phase.VERIFICATION])
        errors = [d for d in result.diagnostics if d.severity == Severity.ERROR]
        assert any("missing evidence" in d.message.lower() for d in errors)

    def test_valid_fact_with_evidence(self) -> None:
        graph = KnowledgeGraph()
        graph = graph.add_evidence(
            Evidence(content="Python is a programming language.", source="doc.md", id="ev_001")
        )
        graph = graph.add_fact(
            Fact(
                statement="Python is a programming language.",
                evidence_refs=["ev_001"],
                id="f_001",
            )
        )
        passer = PassManager()
        passer.register(SemanticValidationPass())
        result = passer.execute(graph, phases=[Phase.VERIFICATION])
        # Should be no errors or warnings for evidence
        errors_or_warnings = [
            d for d in result.diagnostics if d.severity in (Severity.ERROR, Severity.WARNING)
        ]
        # Note: there may still be suggestions about descriptions, etc.
        ev_issues = [
            d
            for d in errors_or_warnings
            if "evidence" in d.message.lower() or "fact" in d.message.lower()
        ]
        assert len(ev_issues) == 0

    def test_entity_without_description(self) -> None:
        graph = KnowledgeGraph()
        graph = graph.add_entity(Entity(name="Python", id="ent_001"))
        passer = PassManager()
        passer.register(SemanticValidationPass())
        result = passer.execute(graph, phases=[Phase.VERIFICATION])
        suggestions = [d for d in result.diagnostics if d.severity == Severity.SUGGESTION]
        assert any("no description" in d.message for d in suggestions)

    def test_broken_relationship_refs(self) -> None:
        graph = KnowledgeGraph()
        graph = graph.add_relationship(
            Relationship(
                source_id="ent_missing",
                target_id="ent_also_missing",
                relationship_type="uses",
                id="rel_001",
            )
        )
        passer = PassManager()
        passer.register(SemanticValidationPass())
        result = passer.execute(graph, phases=[Phase.VERIFICATION])
        # Relationship ref checks are now in StructuralValidationPass
        assert len(result.diagnostics) == 0

    def test_empty_graph(self) -> None:
        passer = PassManager()
        passer.register(SemanticValidationPass())
        result = passer.execute(KnowledgeGraph(), phases=[Phase.VERIFICATION])
        assert len(result.diagnostics) == 0


class TestOntologyValidationPass:
    def setup_passer(self) -> PassManager:
        passer = PassManager()
        passer.register(SemanticValidationPass())
        passer.register(EvidenceValidationPass())
        passer.register(OntologyValidationPass())
        return passer

    def test_unknown_relationship_type(self) -> None:
        graph = KnowledgeGraph()
        graph = graph.add_relationship(
            Relationship(
                source_id="ent_001",
                target_id="ent_002",
                relationship_type="magical_power",
                id="rel_001",
            )
        )
        passer = self.setup_passer()
        result = passer.execute(graph, phases=[Phase.VERIFICATION])
        warnings = [d for d in result.diagnostics if d.severity == Severity.WARNING]
        assert any("unknown relationship" in d.message.lower() for d in warnings)

    def test_duplicate_relationships(self) -> None:
        graph = KnowledgeGraph()
        graph = graph.add_relationship(
            Relationship(
                source_id="ent_001",
                target_id="ent_002",
                relationship_type="uses",
                id="rel_001",
            )
        )
        graph = graph.add_relationship(
            Relationship(
                source_id="ent_001",
                target_id="ent_002",
                relationship_type="uses",
                id="rel_002",
            )
        )
        passer = self.setup_passer()
        result = passer.execute(graph, phases=[Phase.VERIFICATION])
        warnings = [d for d in result.diagnostics if d.severity == Severity.WARNING]
        assert any("duplicate relationship" in d.message.lower() for d in warnings)

    def test_valid_relationship_type(self) -> None:
        graph = KnowledgeGraph()
        graph = graph.add_relationship(
            Relationship(
                source_id="ent_001",
                target_id="ent_002",
                relationship_type="uses",
                id="rel_001",
            )
        )
        passer = self.setup_passer()
        result = passer.execute(graph, phases=[Phase.VERIFICATION])
        type_warnings = [
            d
            for d in result.diagnostics
            if d.severity == Severity.WARNING and "relationship type" in d.message
        ]
        # There might be warnings about duplicate, but not about unknown type
        unknown_type = [d for d in type_warnings if "unknown" in d.message.lower()]
        assert len(unknown_type) == 0


class TestEvidenceValidationPass:
    def test_entity_without_provenance(self) -> None:
        graph = KnowledgeGraph()
        graph = graph.add_entity(Entity(name="Python", id="ent_001"))
        passer = PassManager()
        passer.register(SemanticValidationPass())
        passer.register(EvidenceValidationPass())
        result = passer.execute(graph, phases=[Phase.VERIFICATION])
        warnings = [d for d in result.diagnostics if d.severity == Severity.WARNING]
        provenance_warnings = [d for d in warnings if "provenance" in d.message.lower()]
        assert len(provenance_warnings) >= 1

    def test_entity_with_provenance(self) -> None:
        graph = KnowledgeGraph()
        graph = graph.add_entity(
            Entity(
                name="Python",
                id="ent_001",
                provenance=Provenance(source_id="doc.md", extractor="test"),
            )
        )
        passer = PassManager()
        passer.register(SemanticValidationPass())
        passer.register(EvidenceValidationPass())
        result = passer.execute(graph, phases=[Phase.VERIFICATION])
        provenance_warnings = [d for d in result.diagnostics if "provenance" in d.message.lower()]
        assert len(provenance_warnings) == 0

    def test_fact_with_evidence(self) -> None:
        graph = KnowledgeGraph()
        graph = graph.add_evidence(
            Evidence(content="Python is a language.", source="doc.md", id="ev_001")
        )
        graph = graph.add_fact(
            Fact(statement="Python is a language.", evidence_refs=["ev_001"], id="f_001")
        )
        passer = PassManager()
        passer.register(SemanticValidationPass())
        passer.register(EvidenceValidationPass())
        result = passer.execute(graph, phases=[Phase.VERIFICATION])
        evidence_warnings = [
            d
            for d in result.diagnostics
            if "evidence" in d.message.lower() and "no evidence" in d.message.lower()
        ]
        assert len(evidence_warnings) == 0

    def test_fact_without_evidence(self) -> None:
        graph = KnowledgeGraph()
        graph = graph.add_fact(Fact(statement="Python is great.", id="f_001"))
        passer = PassManager()
        passer.register(SemanticValidationPass())
        passer.register(EvidenceValidationPass())
        result = passer.execute(graph, phases=[Phase.VERIFICATION])
        # Fact-without-evidence warnings are from SemanticValidationPass
        evidence_warnings = [
            d for d in result.diagnostics if "no supporting evidence" in d.message.lower()
        ]
        assert len(evidence_warnings) >= 1


class TestVerificationPipelineIntegration:
    def test_full_verification_pipeline(self) -> None:
        passer = PassManager()
        passer.register(SemanticValidationPass())
        passer.register(OntologyValidationPass())
        passer.register(EvidenceValidationPass())

        graph = KnowledgeGraph()
        graph = graph.add_entity(Entity(name="Python", id="ent_001"))
        graph = graph.add_entity(Entity(name="JavaScript", id="ent_002"))
        graph = graph.add_fact(
            Fact(
                statement="Python is a programming language.",
                id="f_001",
            )
        )
        graph = graph.add_relationship(
            Relationship(
                source_id="ent_001",
                target_id="ent_002",
                relationship_type="influences",
                id="rel_001",
            )
        )

        result = passer.execute(graph, phases=[Phase.VERIFICATION])
        assert len(result.diagnostics) >= 3  # fact, provenance, unknown type warnings
        assert len(result.executed) == 3
        assert result.executed == [
            "verification.semantic",
            "verification.evidence",
            "verification.ontology",
        ]
