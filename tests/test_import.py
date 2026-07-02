"""Basic import and API surface tests."""

from knowledge import __version__


def test_version_is_string() -> None:
    assert isinstance(__version__, str)


def test_version_is_not_empty() -> None:
    assert len(__version__) > 0


def test_version_format() -> None:
    parts = __version__.split(".")
    assert len(parts) == 3
    for part in parts:
        assert part.isdigit()
