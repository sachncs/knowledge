"""Tests for the LLM extractor — strip_json_fence and LLMExtractor."""

from unittest.mock import MagicMock, patch

import pytest

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
        ],
    )
    def test_strip_json_fence_casing(self, raw: str, expected: str) -> None:
        """Strip fences regardless of json tag casing."""
        assert strip_json_fence(raw) == expected

    def test_strip_json_fence_no_fence(self) -> None:
        """Non-fenced text is returned unchanged after strip."""
        assert strip_json_fence('{"key": "value"}') == '{"key": "value"}'


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
