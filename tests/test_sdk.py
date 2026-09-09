"""Tests for the SDK — Knowledge class, KnowledgeGraph, fetch_url, parse_concept_file."""

import os
import tempfile
from unittest.mock import MagicMock, patch

import pytest
from pydantic import ValidationError as PydanticValidationError

from knowledge import Knowledge
from knowledge.exceptions import FetchError
from knowledge.llm.manager import parse_concept_file
from knowledge.models import Concept, KnowledgeGraph
from knowledge.sdk import fetch_url

# ---------------------------------------------------------------------------
# KnowledgeGraph model tests
# ---------------------------------------------------------------------------


class TestKnowledgeGraph:
    def test_empty_graph(self) -> None:
        g = KnowledgeGraph()
        assert g.concepts == {}

    def test_add_concept(self) -> None:
        c = Concept(id="foo", name="Foo")
        g = KnowledgeGraph().add_concept(c)
        assert "foo" in g.concepts
        assert g.concepts["foo"].name == "Foo"

    def test_add_concept_immutable(self) -> None:
        c1 = Concept(id="foo", name="Foo")
        g1 = KnowledgeGraph().add_concept(c1)
        g2 = g1.add_concept(Concept(id="bar", name="Bar"))
        assert "foo" in g1.concepts
        assert "bar" not in g1.concepts
        assert "bar" in g2.concepts

    def test_add_concept_replaces_existing(self) -> None:
        c1 = Concept(id="foo", name="Foo v1")
        c2 = Concept(id="foo", name="Foo v2")
        g = KnowledgeGraph().add_concept(c1).add_concept(c2)
        assert g.concepts["foo"].name == "Foo v2"

    def test_remove_concept(self) -> None:
        g = (
            KnowledgeGraph()
            .add_concept(Concept(id="foo", name="Foo"))
            .add_concept(Concept(id="bar", name="Bar"))
        )
        g2 = g.remove_concept("foo")
        assert "foo" not in g2.concepts
        assert "bar" in g2.concepts

    def test_remove_concept_nonexistent(self) -> None:
        g = KnowledgeGraph().add_concept(Concept(id="foo", name="Foo"))
        g2 = g.remove_concept("nonexistent")
        assert g2.concepts == g.concepts

    def test_frozen(self) -> None:
        g = KnowledgeGraph()
        with pytest.raises((TypeError, PydanticValidationError)):
            g.concepts = {}  # type: ignore[misc]

    def test_concept_slug_validation(self) -> None:
        Concept(id="valid-slug", name="OK")
        with pytest.raises(PydanticValidationError):
            Concept(id="InvalidID", name="Bad")
        with pytest.raises(PydanticValidationError):
            Concept(id="has spaces", name="Bad")
        with pytest.raises(PydanticValidationError):
            Concept(id="", name="Bad")


# ---------------------------------------------------------------------------
# parse_concept_file tests
# ---------------------------------------------------------------------------


