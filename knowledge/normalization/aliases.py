"""Alias resolution — detecting when different names refer to the same entity.

Alias resolution is a deterministic normalization step that identifies
entities with the same canonical name and consolidates their aliases.
"""

from __future__ import annotations

from knowledge.models import Entity, KnowledgeGraph
from knowledge.normalization.identifiers import CanonicalIdGenerator


class AliasResolver:
    """Resolves aliases and consolidates entities with equivalent names.

    Two entities are considered the same if their canonical (normalized)
    names match. When duplicates are found, aliases are merged into the
    canonical entity.
    """

    def resolve(self, graph: KnowledgeGraph) -> KnowledgeGraph:
        name_map: dict[str, Entity] = {}

        for entity in graph.entities.values():
            canonical_name = CanonicalIdGenerator.normalize_name(entity.name)
            if canonical_name in name_map:
                existing = name_map[canonical_name]
                merged_aliases = list(
                    set(existing.aliases + entity.aliases + [entity.name])
                )
                merged_aliases.sort()
                name_map[canonical_name] = existing.model_copy(
                    update={"aliases": merged_aliases}
                )
            else:
                name_map[canonical_name] = entity

        return graph.model_copy(
            update={"entities": {e.id: e for e in name_map.values()}}
        )
