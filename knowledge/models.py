"""Pydantic domain models for knowledge extraction — Concept and KnowledgeGraph.

This module defines the two core value objects that flow through the
entire pipeline:

* :class:`Concept` — a single section or topic extracted from a source
  document by the LLM.
* :class:`KnowledgeGraph` — an immutable container that holds a
  collection of ``Concept`` instances, keyed by their unique ID.

Both models are **frozen** (immutable) Pydantic objects.  Every
mutating operation (``add_concept``, ``remove_concept``) returns a
*new* instance, leaving the original unchanged.  This makes the models
safe to share across threads and easy to reason about in pipelines.

Design rationale
----------------
Using Pydantic ``BaseModel`` gives us free serialization, schema
validation, and type coercion.  The ``frozen=True`` flag on
``KnowledgeGraph`` enforces the immutability contract at runtime.
"""

from __future__ import annotations

import re

from pydantic import BaseModel, Field, field_validator

__all__ = [
    "Concept",
    "KnowledgeGraph",
]


class Concept(BaseModel):
    """A single extracted concept or section from a source document.

    Each ``Concept`` corresponds to one heading-level section from the
    source.  The LLM converts the raw section content (HTML or Markdown)
    into clean Markdown and assigns a stable kebab-case ``id``.

    The ``id`` field is validated to match the pattern ``^[a-z][a-z0-9-]*$``.
    This restriction serves two purposes:

    1. **Filesystem safety** — ensures the ``id`` can be used as a filename
       without risk of path traversal (no ``..``, no ``/``).
    2. **URL friendliness** — kebab-case IDs are natural in URLs and
       consistent with common documentation conventions.

    .. rubric:: Example

    .. code-block:: python

        concept = Concept(
            id="installing-the-sdk",
            name="Installing the SDK",
            description="Run ``pip install knowledge`` ...",
            tags=["setup", "guide"],
        )
    """

    id: str = Field(description="Stable identifier (kebab-case slug)")
    name: str = Field(description="Canonical name / heading text")
    description: str | None = Field(
        default=None, description="Section plain-text content in Markdown"
    )
    tags: list[str] = Field(default_factory=list, description="Category tags for grouping")

    @field_validator("id")
    @classmethod
    def validate_id_is_slug(cls, v: str) -> str:  # noqa: N804 — Pydantic invokes via metaclass
        """Validate that ``id`` is a safe, kebab-case slug.

        The allowed character set ``[a-z0-9-]`` prevents path-traversal
        characters (``..``, ``/``) and special characters that are invalid
        in filenames or URLs.  Leading lowercase letter ensures the slug
        never starts with a digit or hyphen.

        Args:
            v: The candidate ``id`` value.

        Returns:
            The unchanged value if valid.

        Raises:
            ValueError: If the value does not match ``^[a-z][a-z0-9-]*$``.
        """
        if not re.match(r"^[a-z][a-z0-9-]*$", v):
            raise ValueError(f"Concept id must be a kebab-case slug, got: {v!r}")
        return v


class KnowledgeGraph(BaseModel, frozen=True):
    """An immutable collection of :class:`Concept` objects.

    ``KnowledgeGraph`` is the top-level container returned by the
    :class:`~knowledge.llm.extractor.LLMExtractor` and accepted by the
    :class:`~knowledge.kmd.bundle.BundleSerializer`.

    **Immutability contract**

    Because the model is ``frozen=True``, every mutation returns a **new**
    instance:

    .. code-block:: python

        g1 = KnowledgeGraph()
        g2 = g1.add_concept(Concept(id="a", name="A"))
        # g1 is unchanged, g2 contains "a"

    This makes the graph safe to share without defensive copies and
    eliminates a class of concurrency bugs.

    .. rubric:: Complexity

    * ``add_concept`` — O(n) in the number of concepts (dict unpack into
      a new dict).  Acceptable for the expected graph size (< 1 000
      entries).  If graphs grow significantly, consider batch construction
      at init time.
    * ``remove_concept`` — O(n) (dict comprehension filtering).
    """

    concepts: dict[str, Concept] = Field(default_factory=dict)

    def add_concept(self, concept: Concept) -> KnowledgeGraph:
        """Return a new graph with *concept* added (or replaced).

        If a concept with the same ``id`` already exists, it is silently
        overwritten (dict key replacement).  The original ``KnowledgeGraph``
        is not modified.

        Args:
            concept: The :class:`Concept` instance to add.

        Returns:
            A new ``KnowledgeGraph`` containing all existing concepts plus
            *concept*.
        """
        return self.model_copy(update={"concepts": {**self.concepts, concept.id: concept}})

    def remove_concept(self, concept_id: str) -> KnowledgeGraph:
        """Return a new graph with the concept identified by *concept_id* removed.

        If the ID does not exist in the graph the operation is a no-op
        (idempotent).  The original ``KnowledgeGraph`` is not modified.

        Args:
            concept_id: The ID of the concept to remove.

        Returns:
            A new ``KnowledgeGraph`` without the specified concept.
        """
        return self.model_copy(
            update={"concepts": {k: v for k, v in self.concepts.items() if k != concept_id}}
        )
