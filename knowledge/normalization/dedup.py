"""Duplicate detection and merging for knowledge elements.

Uses deterministic name comparison to find potential duplicates
and merge them into canonical representations.
"""

from __future__ import annotations

from knowledge.models import Concept, Entity, KnowledgeGraph
from knowledge.normalization.identifiers import CanonicalIdGenerator


class DuplicateDetector:
    """Detects and merges duplicate entities and concepts.

    Two elements are considered duplicates if their canonical
    (normalized) names are identical. The first occurrence is
    kept as the canonical version; subsequent occurrences have
    their aliases merged in.
    """

    def deduplicate_entities(self, graph: KnowledgeGraph) -> KnowledgeGraph:
        seen: dict[str, Entity] = {}

        for entity in graph.entities.values():
            key = CanonicalIdGenerator.normalize_name(entity.name)
            if key in seen:
                existing = seen[key]
                merged_aliases = list(
                    set(existing.aliases + entity.aliases + [entity.name, existing.name])
                )
                merged_aliases.sort()
                updated = existing.model_copy(
                    update={"aliases": merged_aliases}
                )
                seen[key] = updated
            else:
                seen[key] = entity

        return graph.model_copy(
            update={"entities": {e.id: e for e in seen.values()}}
        )

    def deduplicate_concepts(self, graph: KnowledgeGraph) -> KnowledgeGraph:
        seen: dict[str, Concept] = {}

        for concept in graph.concepts.values():
            key = CanonicalIdGenerator.normalize_name(concept.name)
            if key in seen:
                existing = seen[key]
                updated = existing.model_copy(
                    update={
                        "description": existing.description or concept.description,
                    }
                )
                seen[key] = updated
            else:
                seen[key] = concept

        return graph.model_copy(
            update={"concepts": {c.id: c for c in seen.values()}}
        )

    def deduplicate_all(self, graph: KnowledgeGraph) -> KnowledgeGraph:
        graph = self.deduplicate_entities(graph)
        graph = self.deduplicate_concepts(graph)
        return graph
