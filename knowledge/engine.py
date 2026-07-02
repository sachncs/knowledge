"""Verification Engine — the core component that protects knowledge integrity.

Every mutation passes through the engine before completion. It iteratively
validates, diagnoses, repairs, scores, and revalidates until convergence.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from pydantic import BaseModel, Field

from knowledge.models import KnowledgeGraph
from knowledge.passes import (
    Diagnostic,
    PassManager,
    Phase,
    PipelineResult,
)
from knowledge.passes.scoring_pass import KnowledgeScore, ScoringPass


class VerificationResult(BaseModel, frozen=True):
    """The result of a verification cycle.

    Contains the final verified graph, quality scores, diagnostics,
    repairs applied, and metadata about the verification process.
    """

    graph: KnowledgeGraph
    score: KnowledgeScore = Field(default_factory=KnowledgeScore)
    diagnostics: list[Diagnostic] = Field(default_factory=list)
    repairs_applied: int = 0
    iteration_count: int = 1
    converged: bool = True
    threshold_met: bool = False


@dataclass
class VerificationEngine:
    """The verification engine that protects knowledge integrity.

    Owns the repair loop: validate → diagnose → repair → rescore → repeat.
    No component outside this engine may modify knowledge in response
    to validation failures.
    """

    pass_manager: PassManager = field(default_factory=PassManager)
    quality_threshold: float = 80.0
    max_iterations: int = 5
    repair_phases: list[Phase] = field(default_factory=lambda: [Phase.REPAIR])
    verification_phases: list[Phase] = field(
        default_factory=lambda: [
            Phase.VERIFICATION,
            Phase.SCORING,
        ]
    )

    def _setup_default_passes(self) -> None:
        from knowledge.passes.consistency_pass import ConsistencyValidationPass
        from knowledge.passes.repair_passes import (
            AttachProvenancePass,
            FixEvidenceRefsPass,
            MergeDuplicateEntitiesPass,
            NormalizeConfidencePass,
        )
        from knowledge.passes.schema_pass import SchemaValidationPass
        from knowledge.passes.structural_pass import StructuralValidationPass

        for pass_ in [
            SchemaValidationPass(),
            StructuralValidationPass(),
            ConsistencyValidationPass(),
            ScoringPass(),
            MergeDuplicateEntitiesPass(),
            AttachProvenancePass(),
            FixEvidenceRefsPass(),
            NormalizeConfidencePass(),
        ]:
            try:
                self.pass_manager.register(pass_)
            except ValueError:
                pass

    def verify(
        self,
        graph: KnowledgeGraph,
        config: dict[str, Any] | None = None,
        threshold: float | None = None,
        max_iterations: int | None = None,
    ) -> VerificationResult:
        if not self.pass_manager.registered_ids:
            self._setup_default_passes()

        threshold = threshold if threshold is not None else self.quality_threshold
        max_iterations = max_iterations if max_iterations is not None else self.max_iterations
        current_graph = graph
        all_diagnostics: list[Diagnostic] = []
        total_repairs = 0

        for iteration in range(1, max_iterations + 1):
            # Verify
            v_result = self.pass_manager.execute(
                current_graph, config=config, phases=self.verification_phases
            )
            all_diagnostics.extend(v_result.diagnostics)

            # Extract score
            score = self._extract_score(v_result)
            if score.overall >= threshold:
                return VerificationResult(
                    graph=v_result.graph,
                    score=score,
                    diagnostics=all_diagnostics,
                    repairs_applied=total_repairs,
                    iteration_count=iteration,
                    converged=True,
                    threshold_met=True,
                )

            # Repair
            r_result = self.pass_manager.execute(
                v_result.graph, config=config, phases=self.repair_phases
            )
            repairs_this = sum(
                1 for d in r_result.diagnostics
                if d.severity.name != "INFORMATION"
            )
            total_repairs += repairs_this if repairs_this > 0 else len(r_result.diagnostics)
            all_diagnostics.extend(r_result.diagnostics)

            # Check convergence — if no change, stop
            if r_result.graph == current_graph:
                final_score = self._compute_final_score(r_result.graph)
                return VerificationResult(
                    graph=r_result.graph,
                    score=final_score,
                    diagnostics=all_diagnostics,
                    repairs_applied=total_repairs,
                    iteration_count=iteration,
                    converged=True,
                    threshold_met=final_score.overall >= threshold,
                )

            current_graph = r_result.graph

        # Max iterations reached
        final_score = self._compute_final_score(current_graph)
        return VerificationResult(
            graph=current_graph,
            score=final_score,
            diagnostics=all_diagnostics,
            repairs_applied=total_repairs,
            iteration_count=max_iterations,
            converged=False,
            threshold_met=final_score.overall >= threshold,
        )

    def _extract_score(self, result: PipelineResult) -> KnowledgeScore:
        for d in result.diagnostics:
            if d.location == "scoring.quality" and d.severity.name == "INFORMATION":
                prefix = "Quality score: "
                msg = d.message[len(prefix):] if d.message.startswith(prefix) else d.message
                scores = {}
                for part in msg.split(", "):
                    if "=" in part:
                        key, val = part.split("=", 1)
                        scores[key.strip()] = float(val.replace("%", "").strip())
                return KnowledgeScore(
                    overall=scores.get("overall", 0.0),
                    completeness=scores.get("completeness", 0.0),
                    consistency=scores.get("consistency", 0.0),
                    evidence_quality=scores.get("evidence", 0.0),
                    ontology_quality=scores.get("ontology", 0.0),
                    metadata_completeness=scores.get("metadata", 0.0),
                )
        return KnowledgeScore()

    @staticmethod
    def _compute_final_score(graph: KnowledgeGraph) -> KnowledgeScore:

        result = ScoringPass().execute(graph)
        for d in result.diagnostics:
            if d.location == "scoring.quality":
                prefix = "Quality score: "
                msg = d.message[len(prefix):] if d.message.startswith(prefix) else d.message
                scores = {}
                for part in msg.split(", "):
                    if "=" in part:
                        key, val = part.split("=", 1)
                        scores[key.strip()] = float(val.replace("%", "").strip())
                return KnowledgeScore(
                    overall=scores.get("overall", 0.0),
                    completeness=scores.get("completeness", 0.0),
                    consistency=scores.get("consistency", 0.0),
                    evidence_quality=scores.get("evidence", 0.0),
                    ontology_quality=scores.get("ontology", 0.0),
                    metadata_completeness=scores.get("metadata", 0.0),
                )
        return KnowledgeScore()
