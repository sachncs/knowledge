"""Compiler pass framework for the knowledge SDK."""

from knowledge.passes.analysis_pass import GraphStatisticsPass
from knowledge.passes.base import CompilerPass, KnowledgeScore, PassResult, Phase
from knowledge.passes.consistency_pass import ConsistencyValidationPass
from knowledge.passes.diagnostics import Diagnostic, Severity
from knowledge.passes.extraction_pass import ExtractionPass
from knowledge.passes.manager import PassManager, PipelineResult
from knowledge.passes.normalization_passes import AliasResolutionPass, DuplicateDetectionPass
from knowledge.passes.repair_passes import (
    AttachProvenancePass,
    FixEvidenceRefsPass,
    MergeDuplicateEntitiesPass,
    NormalizeConfidencePass,
)
from knowledge.passes.schema_pass import SchemaValidationPass
from knowledge.passes.scoring_pass import ScoringPass
from knowledge.passes.structural_pass import StructuralValidationPass
from knowledge.passes.verification_passes import (
    EvidenceValidationPass,
    OntologyValidationPass,
    SemanticValidationPass,
)

__all__ = [
    "Phase",
    "CompilerPass",
    "PassResult",
    "Severity",
    "Diagnostic",
    "PassManager",
    "PipelineResult",
    "ExtractionPass",
    "AliasResolutionPass",
    "DuplicateDetectionPass",
    "SemanticValidationPass",
    "OntologyValidationPass",
    "EvidenceValidationPass",
    "SchemaValidationPass",
    "StructuralValidationPass",
    "ConsistencyValidationPass",
    "ScoringPass",
    "GraphStatisticsPass",
    "KnowledgeScore",
    "MergeDuplicateEntitiesPass",
    "AttachProvenancePass",
    "FixEvidenceRefsPass",
    "NormalizeConfidencePass",
]
