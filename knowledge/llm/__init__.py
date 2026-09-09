"""LLM-powered document extraction and knowledge bundle management.

This package wraps litellm to extract structured concepts
(:class:`~knowledge.models.Concept`) from raw document text, and
provides high-level operations (create / update / remove) for
managing OKF v0.1 bundles on disk.

Public API
----------
* :class:`~knowledge.llm.extractor.LLMExtractor` — splits a document
  into heading-delimited sections and extracts one Concept per section
  via an LLM.
* :class:`~knowledge.llm.manager.KnowledgeBundleManager` — orchestrates
  extraction and serialization into an OKF v0.1 bundle (create, update,
  remove).
"""

from knowledge.llm.extractor import LLMExtractor
from knowledge.llm.manager import KnowledgeBundleManager

__all__ = [
    "LLMExtractor",
    "KnowledgeBundleManager",
]
