"""Bundle serialization — OKF v0.1 directory format.

This package provides the sole serializer for writing
:class:`~knowledge.models.KnowledgeGraph` objects to disk as
OKF v0.1 bundles (a directory of Markdown files with YAML frontmatter).

Public API
----------
:class:`~knowledge.kmd.bundle.BundleSerializer` — serializes
a ``KnowledgeGraph`` to disk, validates a written bundle, and
provides helpers for YAML escaping and path resolution.
"""

from knowledge.kmd.bundle import BundleSerializer

__all__ = [
    "BundleSerializer",
]
