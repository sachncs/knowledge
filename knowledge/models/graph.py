"""KnowledgeGraph — the canonical in-memory representation of knowledge."""

from pydantic import BaseModel, Field

from knowledge.models.concept import Concept
from knowledge.models.entity import Entity
from knowledge.models.evidence import Evidence
from knowledge.models.fact import Fact
from knowledge.models.relationship import Relationship


class KnowledgeGraph(BaseModel, frozen=True):
    """The canonical in-memory representation of knowledge.

    The KnowledgeGraph is the central data structure of the SDK. Every
    operation — extraction, verification, repair, scoring, serialization —
    works against this model.

    It is composed of independent collections of Entities, Concepts,
    Facts, Relationships, and Evidence, each keyed by stable identifier.

    All mutation methods return new instances, preserving immutability.
    """

    entities: dict[str, Entity] = Field(default_factory=dict)
    concepts: dict[str, Concept] = Field(default_factory=dict)
    facts: dict[str, Fact] = Field(default_factory=dict)
    relationships: dict[str, Relationship] = Field(default_factory=dict)
    evidence: dict[str, Evidence] = Field(default_factory=dict)

    def add_entity(self, entity: Entity) -> "KnowledgeGraph":
        """Add an entity to the graph.

        Args:
            entity: The Entity instance to add.

        Returns:
            A new KnowledgeGraph with the entity included.
        """
        return self.model_copy(update={"entities": {**self.entities, entity.id: entity}})

    def add_concept(self, concept: Concept) -> "KnowledgeGraph":
        """Add a concept to the graph.

        Args:
            concept: The Concept instance to add.

        Returns:
            A new KnowledgeGraph with the concept included.
        """
        return self.model_copy(update={"concepts": {**self.concepts, concept.id: concept}})

    def add_fact(self, fact: Fact) -> "KnowledgeGraph":
        """Add a fact to the graph.

        Args:
            fact: The Fact instance to add.

        Returns:
            A new KnowledgeGraph with the fact included.
        """
        return self.model_copy(update={"facts": {**self.facts, fact.id: fact}})

    def add_relationship(self, relationship: Relationship) -> "KnowledgeGraph":
        """Add a relationship to the graph.

        Args:
            relationship: The Relationship instance to add.

        Returns:
            A new KnowledgeGraph with the relationship included.
        """
        return self.model_copy(
            update={
                "relationships": {
                    **self.relationships,
                    relationship.id: relationship,
                }
            }
        )

    def add_evidence(self, evidence: Evidence) -> "KnowledgeGraph":
        """Add evidence to the graph.

        Args:
            evidence: The Evidence instance to add.

        Returns:
            A new KnowledgeGraph with the evidence included.
        """
        return self.model_copy(update={"evidence": {**self.evidence, evidence.id: evidence}})

    def remove_entity(self, entity_id: str) -> "KnowledgeGraph":
        """Remove an entity by ID.

        Args:
            entity_id: The stable identifier of the entity to remove.

        Returns:
            A new KnowledgeGraph without the specified entity.
        """
        return self.model_copy(
            update={"entities": {k: v for k, v in self.entities.items() if k != entity_id}}
        )

    def remove_concept(self, concept_id: str) -> "KnowledgeGraph":
        """Remove a concept by ID.

        Args:
            concept_id: The stable identifier of the concept to remove.

        Returns:
            A new KnowledgeGraph without the specified concept.
        """
        return self.model_copy(
            update={"concepts": {k: v for k, v in self.concepts.items() if k != concept_id}}
        )

    def remove_fact(self, fact_id: str) -> "KnowledgeGraph":
        """Remove a fact by ID.

        Args:
            fact_id: The stable identifier of the fact to remove.

        Returns:
            A new KnowledgeGraph without the specified fact.
        """
        return self.model_copy(
            update={"facts": {k: v for k, v in self.facts.items() if k != fact_id}}
        )

    def remove_relationship(self, relationship_id: str) -> "KnowledgeGraph":
        """Remove a relationship by ID.

        Args:
            relationship_id: The stable identifier of the relationship to remove.

        Returns:
            A new KnowledgeGraph without the specified relationship.
        """
        return self.model_copy(
            update={
                "relationships": {
                    k: v for k, v in self.relationships.items() if k != relationship_id
                }
            }
        )

    def remove_evidence(self, evidence_id: str) -> "KnowledgeGraph":
        """Remove evidence by ID.

        Args:
            evidence_id: The stable identifier of the evidence to remove.

        Returns:
            A new KnowledgeGraph without the specified evidence.
        """
        return self.model_copy(
            update={"evidence": {k: v for k, v in self.evidence.items() if k != evidence_id}}
        )

    def update_entity(self, entity: Entity) -> "KnowledgeGraph":
        """Replace an existing entity (add with same ID overwrites).

        Args:
            entity: The Entity instance with updated fields.

        Returns:
            A new KnowledgeGraph with the entity replaced.
        """
        return self.add_entity(entity)

    def update_concept(self, concept: Concept) -> "KnowledgeGraph":
        """Replace an existing concept (add with same ID overwrites).

        Args:
            concept: The Concept instance with updated fields.

        Returns:
            A new KnowledgeGraph with the concept replaced.
        """
        return self.add_concept(concept)

    def update_fact(self, fact: Fact) -> "KnowledgeGraph":
        """Replace an existing fact (add with same ID overwrites).

        Args:
            fact: The Fact instance with updated fields.

        Returns:
            A new KnowledgeGraph with the fact replaced.
        """
        return self.add_fact(fact)

    def update_relationship(self, relationship: Relationship) -> "KnowledgeGraph":
        """Replace an existing relationship (add with same ID overwrites).

        Args:
            relationship: The Relationship instance with updated fields.

        Returns:
            A new KnowledgeGraph with the relationship replaced.
        """
        return self.add_relationship(relationship)

    def update_evidence(self, evidence: Evidence) -> "KnowledgeGraph":
        """Replace existing evidence (add with same ID overwrites).

        Args:
            evidence: The Evidence instance with updated fields.

        Returns:
            A new KnowledgeGraph with the evidence replaced.
        """
        return self.add_evidence(evidence)

    SINGULAR: dict[str, str] = {
        "entities": "entity",
        "concepts": "concept",
        "facts": "fact",
        "relationships": "relationship",
        "evidence": "evidence",
    }

    def merge(self, other: "KnowledgeGraph") -> "KnowledgeGraph":
        """Merge all elements from another graph into this one.

        Uses the SINGULAR dispatch table to generically add each
        element from ``other`` regardless of collection type.

        Args:
            other: The KnowledgeGraph whose elements to merge in.

        Returns:
            A new KnowledgeGraph containing elements from both graphs.
        """
        merged = self
        for plural, singular in self.SINGULAR.items():
            for element in getattr(other, plural).values():
                merged = getattr(merged, f"add_{singular}")(element)
        return merged

    def diff(self, other: "KnowledgeGraph") -> dict[str, list[str]]:
        """Compute element-level differences with another graph.

        Compares entity, concept, fact, and relationship collections
        by stable ID. Evidence is excluded because it is append-only.

        Args:
            other: The KnowledgeGraph to compare against.

        Returns:
            A dict mapping e.g. ``entities_added``, ``entities_removed``,
            ``concepts_added``, etc. to lists of element IDs.
        """
        result: dict[str, list[str]] = {}
        for collection in ("entities", "concepts", "facts", "relationships"):
            ours = getattr(self, collection)
            theirs = getattr(other, collection)
            plural = collection
            result[f"{plural}_added"] = [e.id for e in theirs.values() if e.id not in ours]
            result[f"{plural}_removed"] = [e.id for e in ours.values() if e.id not in theirs]
        return result
