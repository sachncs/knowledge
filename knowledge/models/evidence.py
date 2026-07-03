"""Evidence model — supporting material from which knowledge is derived."""

from knowledge.models.base import KnowledgeModel


class Evidence(KnowledgeModel):
    """Supporting material from which knowledge is derived.

    Evidence represents the raw source material — document sections,
    URLs, paragraphs, API specifications — that support the claims
    made by knowledge elements.

    Evidence is immutable once created. Knowledge references evidence,
    but evidence never references knowledge.
    """

    content: str
    source: str
