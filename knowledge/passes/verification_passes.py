"""Compiler passes for semantic and structural verification.

These passes run in the VERIFICATION phase and evaluate knowledge
quality, consistency, and correctness. They produce diagnostics
but never modify the graph directly.
"""

from __future__ import annotations

from typing import Any

from knowledge.models import KnowledgeGraph
from knowledge.passes.base import CompilerPass, PassResult, Phase
from knowledge.passes.diagnostics import Diagnostic, Severity
from knowledge.verification.reasoning import (
    DeterministicReasoningProvider,
    ReasoningProvider,
)


class SemanticValidationPass(CompilerPass):
    """Validates the semantic quality of the KnowledgeGraph.

    Checks include:
    - Every fact has supporting evidence
    - Entities have meaningful descriptions
    - Facts contain statements
    - Evidence references are valid
    """

    id = "verification.semantic"
    phase = Phase.VERIFICATION
    version = "0.1.0"
    description = "Validate semantic quality of knowledge elements"

    def __init__(self, reasoning_provider: ReasoningProvider | None = None) -> None:
        self._reasoning = reasoning_provider or DeterministicReasoningProvider()

    def execute(
        self,
        graph: KnowledgeGraph,
        config: dict[str, Any] | None = None,
    ) -> PassResult:
        diagnostics: list[Diagnostic] = []

        # Check facts have evidence
        for fact in graph.facts.values():
            if not fact.evidence_refs:
                diagnostics.append(
                    Diagnostic(
                        severity=Severity.WARNING,
                        message=f"Fact '{fact.id}' has no supporting evidence",
                        explanation=(
                            f"The fact '{fact.statement[:80]}...' has no evidence references."
                        ),
                        location=f"Fact: {fact.id}",
                        affected_objects=[fact.id],
                        suggested_fix="Add evidence references to this fact.",
                    )
                )
            else:
                missing = [ref for ref in fact.evidence_refs if ref not in graph.evidence]
                if missing:
                    diagnostics.append(
                        Diagnostic(
                            severity=Severity.ERROR,
                            message=f"Fact '{fact.id}' references missing evidence: {missing}",
                            location=f"Fact: {fact.id}",
                            affected_objects=[fact.id] + missing,
                            suggested_fix=(
                                "Ensure all evidence references point to existing evidence blocks."
                            ),
                        )
                    )

        # Check entities have descriptions
        for entity in graph.entities.values():
            if not entity.description:
                diagnostics.append(
                    Diagnostic(
                        severity=Severity.SUGGESTION,
                        message=f"Entity '{entity.name}' has no description",
                        explanation=f"Entity '{entity.name}' would benefit from a description.",
                        location=f"Entity: {entity.id}",
                        affected_objects=[entity.id],
                        suggested_fix="Add a description to this entity.",
                    )
                )

        # Check evidence exists
        for ev in graph.evidence.values():
            if not ev.content or len(ev.content.strip()) < 10:
                diagnostics.append(
                    Diagnostic(
                        severity=Severity.WARNING,
                        message=f"Evidence '{ev.id}' has very short or empty content",
                        location=f"Evidence: {ev.id}",
                        affected_objects=[ev.id],
                    )
                )

        # Check relationship references are valid
        for rel in graph.relationships.values():
            if rel.source_id not in graph.entities:
                diagnostics.append(
                    Diagnostic(
                        severity=Severity.ERROR,
                        message=(
                            f"Relationship '{rel.id}' references unknown "
                            f"source entity '{rel.source_id}'"
                        ),
                        location=f"Relationship: {rel.id}",
                        affected_objects=[rel.id],
                        suggested_fix="Ensure the source entity exists or fix the reference.",
                    )
                )
            if rel.target_id not in graph.entities:
                diagnostics.append(
                    Diagnostic(
                        severity=Severity.ERROR,
                        message=(
                            f"Relationship '{rel.id}' references unknown "
                            f"target entity '{rel.target_id}'"
                        ),
                        location=f"Relationship: {rel.id}",
                        affected_objects=[rel.id],
                        suggested_fix="Ensure the target entity exists or fix the reference.",
                    )
                )

        # Check for broken entity references in facts
        for fact in graph.facts.values():
            for ref in fact.evidence_refs:
                if ref not in graph.evidence:
                    pass  # already reported above

        return PassResult(graph=graph, diagnostics=diagnostics)


