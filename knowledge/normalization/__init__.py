"""Knowledge normalization — transforming extracted knowledge into canonical form.

Normalization passes run after extraction and before verification.
They ensure the KnowledgeGraph is in a canonical, well-structured state.
"""

from knowledge.normalization.aliases import AliasResolver
from knowledge.normalization.dedup import DuplicateDetector
from knowledge.normalization.identifiers import CanonicalIdGenerator, StableIdGenerator

__all__ = [
    "CanonicalIdGenerator",
    "StableIdGenerator",
    "AliasResolver",
    "DuplicateDetector",
]
