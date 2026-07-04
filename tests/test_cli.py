"""Tests for the CLI."""

import tempfile
from pathlib import Path

from knowledge.cli import build_parser


class TestCLI:
    def test_parser_accepts_create(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["create", "http://example.com", "/tmp/out"])
        assert args.command == "create"
        assert args.input == "http://example.com"
        assert args.output == "/tmp/out"

    def test_create_bundle(self) -> None:
        from knowledge import Knowledge

        with tempfile.TemporaryDirectory() as tmpdir:
            Knowledge().create_bundle(
                "https://google.github.io/styleguide/pyguide.html", tmpdir
            )
            files = list(Path(tmpdir).glob("*.md"))
            assert len(files) > 1
            assert (Path(tmpdir) / "index.md").exists()
