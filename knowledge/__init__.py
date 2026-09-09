"""Top-level entry point for the knowledge SDK.

Usage
-----
::

    from knowledge import Knowledge

    k = Knowledge()
    graph = k.create("https://example.com/doc.html")

Sub-packages
------------
* ``knowledge.llm`` — LLM-based concept extraction.
* ``knowledge.kmd`` — OKF v0.1 bundle serialization.

Public API
----------
* :class:`~knowledge.sdk.Knowledge` — single entry point for all
  create / update / remove operations.
* ``DEFAULT_MODEL`` — default LLM model identifier.
* ``__version__`` — PEP 440 version string.
"""

from knowledge.sdk import Knowledge
from knowledge.version import DEFAULT_MODEL, __version__

__all__ = [
    "Knowledge",
    "DEFAULT_MODEL",
    "__version__",
]
