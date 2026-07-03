"""Evidence model — supporting material from which knowledge is derived."""

from pydantic import Field

from knowledge.models.base import KnowledgeModel


class Evidence(KnowledgeModel):
    """Supporting material from which knowledge is derived.

    Evidence represents the raw source material — document sections,
    URLs, paragraphs, API specifications — that support the claims
    made by knowledge elements.

    Evidence is immutable once created. Knowledge references evidence,
    but evidence never references knowledge.
    """

    content: str = Field(description="Raw source content (paragraph, URL, spec excerpt)")
    source: str = Field(description="Identifier of the source document or location")
