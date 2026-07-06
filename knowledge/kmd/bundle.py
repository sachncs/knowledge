"""OKF v0.1 directory-bundle serializer with validation.

This module implements the **OKF v0.1** (Open Knowledge Format) bundle
specification.  A bundle is a directory of Markdown files on disk::

    my-bundle/
    ├── index.md           ← root index (lists all concepts)
    ├── some-concept.md    ← concept file with YAML frontmatter
    └── guide/
        ├── index.md       ← subdirectory index
        └── getting-started.md

Each concept file uses a simple YAML frontmatter block (between ``---``
delimiters)::

    ---
    id: some-concept
    title: "Some Concept"
    type: concept
    tags: ["tag-a", "tag-b"]
    ---

    ## Some Concept

    Body content in Markdown.

Design rationale
----------------
* **No external YAML parser** — frontmatter is written using a simple
  key-value convention.  This avoids adding a PyYAML dependency for a
  very limited schema.  The :func:`yaml_escape` function handles control
  characters manually.
* **Path-based grouping** — concepts can be grouped into subdirectories
  via a :attr:`path_map` that maps tag names to subdirectory paths.
* **Validation** — :meth:`validate` checks that all index links resolve
  and no orphan files exist (files not linked from any index).

Security
--------
YAML escaping (see :meth:`yaml_escape`) prevents injection attacks via
concept names or tags that contain control characters, YAML special
characters, or sequences that could break the frontmatter parser.
"""

from __future__ import annotations

import os
import re
from collections import defaultdict

from knowledge.models import Concept, KnowledgeGraph

Entry = tuple[str, str, str | None]