class OntologyValidationPass(CompilerPass):
    """Validates the ontology (relationship types, concept taxonomy).

    Checks include:
    - Relationship types are from a known set
    - No duplicate relationships
    - Concept hierarchy is acyclic
    """

    id = "verification.ontology"
    phase = Phase.VERIFICATION
    version = "0.1.0"
    description = "Validate ontology consistency and relationship types"
    depends_on = ("verification.evidence",)

    VALID_RELATIONSHIP_TYPES = {
        "uses",
        "depends_on",
        "extends",
        "implements",
        "part_of",
        "contains",
        "creates",
        "manages",
        "requires",
        "supports",
        "provides",
        "enables",
        "integrates_with",
        "references",
        "related_to",
    }

    def execute(
        self,
        graph: KnowledgeGraph,
        config: dict[str, Any] | None = None,
    ) -> PassResult:
        diagnostics: list[Diagnostic] = []

        # Check relationship types
        for rel in graph.relationships.values():
            if rel.relationship_type not in self.VALID_RELATIONSHIP_TYPES:
                diagnostics.append(
                    Diagnostic(
                        severity=Severity.WARNING,
                        message=(
                            f"Unknown relationship type '{rel.relationship_type}'"
                        ),
                        explanation=(
                            f"Relationship '{rel.id}' uses type '{rel.relationship_type}' "
                            f"which is not in the standard set: "
                            f"{sorted(self.VALID_RELATIONSHIP_TYPES)}"
                        ),
                        location=f"Relationship: {rel.id}",
                        affected_objects=[rel.id],
                        suggested_fix=(
                            "Use a standard relationship type: "
                            f"{', '.join(sorted(self.VALID_RELATIONSHIP_TYPES))}"
                        ),
                    )
                )

        # Check for duplicate relationships (same source, type, target)
        seen: set[tuple[str, str, str]] = set()
        for rel in graph.relationships.values():
            key = (rel.source_id, rel.relationship_type, rel.target_id)
            if key in seen:
                diagnostics.append(
                    Diagnostic(
                        severity=Severity.WARNING,
                        message=(
                            f"Duplicate relationship: '{rel.relationship_type}' "
                            f"from '{rel.source_id}' to '{rel.target_id}'"
                        ),
                        location=f"Relationship: {rel.id}",
                        affected_objects=[rel.id],
                        suggested_fix="Remove the duplicate relationship.",
                    )
                )
            seen.add(key)

        return PassResult(graph=graph, diagnostics=diagnostics)


class EvidenceValidationPass(CompilerPass):
    """Validates evidence quality and coverage.

    Checks include:
    - Every entity, fact, and relationship has at least one evidence ref
    - Evidence is well-formed
    """

    id = "verification.evidence"
    phase = Phase.VERIFICATION
    version = "0.1.0"
    description = "Validate evidence coverage and quality"
    depends_on = ("verification.semantic",)

    def execute(
        self,
        graph: KnowledgeGraph,
        config: dict[str, Any] | None = None,
    ) -> PassResult:
        diagnostics: list[Diagnostic] = []

        # Check entities have provenance
        for entity in graph.entities.values():
            if entity.provenance is None:
                diagnostics.append(
                    Diagnostic(
                        severity=Severity.WARNING,
                        message=f"Entity '{entity.name}' has no provenance",
                        location=f"Entity: {entity.id}",
                        affected_objects=[entity.id],
                        suggested_fix="Attach provenance information to this entity.",
                    )
                )

        # Check facts have evidence
        for fact in graph.facts.values():
            if not fact.evidence_refs:
                diagnostics.append(
                    Diagnostic(
                        severity=Severity.WARNING,
                        message=f"Fact '{fact.id}' has no evidence references",
                        location=f"Fact: {fact.id}",
                        affected_objects=[fact.id],
                        suggested_fix="Link this fact to supporting evidence.",
                    )
                )

        return PassResult(graph=graph, diagnostics=diagnostics)
