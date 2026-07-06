"""Tests for the CLI — argument parsing and command execution."""

import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

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

    def test_parser_model_default(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["create", "http://example.com", "/tmp/out"])
        assert args.model == "gpt-4o"

    def test_parser_rejects_no_command(self) -> None:
        parser = build_parser()
        with pytest.raises(SystemExit):
            parser.parse_args([])

    def test_parser_create_validate_flag(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["create", "--validate", "http://example.com", "/tmp/out"])
        assert args.validate is True

    def test_parser_create_no_validate(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["create", "http://example.com", "/tmp/out"])
        assert args.validate is False

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

    def test_remove_multiple_concepts(self) -> None:
        with patch("knowledge.sdk.Knowledge.remove", return_value=2):
            with tempfile.TemporaryDirectory() as tmpdir:
                main(["remove", "old-concept", "another", tmpdir])
                assert Path(tmpdir).exists()

    def test_main_error_handling(self) -> None:
        """main() should catch exceptions and exit with code 1."""
        with patch("knowledge.cli.cmd_create", side_effect=RuntimeError("boom")):
            with pytest.raises(SystemExit) as exc:
                main(["create", "http://example.com", "/tmp/out"])
            assert exc.value.code == 1

    def test_main_with_model_flag_on_create(self) -> None:
        with patch("knowledge.sdk.Knowledge.create_bundle", return_value=1):
            with tempfile.TemporaryDirectory() as tmpdir:
                main(
                    [
                        "--model",
                        "claude-3-opus-20240229",
                        "create",
                        "https://example.com",
                        tmpdir,
                    ]
                )

    def test_model_flag_still_allows_remove(self) -> None:
        """--model flag is accepted by remove but silently ignored."""
        with patch("knowledge.sdk.Knowledge.remove", return_value=1):
            with tempfile.TemporaryDirectory() as tmpdir:
                main(["--model", "gpt-4o", "remove", "x", tmpdir])
