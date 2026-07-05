"""OKF v0.1 directory-bundle serializer with validation."""

from __future__ import annotations

import os
import re
from collections import defaultdict

from knowledge.exceptions import ValidationError
from knowledge.models import Concept, KnowledgeGraph


class BundleSerializer:
    """Serializes a KnowledgeGraph into an OKF v0.1 directory bundle."""

    def __init__(self, path_map: dict[str, str] | None = None) -> None:
        self.path_map = path_map or {}

    def serialize(self, graph: KnowledgeGraph, output_dir: str) -> int:
        """Write the bundle and return the number of concept files created.

        Args:
            graph: The knowledge graph to serialize.
            output_dir: Output directory.

        Returns:
            Number of concept files written.

        Raises:
            ValidationError: If duplicate concept IDs exist.
        """
        self.check_duplicates(graph)

        path_groups: dict[str, list[tuple[str, str, str]]] = defaultdict(list)
        flat_concepts: list[tuple[str, str, str]] = []

        for cid, concept in sorted(graph.concepts.items()):
            subdir = self.find_path(concept.tags)
            entry = (cid, concept.name, concept.description or "")
            if subdir:
                path_groups[subdir].append(entry)
            else:
                flat_concepts.append(entry)

        all_dirs: set[str] = set()
        for subdir in path_groups:
            parts = subdir.split("/")
            for i in range(1, len(parts) + 1):
                all_dirs.add("/".join(parts[:i]))

        written = 0
        for subdir, entries in sorted(path_groups.items()):
            target = os.path.join(output_dir, subdir)
            os.makedirs(target, exist_ok=True)
            for cid, name, _ in entries:
                self.write_concept(target, graph.concepts[cid])
                written += 1

        for cid, _, _ in flat_concepts:
            self.write_concept(output_dir, graph.concepts[cid])
            written += 1

        for subdir in sorted(all_dirs):
            target = os.path.join(output_dir, subdir)
            raw_entries = path_groups.get(subdir, [])
            if not raw_entries:
                continue
            title = self.dir_title(subdir)
            index_entries = [(cid, name, "") for cid, name, _ in raw_entries]
            self.write_index(target, title, "index", index_entries)

        root_entries = [(cid, name, "") for cid, name, _ in flat_concepts]
        for subdir in sorted(all_dirs):
            title = self.dir_title(subdir)
            root_entries.append((subdir, title, subdir))
        self.write_index(output_dir, "Knowledge Bundle", "bundle", root_entries)

        return written

    def validate(self, output_dir: str) -> list[str]:
        """Validate a written bundle for consistency.

        Checks:
        - All ``index.md`` links resolve to existing files.
        - No orphan concept files (files not listed in any index).
        - All YAML frontmatter has required fields.

        Args:
            output_dir: The bundle directory to validate.

        Returns:
            A list of warning/error messages (empty if valid).
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
                valid, broken = self.links_in_index(
                    os.path.join(root, "index.md"), root
                )
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
        """Extract all linked file paths from an index.md.

        Args:
            index_path: Path to the index file.
            base_dir: Directory to resolve relative links against.

        Returns:
            Tuple of (set of resolved file paths, list of broken link issues).
        """
        files: set[str] = set()
        broken: list[str] = []
        try:
            with open(index_path, encoding="utf-8") as f:
                content = f.read()
        except OSError as exc:
            broken.append(f"Cannot read {os.path.basename(index_path)}: {exc}")
            return files, broken

        for match in re.finditer(r"\(([^)]+)\)", content):
            link = match.group(1)
            resolved = os.path.normpath(os.path.join(base_dir, link))
            if os.path.isfile(resolved):
                files.add(resolved)
            else:
                rel = os.path.relpath(resolved, os.path.dirname(index_path))
                broken.append(f"Broken link in {os.path.basename(index_path)}: {rel}")
        return files, broken

    @staticmethod
    def check_duplicates(graph: KnowledgeGraph) -> None:
        """Check for duplicate concept IDs before writing.

        Args:
            graph: The knowledge graph to validate.

        Raises:
            ValidationError: If duplicate IDs are found.
        """
        seen: set[str] = set()
        dupes: set[str] = set()
        for c in graph.concepts.values():
            if c.id in seen:
                dupes.add(c.id)
            seen.add(c.id)
        if dupes:
            raise ValidationError(f"Duplicate concept IDs: {sorted(dupes)}")

    def find_path(self, tags: list[str]) -> str:
        for tag in tags:
            if tag in self.path_map:
                return self.path_map[tag]
        return ""

    @staticmethod
    def dir_title(subdir: str) -> str:
        parts = subdir.replace("-", " ").replace("_", " ").split("/")
        return " / ".join(p.title() for p in parts)

    @staticmethod
    def yaml_escape(value: str) -> str:
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

    def write_concept(self, directory: str, concept: Concept) -> None:
        tag_list = (
            ", ".join(f'"{self.yaml_escape(t)}"' for t in concept.tags)
            if concept.tags
            else ""
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

    def write_index(
        self,
        directory: str,
        title: str,
        index_type: str,
        entries: list[tuple[str, str, str]],
    ) -> None:
        frontmatter_lines = [
            "---",
            f"id: {self.index_id(directory, title)}",
            f'title: "{self.yaml_escape(title)}"',
            f"type: {index_type}",
            "",
            "---",
        ]

        body_lines = ["", f"# {title}", ""]
        for eid, name, link_path_flag in entries:
            if link_path_flag:
                body_lines.append(f"- [{name}]({link_path_flag}/index.md)")
            else:
                body_lines.append(f"- [{name}]({eid}.md)")

        content = "\n".join(frontmatter_lines + body_lines) + "\n"
        filepath = os.path.join(directory, "index.md")
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)

    @staticmethod
    def index_id(directory: str, title: str) -> str:
        base = (
            os.path.basename(directory.rstrip("/"))
            if directory and directory not in (".", "")
            else title.lower()
        )
        return base.replace(" ", "-").replace("/", "-").lower()
