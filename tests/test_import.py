"""Basic import and API surface tests."""

import re

from knowledge import DEFAULT_MODEL, __version__


def test_version_is_string() -> None:
    assert isinstance(__version__, str)


def test_version_is_not_empty() -> None:
    assert len(__version__) > 0


def test_version_format() -> None:
    """Version must be a valid PEP 440 public version identifier."""
    assert re.match(r"^\d+\.\d+\.\d+", __version__)


def test_default_model() -> None:
    assert DEFAULT_MODEL == "gpt-4o"
