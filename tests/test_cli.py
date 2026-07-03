"""Tests for the CLI."""

import os
import tempfile

import pytest

from knowledge.cli import build_parser, main
from knowledge.models import Entity, KnowledgeGraph
from knowledge.okf import OKFSerializer


def run_cmd(args: list[str]) -> None:
    """Run a CLI command by parsing args and calling the handler directly."""
    parser = build_parser()
    parsed = parser.parse_args(args)
    parsed.func(parsed)


class TestCLICommands:
    def test_create_text(self) -> None:
        run_cmd(["create", "Python is a language.", "--no-verify"])

    def test_create_markdown(self) -> None:
        run_cmd(["create", "Python is a language.", "-f", "markdown", "--no-verify"])

    def test_create_with_output(self) -> None:
        with tempfile.NamedTemporaryFile(suffix=".md", delete=False) as f:
            fname = f.name
        run_cmd(["create", "Python is a language.", "-o", fname, "--no-verify"])

    def test_read(self) -> None:
        graph = KnowledgeGraph()
        graph = graph.add_entity(Entity(name="Python", id="ent_001"))
        serializer = OKFSerializer()
        content = serializer.serialize(graph)
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            f.write(content)
            fname = f.name
        run_cmd(["read", fname])

    def test_inspect(self) -> None:
        graph = KnowledgeGraph()
        graph = graph.add_entity(Entity(name="Python", id="ent_001"))
        serializer = OKFSerializer()
        content = serializer.serialize(graph)
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            f.write(content)
            fname = f.name
        run_cmd(["inspect", fname])

    def test_score(self) -> None:
        graph = KnowledgeGraph()
        graph = graph.add_entity(Entity(name="Python", id="ent_001"))
        serializer = OKFSerializer()
        content = serializer.serialize(graph)
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            f.write(content)
            fname = f.name
        run_cmd(["score", fname])

    def test_verify(self) -> None:
        graph = KnowledgeGraph()
        graph = graph.add_entity(Entity(name="Python", id="ent_001"))
        serializer = OKFSerializer()
        content = serializer.serialize(graph)
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            f.write(content)
            fname = f.name
        run_cmd(["verify", fname])

    def test_diff(self) -> None:
        graph_a = KnowledgeGraph()
        graph_a = graph_a.add_entity(Entity(name="Python", id="ent_001"))
        graph_b = KnowledgeGraph()
        graph_b = graph_b.add_entity(Entity(name="Java", id="ent_002"))
        serializer = OKFSerializer()
        content_a = serializer.serialize(graph_a)
        content_b = serializer.serialize(graph_b)
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            f.write(content_a)
            fname_a = f.name
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            f.write(content_b)
            fname_b = f.name
        run_cmd(["diff", fname_a, fname_b])

    def test_update(self) -> None:
        graph = KnowledgeGraph()
        graph = graph.add_entity(Entity(name="Python", id="ent_001"))
        serializer = OKFSerializer()
        content = serializer.serialize(graph)
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            f.write(content)
            fname = f.name
        run_cmd(["update", fname, "JavaScript is a language."])

    def test_unknown_command(self) -> None:
        parser = build_parser()
        try:
            parser.parse_args(["unknown_command"])
        except SystemExit:
            pass

    def test_update_with_output(self) -> None:
        graph = KnowledgeGraph()
        graph = graph.add_entity(Entity(name="Python", id="ent_001"))
        serializer = OKFSerializer()
        content = serializer.serialize(graph)
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            f.write(content)
            fname = f.name
        with tempfile.NamedTemporaryFile(suffix=".md", delete=False) as out:
            outname = out.name
        run_cmd(["update", fname, "JavaScript is a language.", "-o", outname])
        assert os.path.exists(outname)

    def test_verify_with_output(self) -> None:
        graph = KnowledgeGraph()
        graph = graph.add_entity(Entity(name="Python", id="ent_001"))
        serializer = OKFSerializer()
        content = serializer.serialize(graph)
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            f.write(content)
            fname = f.name
        with tempfile.NamedTemporaryFile(suffix=".md", delete=False) as out:
            outname = out.name
        run_cmd(["verify", fname, "-o", outname])
        assert os.path.exists(outname)

    def test_main_catches_exceptions(self) -> None:
        with pytest.raises(SystemExit):
            main(["create", "http://invalid-source"])
