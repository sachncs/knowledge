"""Tests for the LLM extractor — strip_json_fence and LLMExtractor."""

from unittest.mock import MagicMock, patch

import pytest
from litellm.exceptions import APIError as LLMAPIError
from litellm.exceptions import BadRequestError

from knowledge.llm.extractor import LLMExtractor, strip_json_fence
from knowledge.models import Concept


class TestStripJsonFence:
    @pytest.mark.parametrize(
        ("raw", "expected"),
        [
            ('```json\n{"id": "test", "name": "Test"}\n```', '{"id": "test", "name": "Test"}'),
            ('```JSON\n{"id": "test", "name": "Test"}\n```', '{"id": "test", "name": "Test"}'),
            ('```Json\n{"id": "test", "name": "Test"}\n```', '{"id": "test", "name": "Test"}'),
            ('```jSoN\n{"id": "test", "name": "Test"}\n```', '{"id": "test", "name": "Test"}'),
            ('```\n{"id": "test", "name": "Test"}\n```', '{"id": "test", "name": "Test"}'),
            ('{"id": "test", "name": "Test"}', '{"id": "test", "name": "Test"}'),
            ('  ```json\n{"x": 1}\n```  ', '{"x": 1}'),
            # Trailing prose after the closing fence is removed (issue #45)
            (
                '```json\n{"id": "x", "name": "X"}\n```\nThis is some explanation.',
                '{"id": "x", "name": "X"}',
            ),
            # Trailing prose after raw JSON is also stripped
            (
                '{"id": "x", "name": "X"}\nExplanation follows here.',
                '{"id": "x", "name": "X"}',
            ),
        ],
    )
    def test_strip_json_fence_casing(self, raw: str, expected: str) -> None:
        """Strip fences regardless of json tag casing and trim trailing prose."""
        assert strip_json_fence(raw) == expected

    def test_strip_json_fence_no_fence(self) -> None:
        """Non-fenced text is returned unchanged after strip."""
        assert strip_json_fence('{"key": "value"}') == '{"key": "value"}'


class TestHeadingSplitting:
    def test_html_supports_all_levels(self) -> None:
        """HTML headings of any level are recognised (issue #42)."""
        html = (
            "<h1>One</h1><p>a</p>"
            "<h2>Two</h2><p>b</p>"
            "<h3>Three</h3><p>c</p>"
            "<h4>Four</h4><p>d</p>"
            "<h5>Five</h5><p>e</p>"
            "<h6>Six</h6><p>f</p>"
        )
        sections = LLMExtractor.split_html_headings(html)
        assert [s[2] for s in sections] == [1, 2, 3, 4, 5, 6]
        assert [s[0] for s in sections] == ["One", "Two", "Three", "Four", "Five", "Six"]

    def test_markdown_supports_all_levels(self) -> None:
        """Markdown headings of any level are recognised (issue #41)."""
        md = (
            "# One\n\na\n"
            "## Two\n\nb\n"
            "### Three\n\nc\n"
            "#### Four\n\nd\n"
            "##### Five\n\ne\n"
            "###### Six\n\nf\n"
        )
        sections = LLMExtractor.split_markdown_headings(md)
        assert [s[2] for s in sections] == [1, 2, 3, 4, 5, 6]
        assert [s[0] for s in sections] == ["One", "Two", "Three", "Four", "Five", "Six"]

    def test_markdown_strips_trailing_hashes(self) -> None:
        md = "## Installation ##\n\nbody\n"
        sections = LLMExtractor.split_markdown_headings(md)
        assert sections[0][0] == "Installation"

    def test_html_strips_html_comments(self) -> None:
        html = "<!-- <h2>fake</h2> --><h2>Real</h2><p>body</p>"
        sections = LLMExtractor.split_html_headings(html)
        assert [s[0] for s in sections] == ["Real"]

    def test_html_handles_inline_markup_in_heading(self) -> None:
        html = "<h2>Some <em>rich</em> heading</h2><p>body</p>"
        sections = LLMExtractor.split_html_headings(html)
        assert sections[0][0] == "Some rich heading"

    def test_html_returns_empty_when_no_headings(self) -> None:
        assert LLMExtractor.split_html_headings("<p>no headings here</p>") == []

    def test_markdown_returns_empty_when_no_headings(self) -> None:
        assert LLMExtractor.split_markdown_headings("just some text\n") == []

    def test_split_sections_falls_back_to_markdown(self) -> None:
        sections = LLMExtractor().split_sections("## Hello\n\nbody")
        assert sections[0][0] == "Hello"

    def test_split_sections_falls_back_to_document(self) -> None:
        sections = LLMExtractor().split_sections("just plain text with no headings")
        assert sections == [("Document", "just plain text with no headings", 1)]

    def test_split_sections_prefers_html(self) -> None:
        """When both HTML and Markdown headings are present, HTML wins."""
        text = "<h2>HTML Heading</h2><p>body</p>## MD Heading\n\nmore"
        sections = LLMExtractor().split_sections(text)
        assert [s[0] for s in sections] == ["HTML Heading"]


class TestLLMExtractor:
    @patch("litellm.completion")
    def test_extract_section_uppercase_fence(self, mock_completion: MagicMock) -> None:
        """Uppercase JSON code fence is parsed into Concept without errors."""
        mock_response = MagicMock()
        mock_response.choices = [
            MagicMock(
                message=MagicMock(
                    content=(
                        '```JSON\n{"id": "sample-concept", "name": "Sample", '
                        '"description": "Desc", "tags": ["tag1"]}\n```'
                    )
                )
            )
        ]
        mock_completion.return_value = mock_response

        extractor = LLMExtractor()
        concept = extractor.extract_section("Heading", "Content", 2)
        assert concept is not None
        assert isinstance(concept, Concept)
        assert concept.id == "sample-concept"
        assert concept.name == "Sample"
        assert concept.description == "Desc"
        assert concept.tags == ["tag1"]

    @patch("litellm.completion")
    def test_extract_section_swallows_litellm_api_error(self, mock_completion: MagicMock) -> None:
        """A normalized APIError must not abort extraction (issue #43)."""
        mock_completion.side_effect = LLMAPIError(
            status_code=500,
            message="upstream failure",
            llm_provider="openai",
            model="gpt-4o",
        )
        assert LLMExtractor().extract_section("Heading", "Content", 2) is None

    @patch("litellm.completion")
    def test_extract_section_swallows_litellm_bad_request(self, mock_completion: MagicMock) -> None:
        """A BadRequestError must not abort extraction (issue #43)."""
        mock_completion.side_effect = BadRequestError(
            message="bad params", llm_provider="openai", model="gpt-4o"
        )
        assert LLMExtractor().extract_section("Heading", "Content", 2) is None

    @patch("litellm.completion")
    def test_extract_section_returns_none_on_trailing_prose(
        self, mock_completion: MagicMock
    ) -> None:
        """Trailing prose after the closing fence is stripped (issue #45)."""
        mock_response = MagicMock()
        mock_response.choices = [
            MagicMock(
                message=MagicMock(
                    content=(
                        '```json\n{"id": "ok", "name": "OK", '
                        '"description": "d", "tags": []}\n```\nFollowed by prose.'
                    )
                )
            )
        ]
        mock_completion.return_value = mock_response

        concept = LLMExtractor().extract_section("Heading", "Content", 2)
        assert concept is not None
        assert concept.id == "ok"
