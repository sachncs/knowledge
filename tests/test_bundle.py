"""Tests for BundleSerializer — OKF v0.1 serialization and validation."""

import os
import tempfile

from knowledge.kmd.bundle import BundleSerializer
from knowledge.llm.manager import KnowledgeBundleManager, parse_concept_file
from knowledge.models import Concept, KnowledgeGraph


def _make_graph(*concepts: Concept) -> KnowledgeGraph:
    g = KnowledgeGraph()
    for c in concepts:
        g = g.add_concept(c)
    return g


SAMPLE_CONCEPTS = [
    Concept(id="intro", name="Introduction", description="Welcome.", tags=["guide"]),
    Concept(
        id="installation",
        name="Installation",
        description="How to install.",
        tags=["guide"],
    ),
    Concept(
        id="api-ref",
        name="API Reference",
        description="Full API docs.",
        tags=["reference"],
    ),
]


class TestBundleSerializer:
    def test_serialize_creates_concept_files(self) -> None:
        graph = _make_graph(*SAMPLE_CONCEPTS)
        with tempfile.TemporaryDirectory() as tmpdir:
            serializer = BundleSerializer()
            count = serializer.serialize(graph, tmpdir)
            assert count == 3
            assert os.path.isfile(os.path.join(tmpdir, "intro.md"))
            assert os.path.isfile(os.path.join(tmpdir, "installation.md"))
            assert os.path.isfile(os.path.join(tmpdir, "api-ref.md"))

    def test_serialize_creates_root_index(self) -> None:
        graph = _make_graph(*SAMPLE_CONCEPTS)
        with tempfile.TemporaryDirectory() as tmpdir:
            BundleSerializer().serialize(graph, tmpdir)
            assert os.path.isfile(os.path.join(tmpdir, "index.md"))

    def test_serialize_empty_graph(self) -> None:
        graph = KnowledgeGraph()
        with tempfile.TemporaryDirectory() as tmpdir:
            count = BundleSerializer().serialize(graph, tmpdir)
            assert count == 0
            assert os.path.isfile(os.path.join(tmpdir, "index.md"))

    def test_serialize_groups_by_tag_via_path_map(self) -> None:
        path_map = {"guide": "docs/guides", "reference": "docs/reference"}
        graph = _make_graph(*SAMPLE_CONCEPTS)
        with tempfile.TemporaryDirectory() as tmpdir:
            BundleSerializer(path_map=path_map).serialize(graph, tmpdir)
            assert os.path.isfile(os.path.join(tmpdir, "docs", "guides", "intro.md"))
            assert os.path.isfile(os.path.join(tmpdir, "docs", "guides", "installation.md"))
            assert os.path.isfile(os.path.join(tmpdir, "docs", "reference", "api-ref.md"))

    def test_round_trip(self) -> None:
        original = _make_graph(*SAMPLE_CONCEPTS)
        with tempfile.TemporaryDirectory() as tmpdir:
            BundleSerializer().serialize(original, tmpdir)
            restored = KnowledgeBundleManager.read_bundle(tmpdir)
            assert len(restored.concepts) == 3
            for cid in ("intro", "installation", "api-ref"):
                assert cid in restored.concepts
                assert restored.concepts[cid].name == original.concepts[cid].name
                assert restored.concepts[cid].description == original.concepts[cid].description
                assert restored.concepts[cid].tags == original.concepts[cid].tags

    def test_write_concept_with_special_chars(self) -> None:
        c = Concept(
            id="special",
            name='Hello "World" & More',
            description="Line1\nLine2\nTab\there",
            tags=['tag"with"quotes', "normal"],
        )
        graph = _make_graph(c)
        with tempfile.TemporaryDirectory() as tmpdir:
            BundleSerializer().serialize(graph, tmpdir)
            filepath = os.path.join(tmpdir, "special.md")
            assert os.path.isfile(filepath)
            parsed = parse_concept_file(filepath)
            assert parsed is not None
            assert parsed.id == "special"
            assert parsed.name == 'Hello "World" & More'
            assert parsed.description == "Line1\nLine2\nTab\there"
            assert parsed.tags == ['tag"with"quotes', "normal"]

    def test_validate_clean_bundle(self) -> None:
        graph = _make_graph(*SAMPLE_CONCEPTS)
        with tempfile.TemporaryDirectory() as tmpdir:
            BundleSerializer().serialize(graph, tmpdir)
            issues = BundleSerializer().validate(tmpdir)
            assert issues == [], f"Expected clean bundle, got: {issues}"

    def test_validate_clean_bundle_counts_files(self) -> None:
        """Verify that validation correctly indexes all concept files."""
        graph = _make_graph(*SAMPLE_CONCEPTS)
        with tempfile.TemporaryDirectory() as tmpdir:
            BundleSerializer().serialize(graph, tmpdir)
            issues = BundleSerializer().validate(tmpdir)
            assert issues == []
            # All concept files exist and are linked from the index
            for c in SAMPLE_CONCEPTS:
                assert os.path.isfile(os.path.join(tmpdir, f"{c.id}.md"))

    def test_validate_missing_index(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            issues = BundleSerializer().validate(tmpdir)
            assert len(issues) == 1
            assert "Missing root index.md" in issues[0]

    def test_validate_orphan_file(self) -> None:
        graph = _make_graph(*SAMPLE_CONCEPTS)
        with tempfile.TemporaryDirectory() as tmpdir:
            BundleSerializer().serialize(graph, tmpdir)
            # Add a file not listed in any index
            orphan_path = os.path.join(tmpdir, "orphan.md")
            with open(orphan_path, "w") as f:
                f.write("# Orphan\n")
            issues = BundleSerializer().validate(tmpdir)
            assert any("Orphan" in i for i in issues)

    def test_validate_finds_broken_links(self) -> None:
        """A link in index.md pointing to a non-existent file."""
        graph = _make_graph(*SAMPLE_CONCEPTS)
        with tempfile.TemporaryDirectory() as tmpdir:
            BundleSerializer().serialize(graph, tmpdir)
            # Corrupt the index to contain a broken link
            index_path = os.path.join(tmpdir, "index.md")
            with open(index_path, "a") as f:
                f.write("\n- [Missing](missing.md)\n")
            issues = BundleSerializer().validate(tmpdir)
            assert any("Broken link" in i for i in issues)

    def test_index_id_variants(self) -> None:
        serializer = BundleSerializer()
        assert serializer.index_id("subdir", "Title") == "subdir"
        assert serializer.index_id("", "Root") == "root"
        assert serializer.index_id(".", "Root") == "root"

    def test_dir_title_formatting(self) -> None:
        assert BundleSerializer.dir_title("rules/language") == "Rules / Language"
        assert BundleSerializer.dir_title("api-v2") == "Api V2"

    def test_validate_skips_absolute_urls(self) -> None:
        """links_in_index should skip http:// and https:// URLs."""
        with tempfile.TemporaryDirectory() as tmpdir:
            index_content = (
                "---\nid: test\ntitle: Test\ntype: index\n---\n\n"
                "- [Google](https://google.com)\n"
                "- [Local](local.md)\n"
            )
            index_path = os.path.join(tmpdir, "index.md")
            with open(index_path, "w", encoding="utf-8") as f:
                f.write(index_content)
            # Create the local file so that only the URL is the unknown
            local_path = os.path.join(tmpdir, "local.md")
            with open(local_path, "w", encoding="utf-8") as f:
                f.write("---\nid: local\ntitle: Local\ntype: concept\n---\n\ncontent\n")
            issues = BundleSerializer().validate(tmpdir)
            # No "Broken link" about google.com
            url_issues = [i for i in issues if "google.com" in i or "google" in i]
            assert not url_issues, f"Should skip absolute URLs: {url_issues}"

    def test_yaml_escape_round_trip(self) -> None:
        inputs = [
            "plain",
            'with "quotes"',
            "with\\backslash",
            "multi\nline",
            "tab\there",
            "\x00null",
        ]
        for raw in inputs:
            escaped = BundleSerializer.yaml_escape(raw)
            # Verify no YAML-illegal characters remain
            assert "\n" not in escaped or "\\n" in escaped
            assert "\t" not in escaped or "\\t" in escaped
            for ch in ("\x00", "\x01", "\x02"):
                assert ch not in escaped
