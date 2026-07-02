"""Compiler pass framework for the knowledge SDK."""

from knowledge.passes.base import CompilerPass, PassResult, Phase
from knowledge.passes.diagnostics import Diagnostic, Severity
from knowledge.passes.extraction_pass import ExtractionPass
from knowledge.passes.manager import PassManager
from knowledge.passes.normalization_passes import AliasResolutionPass, DuplicateDetectionPass
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
    "ExtractionPass",
    "AliasResolutionPass",
    "DuplicateDetectionPass",
    "SemanticValidationPass",
    "OntologyValidationPass",
    "EvidenceValidationPass",
]
