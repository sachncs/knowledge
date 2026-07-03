"""Source readers for knowledge extraction.

Source readers acquire raw content from various input formats.
They never perform semantic analysis — only format-specific parsing
to produce a canonical SourceDocument.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field


@dataclass(frozen=True)
class SourceDocument:
    """Canonical representation of a source document.

    Contains the raw text content along with metadata about its origin.
    """

    content: str
    source: str
    metadata: dict[str, str] = field(default_factory=dict)


class TextSourceReader:
    """Reads plain text content into a SourceDocument."""

    def read(self, content: str, source: str = "text") -> SourceDocument:
        """Read plain text content into a SourceDocument.

        Args:
            content: The raw text content.
            source: Identifier for the source document.

        Returns:
            A SourceDocument with format metadata set to "text".
        """
        return SourceDocument(content=content, source=source, metadata={"format": "text"})


class MarkdownSourceReader:
    """Reads Markdown content, stripping formatting to produce plain text.

    Preserves structural information (headings) as metadata while
    removing Markdown syntax for downstream extraction.
    """

    # Regex to remove inline formatting
    LINK_PATTERN = re.compile(r"\[([^\]]+)\]\([^)]+\)")
    BOLD_PATTERN = re.compile(r"\*\*([^*]+)\*\*")
    ITALIC_PATTERN = re.compile(r"(?<!\*)\*([^*]+)\*(?!\*)")
    CODE_PATTERN = re.compile(r"`([^`]+)`")
    HEADING_PATTERN = re.compile(r"^#{1,6}\s+(.*)", re.MULTILINE)

    def read(self, content: str, source: str = "markdown") -> SourceDocument:
        """Read Markdown content, stripping formatting to produce plain text.

        Args:
            content: The raw Markdown content.
            source: Identifier for the source document.

        Returns:
            A SourceDocument with plain text content and heading metadata.
        """
        text = content
        text = self.LINK_PATTERN.sub(r"\1", text)
        text = self.BOLD_PATTERN.sub(r"\1", text)
        text = self.ITALIC_PATTERN.sub(r"\1", text)
        text = self.CODE_PATTERN.sub(r"\1", text)
        headings = self.HEADING_PATTERN.findall(content)

        return SourceDocument(
            content=text,
            source=source,
            metadata={
                "format": "markdown",
                "headings": ", ".join(h.strip() for h in headings),
            },
        )
