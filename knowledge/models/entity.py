"""Entity model — a uniquely identifiable thing in the knowledge domain."""

from pydantic import Field

from knowledge.models.base import KnowledgeModel


class Entity(KnowledgeModel):
    """A uniquely identifiable thing in the knowledge domain.

    Entities represent concrete objects such as people, organizations,
    software, APIs, documents, datasets, and standards.

    Each entity has a canonical name, optional aliases for alternative
    naming, and a description providing human-readable context.
    """

    name: str = Field(description="Canonical display name of the entity")
    aliases: list[str] = Field(
        default_factory=list,
        description="Alternative names that refer to the same entity",
    )
    description: str | None = Field(
        default=None,
        description="Human-readable description providing context",
    )
