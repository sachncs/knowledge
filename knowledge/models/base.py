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

    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    tags: list[str] = Field(default_factory=list)
    version: int = 1


class Provenance(BaseModel, frozen=True):
    """Provenance records the origin and history of a knowledge element.

    Provenance answers:
    - Where did this come from?
    - When was it added?
    - Which source produced it?
    - Which verification cycle accepted it?
    """

    source_id: str
    extracted_at: datetime = Field(default_factory=datetime.now)
    extractor: str = "unknown"
    verification_cycle: str | None = None


class KnowledgeModel(BaseModel, frozen=True):
    """Base model for all knowledge elements.

    Provides common fields shared by every element in the canonical
    Knowledge Model: a stable identifier, confidence score, verification
    state, provenance, and metadata.

    All domain-level models (Entity, Concept, Fact, Relationship)
    inherit from this class.
    """

    id: str = Field(default_factory=lambda: uuid4().hex)
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    verification_state: VerificationState = VerificationState.PENDING
    provenance: Provenance | None = None
    metadata: Metadata = Field(default_factory=Metadata)
