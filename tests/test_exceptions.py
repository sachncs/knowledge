"""Tests for exception types."""

from knowledge.exceptions import (
    KnowledgeError,
    ParseError,
    UnsupportedSourceError,
)


class TestExceptions:
    def test_knowledge_error(self) -> None:
        err = KnowledgeError("base error")
        assert str(err) == "base error"
        assert isinstance(err, Exception)

    def test_parse_error(self) -> None:
        err = ParseError("bad format")
        assert isinstance(err, KnowledgeError)

    def test_unsupported_source_error(self) -> None:
        err = UnsupportedSourceError("unsupported")
        assert isinstance(err, KnowledgeError)

    def test_all_subclass_knowledge_error(self) -> None:
        exceptions = [
            ParseError,
            UnsupportedSourceError,
        ]
        for exc in exceptions:
            assert issubclass(exc, KnowledgeError)
