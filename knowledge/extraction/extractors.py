"""Deterministic extractors that produce knowledge elements from source text.

Each extractor focuses on one responsibility:
- EntityExtractor: discovers named entities
- ConceptExtractor: discovers abstract concepts
- FactExtractor: extracts factual statements
- RelationshipExtractor: identifies relationships between entities
- EvidenceExtractor: captures source evidence blocks

Extractors use deterministic algorithms (regex, heuristics) rather
than AI to maximize reproducibility.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import datetime

from knowledge.models import (
    Concept,
    Entity,
    Evidence,
    Fact,
    Provenance,
    Relationship,
    VerificationState,
)
from knowledge.models.base import Metadata
from knowledge.normalization.identifiers import CanonicalIdGenerator


@dataclass(frozen=True)
class ExtractionResult:
    """The output of a full extraction pipeline.

    Contains all discovered knowledge elements along with metadata
    about the extraction process.
    """

    entities: list[Entity] = field(default_factory=list)
    concepts: list[Concept] = field(default_factory=list)
    facts: list[Fact] = field(default_factory=list)
    relationships: list[Relationship] = field(default_factory=list)
    evidence: list[Evidence] = field(default_factory=list)


def make_provenance(source: str, extractor: str) -> Provenance:
    """Create a Provenance record for an extracted element.

    Args:
        source: The source identifier.
        extractor: The name of the extractor that discovered the element.

    Returns:
        A Provenance instance with a generated source ID.
    """
    return Provenance(
        source_id=CanonicalIdGenerator.source_id(source),
        extracted_at=datetime.now(),
        extractor=extractor,
    )


# Pattern for single capitalized words and multi-word capitalized phrases
ENTITY_PATTERN = re.compile(r"\b([A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+)*)\b")

# Common non-entity words to filter out
SKIP_WORDS: frozenset[str] = frozenset({
    "both", "this", "that", "these", "those", "here", "there", "when",
    "what", "which", "where", "who", "whom", "whose", "why", "how",
    "also", "very", "just", "then", "than", "some", "each", "every",
    "many", "much", "more", "most", "few", "less", "such", "only",
    "while", "after", "before", "during", "through", "between",
    "among", "above", "below", "under", "over", "into", "onto",
    "upon", "within", "without", "across", "beyond", "about",
    "around", "along", "beneath", "beside", "toward", "towards",
})
# Pattern for sentences (fact candidates)
SENTENCE_PATTERN = re.compile(r"[A-Z][^.!?]*[.!?]")
# Pattern for "X is a Y" or "X is Y" constructions
IS_A_PATTERN = re.compile(
    r"\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+is\s+(?:a|an|the)?\s*([A-Za-z][^,.;!?]+)"
)
# Pattern for "X Ys Z" (verb relationships)
ACTION_PATTERN = re.compile(
    r"\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+"
    r"(?:uses|depends on|extends|implements|contains|creates|"
    r"manages|requires|supports|provides|enables|integrates with)"
    r"\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)"
)


class EntityExtractor:
    """Discovers named entities from source text.

    Uses deterministic heuristics: capitalized multi-word phrases,
    repeated terms, and known naming patterns.
    """

    def extract(self, content: str, source: str = "unknown") -> list[Entity]:
        """Discover named entities from source text.

        Args:
            content: The source text to extract entities from.
            source: Identifier for the source document.

        Returns:
            A list of discovered Entity instances.
        """
        seen: set[str] = set()
        entities: list[Entity] = []

        matches = ENTITY_PATTERN.findall(content)
        for match in matches:
            name = match.strip()
            normalized = name.lower()
            if normalized in seen or normalized in SKIP_WORDS:
                continue
            seen.add(normalized)

            entity = Entity(
                id=CanonicalIdGenerator.entity_id(name),
                name=name,
                description=None,
                confidence=0.5,
                verification_state=VerificationState.PENDING,
                provenance=make_provenance(source, "entity_extractor"),
                metadata=Metadata(tags=["extracted"]),
            )
            entities.append(entity)

        return entities


class ConceptExtractor:
    """Discovers abstract concepts from source text.

    Concepts are identified as domain-specific terms that appear
    in descriptive or categorical contexts.
    """

    # Common concept-indicating patterns
    CONCEPT_PATTERN = re.compile(
        r"\b([A-Z][a-zA-Z]*(?:\s+[a-zA-Z]+){0,3})\s+"
        r"(?:is|are|refers to|describes|involves|encompasses)\s+"
    )

    def extract(self, content: str, source: str = "unknown") -> list[Concept]:
        """Discover abstract concepts from source text.

        Args:
            content: The source text to extract concepts from.
            source: Identifier for the source document.

        Returns:
            A list of discovered Concept instances.
        """
        seen: set[str] = set()
        concepts: list[Concept] = []

        matches = self.CONCEPT_PATTERN.findall(content)
        for match in matches:
            name = match.strip()
            if not name:
                continue
            normalized = name.lower()
            if normalized in seen:
                continue
            seen.add(normalized)

            concept = Concept(
                id=CanonicalIdGenerator.concept_id(name),
                name=name,
                description=None,
                confidence=0.4,
                verification_state=VerificationState.PENDING,
                provenance=make_provenance(source, "concept_extractor"),
                metadata=Metadata(tags=["extracted"]),
            )
            concepts.append(concept)

        return concepts


class FactExtractor:
    """Extracts factual statements from source text.

    Facts are identified as complete sentences that make verifiable
    claims. Each fact is linked to its source evidence.
    """

    def extract(self, content: str, ev_ids: list[str], source: str = "unknown") -> list[Fact]:
        """Extract factual statements from source text.

        Args:
            content: The source text to extract facts from.
            ev_ids: List of evidence IDs to reference in extracted facts.
            source: Identifier for the source document.

        Returns:
            A list of extracted Fact instances.
        """
        seen: set[str] = set()
        facts: list[Fact] = []
        sentence_matches = SENTENCE_PATTERN.findall(content)

        for sentence in sentence_matches:
            statement = sentence.strip()
            if not statement:
                continue
            normalized = statement.lower()
            if normalized in seen:
                continue
            seen.add(normalized)

            fact = Fact(
                id=CanonicalIdGenerator.fact_id(statement),
                statement=statement,
                evidence_refs=ev_ids[:],
                confidence=0.6,
                verification_state=VerificationState.PENDING,
                provenance=make_provenance(source, "fact_extractor"),
                metadata=Metadata(tags=["extracted"]),
            )
            facts.append(fact)

        return facts


class RelationshipExtractor:
    """Identifies relationships between entities.

    Uses pattern matching to find relational constructions like
    "X depends on Y", "X implements Y", etc.
    """

    RELATION_TYPES = {
        "uses": "uses",
        "depends on": "depends_on",
        "extends": "extends",
        "implements": "implements",
        "contains": "contains",
        "creates": "creates",
        "manages": "manages",
        "requires": "requires",
        "supports": "supports",
        "provides": "provides",
        "enables": "enables",
        "integrates with": "integrates_with",
    }

    def extract(
        self,
        content: str,
        entity_names: set[str],
        source: str = "unknown",
    ) -> list[Relationship]:
        """Identify relationships between entities.

        Args:
            content: The source text to extract relationships from.
            entity_names: Set of known entity names to match against.
            source: Identifier for the source document.

        Returns:
            A list of discovered Relationship instances.
        """
        relationships: list[Relationship] = []
        seen: set[str] = set()

        for verb, rel_type in self.RELATION_TYPES.items():
            sorted_names = sorted(entity_names, key=len, reverse=True)
            name_pattern = "|".join(re.escape(e) for e in sorted_names)
            pattern = re.compile(
                rf"\b({name_pattern})\s+{re.escape(verb)}\s+({name_pattern})"
            )
            matches = pattern.findall(content)
            for src_name, tgt_name in matches:
                key = f"{src_name}:{rel_type}:{tgt_name}"
                if key in seen:
                    continue
                seen.add(key)

                rel = Relationship(
                    id=CanonicalIdGenerator.relationship_id(src_name, rel_type, tgt_name),
                    source_id=CanonicalIdGenerator.entity_id(src_name),
                    target_id=CanonicalIdGenerator.entity_id(tgt_name),
                    relationship_type=rel_type,
                    evidence_refs=[],
                    confidence=0.5,
                    verification_state=VerificationState.PENDING,
                    provenance=make_provenance(source, "relationship_extractor"),
                    metadata=Metadata(tags=["extracted"]),
                )
                relationships.append(rel)

        return relationships


class EvidenceExtractor:
    """Captures source evidence from content.

    Evidence blocks are the raw text segments that support knowledge
    claims. They are immutable references that knowledge elements
    point to.
    """

    PARAGRAPH_PATTERN = re.compile(r"(?:^|\n\n)([^\n][\s\S]*?)(?=\n\n|$)")

    def extract(self, content: str, source: str = "unknown") -> list[Evidence]:
        """Capture source evidence blocks from content.

        Args:
            content: The source text to extract evidence from.
            source: Identifier for the source document.

        Returns:
            A list of Evidence instances representing text segments.
        """
        seen: set[str] = set()
        evidence_list: list[Evidence] = []

        paragraphs = self.PARAGRAPH_PATTERN.findall(content)
        for para in paragraphs:
            text = para.strip()
            if len(text) < 20:
                continue
            normalized = text.lower()
            if normalized in seen:
                continue
            seen.add(normalized)

            ev = Evidence(
                id=CanonicalIdGenerator.evidence_id(text),
                content=text,
                source=source,
                confidence=1.0,
                verification_state=VerificationState.PENDING,
                provenance=make_provenance(source, "evidence_extractor"),
                metadata=Metadata(tags=["extracted"]),
            )
            evidence_list.append(ev)

        return evidence_list


class ExtractionPipeline:
    """Orchestrates the full extraction process.

    Runs all extractors in sequence and returns a combined
    ExtractionResult with cross-linked evidence references.
    """

    def __init__(self) -> None:
        self.entity_extractor = EntityExtractor()
        self.concept_extractor = ConceptExtractor()
        self.fact_extractor = FactExtractor()
        self.relationship_extractor = RelationshipExtractor()
        self.evidence_extractor = EvidenceExtractor()

    def extract(self, content: str, source: str = "unknown") -> ExtractionResult:
        """Run the full extraction pipeline.

        Args:
            content: The source text to process.
            source: Identifier for the source document.

        Returns:
            An ExtractionResult containing all discovered knowledge elements.
        """
        evidence = self.evidence_extractor.extract(content, source)
        ev_ids = [e.id for e in evidence]

        entities = self.entity_extractor.extract(content, source)
        concepts = self.concept_extractor.extract(content, source)
        facts = self.fact_extractor.extract(content, ev_ids, source)
        entity_names = {e.name for e in entities}
        relationships = self.relationship_extractor.extract(content, entity_names, source)

        return ExtractionResult(
            entities=entities,
            concepts=concepts,
            facts=facts,
            relationships=relationships,
            evidence=evidence,
        )
