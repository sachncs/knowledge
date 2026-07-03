"""Base model classes for the canonical Knowledge Model.

Defines Metadata, Provenance, and KnowledgeModel — the common base
for all domain-level knowledge elements.
"""

from datetime import datetime
from uuid import uuid4

from pydantic import BaseModel, Field

from knowledge.models.verification import VerificationState


class Metadata(BaseModel, frozen=True):
    """Operational metadata attached to knowledge elements.

    Metadata contains information about the element's lifecycle such as
    creation and modification timestamps, tags for classification, and
    a version number for tracking changes. Metadata never affects
    semantic meaning.
    """

    created_at: datetime = Field(
        default_factory=datetime.now,
        description="Timestamp when the element was first created",
    )
    updated_at: datetime = Field(
        default_factory=datetime.now,
        description="Timestamp when the element was last modified",
    )
    tags: list[str] = Field(
        default_factory=list,
        description="Classification tags for filtering and organization",
    )
    version: int = Field(
        default=1,
        description="Monotonically increasing version number for change tracking",
    )


class Provenance(BaseModel, frozen=True):
    """Provenance records the origin and history of a knowledge element.

    Provenance answers:
    - Where did this come from?
    - When was it added?
    - Which source produced it?
    - Which verification cycle accepted it?
    """

    source_id: str = Field(description="Identifier of the source document")
    extracted_at: datetime = Field(
        default_factory=datetime.now,
        description="When the element was extracted from its source",
    )
    extractor: str = Field(
        default="unknown",
        description="Name of the extractor or process that produced this element",
    )
    verification_cycle: str | None = Field(
        default=None,
        description="Identifier of the verification cycle that accepted this element",
    )


class KnowledgeModel(BaseModel, frozen=True):
    """Base model for all knowledge elements.

    Provides common fields shared by every element in the canonical
    Knowledge Model: a stable identifier, confidence score, verification
    state, provenance, and metadata.

    All domain-level models (Entity, Concept, Fact, Relationship)
    inherit from this class.
    """

    id: str = Field(
        default_factory=lambda: uuid4().hex,
        description="Stable identifier unique across all knowledge elements",
    )
    confidence: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Confidence score between 0.0 and 1.0",
    )
    verification_state: VerificationState = Field(
        default=VerificationState.PENDING,
        description="Current verification status of this element",
    )
    provenance: Provenance | None = Field(
        default=None,
        description="Origin and history record for this element",
    )
    metadata: Metadata = Field(
        default_factory=Metadata,
        description="Operational metadata (timestamps, tags, version)",
    )
