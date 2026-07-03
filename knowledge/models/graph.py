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
        return self.model_copy(update={"entities": {**self.entities, entity.id: entity}})

    def add_concept(self, concept: Concept) -> "KnowledgeGraph":
        return self.model_copy(update={"concepts": {**self.concepts, concept.id: concept}})

    def add_fact(self, fact: Fact) -> "KnowledgeGraph":
        return self.model_copy(update={"facts": {**self.facts, fact.id: fact}})

    def add_relationship(self, relationship: Relationship) -> "KnowledgeGraph":
        return self.model_copy(
            update={
                "relationships": {
                    **self.relationships,
                    relationship.id: relationship,
                }
            }
        )

    def add_evidence(self, evidence: Evidence) -> "KnowledgeGraph":
        return self.model_copy(update={"evidence": {**self.evidence, evidence.id: evidence}})

    def remove_entity(self, entity_id: str) -> "KnowledgeGraph":
        return self.model_copy(
            update={"entities": {k: v for k, v in self.entities.items() if k != entity_id}}
        )

    def remove_concept(self, concept_id: str) -> "KnowledgeGraph":
        return self.model_copy(
            update={"concepts": {k: v for k, v in self.concepts.items() if k != concept_id}}
        )

    def remove_fact(self, fact_id: str) -> "KnowledgeGraph":
        return self.model_copy(
            update={"facts": {k: v for k, v in self.facts.items() if k != fact_id}}
        )

    def remove_relationship(self, relationship_id: str) -> "KnowledgeGraph":
        return self.model_copy(
            update={
                "relationships": {
                    k: v for k, v in self.relationships.items() if k != relationship_id
                }
            }
        )

    def remove_evidence(self, evidence_id: str) -> "KnowledgeGraph":
        return self.model_copy(
            update={"evidence": {k: v for k, v in self.evidence.items() if k != evidence_id}}
        )

    def update_entity(self, entity: Entity) -> "KnowledgeGraph":
        return self.add_entity(entity)

    def update_concept(self, concept: Concept) -> "KnowledgeGraph":
        return self.add_concept(concept)

    def update_fact(self, fact: Fact) -> "KnowledgeGraph":
        return self.add_fact(fact)

    def update_relationship(self, relationship: Relationship) -> "KnowledgeGraph":
        return self.add_relationship(relationship)

    def update_evidence(self, evidence: Evidence) -> "KnowledgeGraph":
        return self.add_evidence(evidence)

    SINGULAR: dict[str, str] = {
        "entities": "entity",
        "concepts": "concept",
        "facts": "fact",
        "relationships": "relationship",
        "evidence": "evidence",
    }

    def merge(self, other: "KnowledgeGraph") -> "KnowledgeGraph":
        merged = self
        for plural, singular in self.SINGULAR.items():
            for element in getattr(other, plural).values():
                merged = getattr(merged, f"add_{singular}")(element)
        return merged

    def diff(self, other: "KnowledgeGraph") -> dict[str, list[str]]:
        result: dict[str, list[str]] = {}
        for collection in ("entities", "concepts", "facts", "relationships"):
            ours = getattr(self, collection)
            theirs = getattr(other, collection)
            plural = collection
            result[f"{plural}_added"] = [e.id for e in theirs.values() if e.id not in ours]
            result[f"{plural}_removed"] = [e.id for e in ours.values() if e.id not in theirs]
        return result
