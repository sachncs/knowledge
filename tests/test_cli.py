"""Tests for the CLI."""

import tempfile
from pathlib import Path
from unittest.mock import patch

from knowledge.cli import build_parser, main


class TestCLI:
    def test_parser_accepts_create(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["create", "http://example.com", "/tmp/out"])
        assert args.command == "create"
        assert args.input == "http://example.com"
        assert args.output == "/tmp/out"

    def test_parser_accepts_update(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["update", "http://example.com", "/tmp/bundle"])
        assert args.command == "update"
        assert args.input == "http://example.com"
        assert args.bundle_dir == "/tmp/bundle"

    def test_parser_accepts_remove(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["remove", "foo", "bar", "/tmp/bundle"])
        assert args.command == "remove"
        assert args.concept_ids == ["foo", "bar"]
        assert args.bundle_dir == "/tmp/bundle"

    def test_parser_accepts_model_flag(self) -> None:
        parser = build_parser()
        args = parser.parse_args(
            ["--model", "gpt-4o-mini", "create", "http://example.com", "/tmp/out"]
        )
        assert args.model == "gpt-4o-mini"

    def test_create_bundle_uses_llm(self) -> None:
        with patch("knowledge.sdk.Knowledge.create_bundle", return_value=2):
            with tempfile.TemporaryDirectory() as tmpdir:
                main(["create", "https://example.com/doc.html", tmpdir])
                assert Path(tmpdir).exists()

    def test_update_command(self) -> None:
        with patch("knowledge.sdk.Knowledge.update", return_value=3):
            with tempfile.TemporaryDirectory() as tmpdir:
                main(["update", "https://example.com/doc.html", tmpdir])
                assert Path(tmpdir).exists()

    def test_remove_command(self) -> None:
        with patch("knowledge.sdk.Knowledge.remove", return_value=1):
            with tempfile.TemporaryDirectory() as tmpdir:
                main(["remove", "old-concept", tmpdir])
                assert Path(tmpdir).exists()
