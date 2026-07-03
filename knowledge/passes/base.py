"""Base abstractions for the compiler pass framework.

All compiler passes inherit from CompilerPass and specify their
phase, dependencies, and execution logic. The framework handles
registration, ordering, and orchestration.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from enum import Enum
from typing import Any, ClassVar

from pydantic import BaseModel, Field

from knowledge.models import KnowledgeGraph
from knowledge.passes.diagnostics import Diagnostic


class KnowledgeScore(BaseModel, frozen=True):
    """Quality scores for a KnowledgeGraph.

    Attributes:
        overall: Overall quality score (0.0 to 1.0).
        completeness: Score representing how complete the graph is.
        consistency: Score representing internal consistency.
        evidence_quality: Quality score for supporting evidence.
        ontology_quality: Quality score for ontology adherence.
        metadata_completeness: Score for metadata coverage.
    """

    overall: float = 0.0
    completeness: float = 0.0
    consistency: float = 0.0
    evidence_quality: float = 0.0
    ontology_quality: float = 0.0
    metadata_completeness: float = 0.0


class Phase(str, Enum):
    """The execution phase of a compiler pass.

    Phases define the stage of the compiler pipeline in which a
    pass executes. The pipeline follows this order:
    PARSER → EXTRACTION → NORMALIZATION → ANALYSIS →
    VERIFICATION → REPAIR → SCORING → SERIALIZATION
    """

    PARSER = "parser"
    EXTRACTION = "extraction"
    NORMALIZATION = "normalization"
    ANALYSIS = "analysis"
    VERIFICATION = "verification"
    REPAIR = "repair"
    SCORING = "scoring"
    SERIALIZATION = "serialization"


class PassResult(BaseModel, frozen=True):
    """The result of executing a single compiler pass.

    Contains the (possibly modified) KnowledgeGraph along with any
    diagnostics the pass produced. Passes that only validate return
    the graph unmodified with diagnostics attached.

    Attributes:
        graph: The (possibly modified) KnowledgeGraph.
        diagnostics: Diagnostics produced during execution.
        score: Optional quality score from scoring passes.
        repairs_applied: Number of repairs performed.
    """

    graph: KnowledgeGraph
    diagnostics: list[Diagnostic] = Field(default_factory=list)
    score: KnowledgeScore | None = None
    repairs_applied: int = 0


VALID_RELATIONSHIP_TYPES: frozenset[str] = frozenset(
    {
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
)


class CompilerPass(ABC):
    """Base class for all compiler passes.

    Subclasses must define:
    - ``id``:       A unique dot-separated identifier.
    - ``phase``:    The Phase in which this pass executes.
    - ``execute``:  The transformation or validation logic.

    Subclasses may define:
    - ``version``:    Semantic version of the pass.
    - ``description``: Human-readable description.
    - ``depends_on``: Tuple of pass IDs that must run first.
    """

    id: ClassVar[str]
    phase: ClassVar[Phase]
    version: ClassVar[str] = "0.1.0"
    description: ClassVar[str] = ""
    depends_on: ClassVar[tuple[str, ...]] = ()

    @abstractmethod
    def execute(
        self,
        graph: KnowledgeGraph,
        config: dict[str, Any] | None = None,
    ) -> PassResult:
        """Execute the pass against the given KnowledgeGraph.

        Args:
            graph: The current KnowledgeGraph to process.
            config: Optional pass-specific configuration.

        Returns:
            A PassResult containing the (possibly modified) graph
            and any diagnostics produced.
        """
        ...
