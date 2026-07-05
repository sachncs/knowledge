"""Knowledge bundle management — create, update, remove via LLM."""

from __future__ import annotations

import logging
import os
import re

from knowledge.exceptions import KnowledgeError
from knowledge.kmd.bundle import BundleSerializer
from knowledge.llm.extractor import LLMExtractor
from knowledge.models import Concept, KnowledgeGraph

logger = logging.getLogger(__name__)


class KnowledgeBundleManager:
    """High-level operations for LLM-based knowledge bundles."""

    def __init__(self, model: str = "gpt-4o") -> None:
        self.model = model

    def create(self, source_text: str, output_dir: str, source_url: str = "") -> int:
        """Extract concepts from source and write an OKF bundle.

        Returns the number of concept files written.
        """
        extractor = LLMExtractor(model=self.model)
        graph = extractor.extract(source_text, source_url=source_url)
        os.makedirs(output_dir, exist_ok=True)
        return BundleSerializer().serialize(graph, output_dir)

    def update(self, source_text: str, bundle_dir: str, source_url: str = "") -> int:
        """Re-extract concepts from source and overwrite the existing bundle.

        Returns the number of concept files written.
        """
        extractor = LLMExtractor(model=self.model)
        graph = extractor.extract(source_text, source_url=source_url)
        os.makedirs(bundle_dir, exist_ok=True)
        return BundleSerializer().serialize(graph, bundle_dir)

    def remove(self, concept_ids: list[str], bundle_dir: str) -> int:
        """Remove specific concepts from an existing bundle by ID.

        Returns the number of concept files written.
        """
        graph = self.read_bundle(bundle_dir)
        for cid in concept_ids:
            graph = graph.remove_concept(cid)
        os.makedirs(bundle_dir, exist_ok=True)
        return BundleSerializer().serialize(graph, bundle_dir)

    @staticmethod
    def read_bundle(bundle_dir: str) -> KnowledgeGraph:
        """Read existing bundle files back into a KnowledgeGraph."""
        graph = KnowledgeGraph()
        index_path = os.path.join(bundle_dir, "index.md")
        if not os.path.isfile(index_path):
            raise KnowledgeError(f"No bundle found at {bundle_dir}")

        for root, dirs, files in os.walk(bundle_dir):
            for file in files:
                if file == "index.md" or not file.endswith(".md"):
                    continue
                filepath = os.path.join(root, file)
                concept = parse_concept_file(filepath)
                if concept is not None:
                    graph = graph.add_concept(concept)

        return graph


def parse_concept_file(filepath: str) -> Concept | None:
    """Parse a single concept .md file back into a Concept."""
    try:
        with open(filepath, encoding="utf-8") as f:
            content = f.read()
    except OSError as exc:
        logger.warning("Skipping unreadable concept file %s: %s", filepath, exc)
        return None

    frontmatter_match = re.match(r"^---\s*\n(.+?)\n---", content, re.DOTALL)
    if not frontmatter_match:
        return None

    fm_lines = frontmatter_match.group(1).split("\n")
    metadata: dict[str, str | list[str]] = {}
    for line in fm_lines:
        if ":" in line:
            key, _, value = line.partition(":")
            key = key.strip()
            value = value.strip().strip('"')
            if key == "tags":
                raw = value.strip("[]").strip()
                value = [t.strip().strip('"') for t in raw.split(",")] if raw else []
            metadata[key] = value

    cid = metadata.get("id")
    name = metadata.get("title")
    if not cid or not name:
        return None

    body = content[frontmatter_match.end():].strip()
    # Strip leading h1/h2 if present
    body = re.sub(r"^#+\s+.*", "", body, count=1).strip()

    raw_tags = metadata.get("tags", [])
    tags: list[str] = raw_tags if isinstance(raw_tags, list) else []
    return Concept(
        id=str(cid),
        name=str(name),
        description=body if body else None,
        tags=tags,
    )
