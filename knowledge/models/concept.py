"""Concept model — an abstract idea that organizes knowledge."""

from pydantic import Field

from knowledge.models.base import KnowledgeModel


class Concept(KnowledgeModel):
    """An abstract idea that organizes knowledge.

    Concepts represent intangible notions such as "machine learning",
    "ontology", "version control", or "semantic validation". They
    group and categorize knowledge rather than representing concrete
    objects.
    """

    name: str = Field(description="Canonical name of the concept")
    description: str | None = Field(
        default=None,
        description="Human-readable definition of the concept",
    )