class BundleSerializer:
    """Serializes a :class:`~knowledge.models.KnowledgeGraph` into an OKF v0.1 directory bundle.

    Usage
    -----
    ::

        serializer = BundleSerializer(path_map={"guide": "docs"})
        count = serializer.serialize(graph, "./my-bundle")
        issues = serializer.validate("./my-bundle")
    """

    def __init__(self, path_map: dict[str, str] | None = None) -> None:
        """Initialise the serializer.

        Args:
            path_map: Optional mapping of tag → subdirectory path.
                Concepts with a matching tag are placed in the
                corresponding subdirectory instead of the bundle root.
        """
        self.path_map = path_map or {}

    def serialize(self, graph: KnowledgeGraph, output_dir: str) -> int:
        """Write the bundle and return the number of concept files created.

        The method:

        1. Groups concepts by their tag-driven path (via :meth:`find_path`).
        2. Creates intermediate directories as needed.
        3. Writes one ``.md`` file per concept (via :meth:`write_concept`).
        4. Writes ``index.md`` for each subdirectory and a root ``index.md``.
        5. Removes stale ``.md`` files not part of the current graph.

        Args:
            graph: The knowledge graph to serialize.
            output_dir: Output directory (created if it does not exist).

        Returns:
            Number of concept files written.
        """
        path_groups: dict[str, list[Entry]] = defaultdict(list)
        flat_concepts: list[Entry] = []

        for cid, concept in sorted(graph.concepts.items()):
            subdir = self.find_path(concept.tags)
            entry = (cid, concept.name, concept.description or None)
            if subdir:
                path_groups[subdir].append(entry)
            else:
                flat_concepts.append(entry)

        all_dirs: set[str] = set()
        for subdir in path_groups:
            parts = subdir.split("/")
            for i in range(1, len(parts) + 1):
                all_dirs.add("/".join(parts[:i]))

        written_files: set[str] = set()
        written = 0

        for subdir, entries in sorted(path_groups.items()):
            target = os.path.join(output_dir, subdir)
            os.makedirs(target, exist_ok=True)
            for cid, _, _ in entries:
                filepath = self.write_concept(target, graph.concepts[cid])
                written_files.add(filepath)
                written += 1

        for cid, _, _ in flat_concepts:
            filepath = self.write_concept(output_dir, graph.concepts[cid])
            written_files.add(filepath)
            written += 1

        # write subdirectory indexes (only for dirs that have direct entries)
        written_indexes: set[str] = set()
        for subdir in sorted(all_dirs):
            target = os.path.join(output_dir, subdir)
            raw_entries = path_groups.get(subdir, [])
            if not raw_entries:
                continue
            title = self.dir_title(subdir)
            index_entries: list[Entry] = [(cid, name, None) for cid, name, _ in raw_entries]
            filepath = self.write_index(target, title, "index", index_entries)
            written_files.add(filepath)
            written_indexes.add(subdir)

        # root index — only link subdirs that actually got an index written
        root_entries: list[Entry] = [(cid, name, None) for cid, name, _ in flat_concepts]
        for subdir in sorted(all_dirs & written_indexes):
            title = self.dir_title(subdir)
            root_entries.append((subdir, title, subdir))
        filepath = self.write_index(output_dir, "Knowledge Bundle", "bundle", root_entries)
        written_files.add(filepath)

        # remove stale .md files not part of this serialization
        for dirpath, _, filenames in os.walk(output_dir):
            for f in filenames:
                if not f.endswith(".md"):
                    continue
                filepath = os.path.join(dirpath, f)
                if filepath not in written_files:
                    os.remove(filepath)

        return written

    def validate(self, output_dir: str) -> list[str]:
        """Validate a written bundle for structural consistency.

        Checks performed:

        1. Root ``index.md`` exists.
        2. All links in every ``index.md`` resolve to existing files.
        3. No orphan ``.md`` files (files not referenced by any index).

        Args:
            output_dir: The bundle directory to validate.

        Returns:
            A list of warning/error messages.  An empty list means the
            bundle is structurally valid.
        """
        issues: list[str] = []
        index_path = os.path.join(output_dir, "index.md")

        if not os.path.isfile(index_path):
            issues.append(f"Missing root index.md at {index_path}")
            return issues

        # Collect all files listed in indexes
        indexed_files: set[str] = set()
        for root, _, files in os.walk(output_dir):
            if "index.md" in files:
                valid, broken = self.links_in_index(os.path.join(root, "index.md"), root)
                indexed_files.update(valid)
                issues.extend(broken)

        # Check all concept files are indexed
        all_files: set[str] = set()
        for root, _, files in os.walk(output_dir):
            for f in files:
                if f.endswith(".md"):
                    all_files.add(os.path.normpath(os.path.join(root, f)))

        for f in sorted(all_files - indexed_files - {os.path.normpath(index_path)}):
            rel = os.path.relpath(f, output_dir)
            issues.append(f"Orphan file not listed in any index: {rel}")

        return issues

    @staticmethod
    def links_in_index(index_path: str, base_dir: str) -> tuple[set[str], list[str]]:
        """Extract all linked file paths from an ``index.md``.

        Parses Markdown links of the form ``[text](path)`` and resolves
        them relative to *base_dir*.

        Args:
            index_path: Path to the index file.
            base_dir: Directory to resolve relative links against.

        Returns:
            A tuple of ``(set_of_resolved_file_paths, list_of_broken_links)``.
        """
        files: set[str] = set()
        broken: list[str] = []
        try:
            with open(index_path, encoding="utf-8") as f:
                content = f.read()
        except OSError as exc:
            broken.append(f"Cannot read {os.path.basename(index_path)}: {exc}")
            return files, broken

        for match in re.finditer(r"\[([^\]]+)\]\(([^)]+)\)", content):
            link = match.group(2)
            if link.startswith(("http://", "https://", "ftp://")):
                continue
            resolved = os.path.normpath(os.path.join(base_dir, link))
            if os.path.isfile(resolved):
                files.add(resolved)
            else:
                rel = os.path.relpath(resolved, os.path.dirname(index_path))
                broken.append(f"Broken link in {os.path.basename(index_path)}: {rel}")
        return files, broken

    def find_path(self, tags: list[str]) -> str:
        """Find the first subdirectory path matching a tag in *tags*.

        Iterates over tags in order and checks :attr:`path_map`.  The
        first matching tag's value is returned.

        Args:
            tags: Concept tag list.

        Returns:
            The subdirectory path if a tag matches, otherwise an empty
            string (meaning "place at bundle root").
        """
        for tag in tags:
            if tag in self.path_map:
                return self.path_map[tag]
        return ""

    @staticmethod
    def dir_title(subdir: str) -> str:
        """Convert a subdirectory path to a human-readable title.

        Replaces hyphens and underscores with spaces, splits on ``/``,
        title-cases each part, and joins with ``" / "``.

        Example: ``"getting-started/quick-start"`` → ``"Getting Started / Quick Start"``
        """
        parts = subdir.replace("-", " ").replace("_", " ").split("/")
        return " / ".join(p.title() for p in parts)

    @staticmethod
    def yaml_escape(value: str) -> str:
        """Escape *value* for safe embedding in a double-quoted YAML string.

        Escaping order (to maintain reversibility):

        1. Backslash ``\\`` → ``\\\\``
        2. Double quote ``"`` → ``\\"``
        3. Newline ``\\n`` → ``\\n`` (literal)
        4. Carriage return ``\\r`` → ``\\r``
        5. Tab ``\\t`` → ``\\t``
        6. Control characters ``\\x00-\\x08``, ``\\x0b``, ``\\x0c``,
           ``\\x0e-\\x1f`` → ``\\xNN`` hexadecimal escape.

        The reverse operation is :func:`knowledge.llm.manager.yaml_unescape`.

        Args:
            value: The raw string value.

        Returns:
            A YAML-safe escaped string suitable for use inside double
            quotes in frontmatter.
        """
        value = value.replace("\\", "\\\\")
        value = value.replace('"', '\\"')
        value = value.replace("\n", "\\n")
        value = value.replace("\r", "\\r")
        value = value.replace("\t", "\\t")
        value = re.sub(
            r"[\x00-\x08\x0b\x0c\x0e-\x1f]",
            lambda m: f"\\x{ord(m.group(0)):02x}",
            value,
        )
        return value

    def write_concept(self, directory: str, concept: Concept) -> str:
        """Write a single concept ``.md`` file to *directory*.

        The file consists of YAML frontmatter (delimited by ``---``)
        followed by a Markdown body section.

        Frontmatter fields: ``id``, ``title``, ``type``, and optionally
        ``tags``.

        Args:
            directory: The directory to write into.
            concept: The concept to serialize.

        Returns:
            The absolute path to the written file.
        """
        tag_list = (
            ", ".join(f'"{self.yaml_escape(t)}"' for t in concept.tags) if concept.tags else ""
        )
        frontmatter_lines = [
            "---",
            f"id: {concept.id}",
            f'title: "{self.yaml_escape(concept.name)}"',
            "type: concept",
        ]
        if tag_list:
            frontmatter_lines.append(f"tags: [{tag_list}]")
        frontmatter_lines.append("")
        frontmatter_lines.append("---")

        body_lines = [""]
        if concept.description:
            body_lines.append(f"## {concept.name}")
            body_lines.append("")
            body_lines.append(concept.description)

        content = "\n".join(frontmatter_lines + body_lines) + "\n"
        filepath = os.path.join(directory, f"{concept.id}.md")
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        return os.path.normpath(filepath)

    def write_index(
        self,
        directory: str,
        title: str,
        index_type: str,
        entries: list[Entry],
    ) -> str:
        """Write an ``index.md`` file listing bundle concepts.

        Args:
            directory: Directory to write the index into.
            title: Index display title.
            index_type: ``"index"`` for subdirectory indexes,
                ``"bundle"`` for the root index.
            entries: List of ``(id, name, link_path)`` tuples.
                ``link_path`` is ``None`` for concept links (resolved
                via ``id.md``) or a subdirectory name (resolved via
                ``subdir/index.md``).

        Returns:
            The absolute path to the written index file.
        """
        frontmatter_lines = [
            "---",
            f"id: {self.index_id(directory, title)}",
            f'title: "{self.yaml_escape(title)}"',
            f"type: {index_type}",
            "",
            "---",
        ]

        body_lines = ["", f"# {title}", ""]
        for eid, name, link_path in entries:
            if link_path:
                body_lines.append(f"- [{name}]({link_path}/index.md)")
            else:
                body_lines.append(f"- [{name}]({eid}.md)")

        content = "\n".join(frontmatter_lines + body_lines) + "\n"
        filepath = os.path.join(directory, "index.md")
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        return os.path.normpath(filepath)

    @staticmethod
    def index_id(directory: str, title: str) -> str:
        """Generate a kebab-case slug from a directory path and title.

        If *directory* is a non-root path the basename is used as the
        slug base; otherwise the title is lowered and hyphenated.

        Args:
            directory: The directory being indexed (may be empty or
                ``"."`` for the root).
            title: The index title (fallback when directory is root).

        Returns:
            A kebab-case string usable as an index ``id``.
        """
        base = (
            os.path.basename(os.path.normpath(directory))
            if directory and directory not in (".", "")
            else title.lower()
        )
        return base.replace(" ", "-").replace("/", "-").lower()