class TestParseConceptFile:
    def test_valid_file(self) -> None:
        content = (
            '---\nid: test-concept\ntitle: "Test Concept"\n'
            'type: concept\ntags: ["guide", "intro"]\n'
            "\n---\n\n# Test Concept\n\nDescription here.\n"
        )
        with tempfile.TemporaryDirectory() as tmpdir:
            path = os.path.join(tmpdir, "test-concept.md")
            with open(path, "w") as f:
                f.write(content)
            concept = parse_concept_file(path)
            assert concept is not None
            assert concept.id == "test-concept"
            assert concept.name == "Test Concept"
            assert concept.description == "Description here."
            assert concept.tags == ["guide", "intro"]

    def test_file_no_frontmatter(self) -> None:
        content = "# Just a heading\n\nSome content.\n"
        with tempfile.TemporaryDirectory() as tmpdir:
            path = os.path.join(tmpdir, "no-fm.md")
            with open(path, "w") as f:
                f.write(content)
            assert parse_concept_file(path) is None

    def test_file_missing_id(self) -> None:
        content = '---\ntitle: "No ID"\ntype: concept\n\n---\n\nBody.\n'
        with tempfile.TemporaryDirectory() as tmpdir:
            path = os.path.join(tmpdir, "no-id.md")
            with open(path, "w") as f:
                f.write(content)
            assert parse_concept_file(path) is None

    def test_file_missing_title(self) -> None:
        content = "---\nid: no-title\ntype: concept\n\n---\n\nBody.\n"
        with tempfile.TemporaryDirectory() as tmpdir:
            path = os.path.join(tmpdir, "no-title.md")
            with open(path, "w") as f:
                f.write(content)
            assert parse_concept_file(path) is None

    def test_file_empty_body(self) -> None:
        content = '---\nid: empty-body\ntitle: "Empty"\ntype: concept\n\n---\n'
        with tempfile.TemporaryDirectory() as tmpdir:
            path = os.path.join(tmpdir, "empty-body.md")
            with open(path, "w") as f:
                f.write(content)
            concept = parse_concept_file(path)
            assert concept is not None
            assert concept.description is None

    def test_file_unreadable(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            path = os.path.join(tmpdir, "nonexistent.md")
            assert parse_concept_file(path) is None

    def test_no_tags(self) -> None:
        content = '---\nid: no-tags\ntitle: "No Tags"\ntype: concept\n\n---\n\nBody.\n'
        with tempfile.TemporaryDirectory() as tmpdir:
            path = os.path.join(tmpdir, "no-tags.md")
            with open(path, "w") as f:
                f.write(content)
            concept = parse_concept_file(path)
            assert concept is not None
            assert concept.tags == []


# ---------------------------------------------------------------------------
# fetch_url tests
# ---------------------------------------------------------------------------


class TestFetchUrl:
    @patch("knowledge.sdk.urlopen")
    def test_successful_fetch(self, mock_urlopen: MagicMock) -> None:
        mock_resp = MagicMock()
        mock_resp.read.return_value = b"hello world"
        mock_resp.headers = {"Content-Type": "text/plain"}
        mock_urlopen.return_value.__enter__.return_value = mock_resp

        result = fetch_url("https://example.com")
        assert result == "hello world"

    @patch("knowledge.sdk.urlopen")
    def test_fetch_with_charset(self, mock_urlopen: MagicMock) -> None:
        mock_resp = MagicMock()
        mock_resp.read.return_value = "café".encode("latin-1")
        mock_resp.headers = {"Content-Type": "text/html; charset=latin-1"}
        mock_urlopen.return_value.__enter__.return_value = mock_resp

        result = fetch_url("https://example.com")
        assert result == "café"

    @patch("knowledge.sdk.urlopen")
    def test_fetch_with_quoted_charset(self, mock_urlopen: MagicMock) -> None:
        mock_resp = MagicMock()
        mock_resp.read.return_value = b"hello"
        mock_resp.headers = {"Content-Type": 'text/html; charset="utf-8"'}
        mock_urlopen.return_value.__enter__.return_value = mock_resp

        result = fetch_url("https://example.com")
        assert result == "hello"

    @patch("knowledge.sdk.urlopen")
    def test_content_length_too_large(self, mock_urlopen: MagicMock) -> None:
        mock_resp = MagicMock()
        mock_resp.headers = {"Content-Length": "999999999"}
        mock_urlopen.return_value.__enter__.return_value = mock_resp

        with pytest.raises(FetchError, match="Response too large"):
            fetch_url("https://example.com")

    @patch("knowledge.sdk.urlopen")
    def test_content_length_malformed(self, mock_urlopen: MagicMock) -> None:
        """Malformed Content-Length should not crash."""
        mock_resp = MagicMock()
        mock_resp.read.return_value = b"small body"
        mock_resp.headers = {
            "Content-Length": "not-a-number",
            "Content-Type": "text/plain",
        }
        mock_urlopen.return_value.__enter__.return_value = mock_resp

        result = fetch_url("https://example.com")
        assert result == "small body"

    @patch("knowledge.sdk.urlopen")
    def test_response_too_large(self, mock_urlopen: MagicMock) -> None:
        mock_resp = MagicMock()
        from knowledge.sdk import MAX_BODY_SIZE

        mock_resp.read.return_value = b"x" * (MAX_BODY_SIZE + 1)
        mock_resp.headers = {"Content-Type": "text/plain"}
        mock_urlopen.return_value.__enter__.return_value = mock_resp

        with pytest.raises(FetchError, match="Response too large"):
            fetch_url("https://example.com")

    @patch("knowledge.sdk.urlopen")
    def test_retry_on_network_error(self, mock_urlopen: MagicMock) -> None:
        from urllib.error import URLError

        def _ctx_mock(body: bytes, content_type: str = "text/plain") -> MagicMock:
            resp = MagicMock()
            resp.read.return_value = body
            resp.headers = {"Content-Type": content_type}
            cm = MagicMock()
            cm.__enter__.return_value = resp
            return cm

        mock_urlopen.side_effect = [
            URLError("conn refused"),
            URLError("conn refused"),
            _ctx_mock(b"success"),
        ]

        result = fetch_url("https://example.com")
        assert result == "success"
        assert mock_urlopen.call_count == 3

    @patch("knowledge.sdk.urlopen")
    def test_retry_on_429(self, mock_urlopen: MagicMock) -> None:
        from http.client import HTTPMessage
        from urllib.error import HTTPError

        def _ctx_mock(body: bytes, content_type: str = "text/plain") -> MagicMock:
            resp = MagicMock()
            resp.read.return_value = body
            resp.headers = {"Content-Type": content_type}
            cm = MagicMock()
            cm.__enter__.return_value = resp
            return cm

        mock_urlopen.side_effect = [
            HTTPError(
                "https://example.com",
                429,
                "Too Many Requests",
                MagicMock(spec=HTTPMessage),
                None,
            ),
            _ctx_mock(b"success"),
        ]

        result = fetch_url("https://example.com")
        assert result == "success"

    @patch("knowledge.sdk.urlopen")
    def test_no_retry_on_404(self, mock_urlopen: MagicMock) -> None:
        from http.client import HTTPMessage
        from urllib.error import HTTPError

        mock_urlopen.side_effect = HTTPError(
            "https://example.com",
            404,
            "Not Found",
            MagicMock(spec=HTTPMessage),
            None,
        )

        with pytest.raises(FetchError, match="HTTP 404"):
            fetch_url("https://example.com")
        assert mock_urlopen.call_count == 1

    @patch("knowledge.sdk.urlopen")
    def test_all_retries_exhausted(self, mock_urlopen: MagicMock) -> None:
        from urllib.error import URLError

        mock_urlopen.side_effect = URLError("timeout")

        with pytest.raises(FetchError, match="Connection failed"):
            fetch_url("https://example.com")
        assert mock_urlopen.call_count == 3


# ---------------------------------------------------------------------------
# Knowledge class tests
# ---------------------------------------------------------------------------


def _sample_graph() -> KnowledgeGraph:
    c1 = Concept(id="intro", name="Introduction", description="Welcome.", tags=["guide"])
    c2 = Concept(id="usage", name="Usage", description="How to use it.", tags=["guide"])
    return KnowledgeGraph().add_concept(c1).add_concept(c2)


class TestKnowledge:
    def test_create(self) -> None:
        fake_html = "<html><body><h2>Intro</h2><p>Hi</p></body></html>"
        patches = [
            patch("knowledge.sdk.fetch_url", return_value=fake_html),
            patch(
                "knowledge.llm.extractor.LLMExtractor.extract",
                return_value=_sample_graph(),
            ),
        ]
        with patches[0], patches[1]:
            knowledge = Knowledge()
            graph = knowledge.create("https://example.com/doc.html")
            assert isinstance(graph, KnowledgeGraph)
            assert len(graph.concepts) == 2

    def test_create_bundle(self) -> None:
        fake_html = "<html><body><h2>Intro</h2><p>Hi</p></body></html>"
        patches = [
            patch("knowledge.sdk.fetch_url", return_value=fake_html),
            patch("knowledge.llm.manager.KnowledgeBundleManager.create", return_value=2),
        ]
        with patches[0], patches[1]:
            knowledge = Knowledge()
            count = knowledge.create_bundle("https://example.com/doc.html", "/tmp/out")
            assert count == 2

    def test_update(self) -> None:
        fake_html = "<html><body><h2>Intro</h2><p>Hi</p></body></html>"
        patches = [
            patch("knowledge.sdk.fetch_url", return_value=fake_html),
            patch("knowledge.llm.manager.KnowledgeBundleManager.update", return_value=3),
        ]
        with patches[0], patches[1]:
            knowledge = Knowledge()
            count = knowledge.update("https://example.com/doc.html", "/tmp/bundle")
            assert count == 3

    def test_remove(self) -> None:
        with patch(
            "knowledge.llm.manager.KnowledgeBundleManager.remove_with_unknowns",
            return_value=(1, []),
        ):
            knowledge = Knowledge()
            count = knowledge.remove(["intro"], "/tmp/bundle")
            assert count == 1

    def test_remove_with_unknowns(self) -> None:
        with patch(
            "knowledge.llm.manager.KnowledgeBundleManager.remove_with_unknowns",
            return_value=(2, ["missing-concept"]),
        ):
            knowledge = Knowledge()
            written, unknowns = knowledge.remove_with_unknowns(
                ["intro", "missing-concept"], "/tmp/bundle"
            )
            assert written == 2
            assert unknowns == ["missing-concept"]

    def test_read_source_url(self) -> None:
        with patch("knowledge.sdk.fetch_url", return_value="fake content"):
            result = Knowledge.read_source("https://example.com")
            assert result == "fake content"

    def test_read_source_file(self) -> None:
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".html", delete=False, encoding="utf-8"
        ) as f:
            f.write("<html></html>")
            path = f.name
        try:
            result = Knowledge.read_source(path)
            assert result == "<html></html>"
        finally:
            os.unlink(path)

    def test_read_source_file_not_found(self) -> None:
        with pytest.raises(FetchError, match="File not found"):
            Knowledge.read_source("/nonexistent/path.html")

    def test_create_bundle_integration(self) -> None:
        """Full round-trip with fake source and real filesystem."""
        fake_html = "<html><body><h2>Intro</h2><p>Hi</p></body></html>"
        with patch("knowledge.sdk.fetch_url", return_value=fake_html):
            with patch(
                "knowledge.llm.extractor.LLMExtractor.extract",
                return_value=_sample_graph(),
            ):
                with tempfile.TemporaryDirectory() as tmpdir:
                    knowledge = Knowledge()
                    count = knowledge.create_bundle("https://example.com/doc.html", tmpdir)
                    assert count == 2
                    assert os.path.isfile(os.path.join(tmpdir, "intro.md"))
                    assert os.path.isfile(os.path.join(tmpdir, "usage.md"))

    def test_import(self) -> None:
        assert Knowledge is not None
