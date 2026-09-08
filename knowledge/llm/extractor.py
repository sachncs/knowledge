"""LLM-based concept extraction from documents using litellm.

The :class:`LLMExtractor` splits a source document into heading-delimited
sections (supporting both HTML and Markdown), sends each section to an LLM
with a structured prompt, and assembles the responses into a
:class:`~knowledge.models.KnowledgeGraph`.

Design decisions
----------------
* **Per-section extraction** — rather than sending the entire document
  in one LLM call, we split by headings.  This keeps each prompt within
  common context windows and avoids truncation of long documents.
* **Pydantic response parsing** — the LLM response is validated with
  :meth:`pydantic.BaseModel.model_validate_json`, providing type safety
  and clear error messages if the LLM produces malformed output.
* **Graceful degradation** — a failing LLM call for one section does not
  abort the entire extraction.  The section is logged at ``WARNING``
  level and skipped.
"""

from __future__ import annotations

import logging
import re
import string

import litellm
from litellm.exceptions import APIError as LLMAPIError
from pydantic import BaseModel, ValidationError

from knowledge.models import Concept, KnowledgeGraph
from knowledge.version import DEFAULT_MODEL

logger = logging.getLogger(__name__)


class LLMResponse(BaseModel):
    """Expected JSON shape from the LLM for a single section.

    The LLM is instructed (via the :attr:`LLMExtractor.EXTRACTION_PROMPT`)
    to return a JSON object matching this schema.  Using a Pydantic model
    here gives us free validation and structured access to the response.
    """

    id: str
    name: str
    description: str | None = None
    tags: list[str] = []
    level: int = 2


class LLMExtractor:
    """Extracts :class:`~knowledge.models.Concept` objects from document text via an LLM.

    Usage
    -----
    ::

        extractor = LLMExtractor()
        graph = extractor.extract(source_text)
        # graph is a KnowledgeGraph with one Concept per section

    The extractor splits the input by top-level headings, sends each
    section to the configured LLM, and assembles the results.
    """

    EXTRACTION_PROMPT = string.Template(
        """\
You are a knowledge extraction system. Given a section from a technical \
document, return a JSON object describing the concept.

Rules:
- Convert any HTML formatting to clean Markdown
- Preserve code blocks, inline code, links, lists, and emphasis faithfully
- The id must be a kebab-case slug (e.g. "installing-the-sdk")
- tags should be short categorization terms
- Return ONLY a JSON object. No markdown fences, no explanation.

Section heading: $heading
Content:
$content

Return exactly this JSON shape:
{
    "id": "...",
    "name": "...",
    "description": "...",
    "tags": ["..."],
    "level": $level
}"""
    )

    def __init__(self, model: str = DEFAULT_MODEL) -> None:
        """Initialise the extractor.

        Args:
            model: A litellm-compatible model identifier
                (e.g. ``"gpt-4o"``, ``"claude-3-opus-20240229"``,
                ``"ollama/llama3"``).  Defaults to ``"gpt-4o"``.
        """
        self.model = model

    def extract(self, source_text: str) -> KnowledgeGraph:
        """Extract concepts from *source_text* by splitting on headings.

        The method:

        1. Attempts to split by HTML ``<h2>-<h4>`` headings.
        2. Falls back to Markdown ``##`` headings.
        3. If neither is found, treats the entire text as a single
           section.
        4. Sends each section to the LLM and collects the results.

        Args:
            source_text: The raw document text (HTML or Markdown).

        Returns:
            A :class:`~knowledge.models.KnowledgeGraph` containing one
            :class:`~knowledge.models.Concept` per section.  Sections
            whose LLM call failed are silently omitted.
        """
        graph = KnowledgeGraph()
        sections = self.split_sections(source_text)

        for heading, content, level in sections:
            concept = self.extract_section(heading, content, level)
            if concept is not None:
                graph = graph.add_concept(concept)

        return graph

    def split_sections(self, text: str) -> list[tuple[str, str, int]]:
        """Split *text* into ``(heading, content, level)`` tuples.

        Heading detection tries two strategies in order:

        1. :meth:`split_html_headings` — looks for ``<h2>``, ``<h3>``,
           and ``<h4>`` tags.  HTML comments (``<!-- ... -->``) are
           stripped before matching to avoid false positives.
        2. :meth:`split_markdown_headings` — looks for ATX ``##``
           headings.

        If neither strategy finds headings, a single entry with heading
        ``"Document"`` and level ``1`` is returned.

        Returns:
            A list of ``(heading, body_text, level)`` tuples.  May be
            empty only if the input text is empty.
        """
        sections = self.split_html_headings(text)
        if sections:
            return sections

        sections = self.split_markdown_headings(text)
        if sections:
            return sections

        return [("Document", text, 1)]

    @staticmethod
    def split_html_headings(text: str) -> list[tuple[str, str, int]]:
        """Split *text* on ``<h2>``, ``<h3>``, ``<h4>`` tags.

        HTML comments (``<!-- ... -->``) are stripped before searching
        to avoid treating commented-out headings as real structure.

        Each heading's content (between the opening and closing tag) is
        cleaned of inner HTML tags to produce a plain-text heading
        string.  The body of a section runs from the closing tag of the
        current heading to the opening tag of the next (or end of text).

        Returns:
            An empty list if no HTML headings are found.
        """
        clean = re.sub(r"<!--.*?-->", "", text, flags=re.DOTALL)
        pattern = r"<h([2-4])(?:[^>]*)>(.*?)</h\1>"
        matches = list(re.finditer(pattern, clean, re.IGNORECASE | re.DOTALL))
        if not matches:
            return []

        sections: list[tuple[str, str, int]] = []
        for i, m in enumerate(matches):
            level = int(m.group(1))
            heading = re.sub(r"<[^>]+>", "", m.group(2)).strip()
            content_start = m.end()
            content_end = matches[i + 1].start() if i + 1 < len(matches) else len(clean)
            content = clean[content_start:content_end].strip()
            sections.append((heading, content, level))
        return sections

    @staticmethod
    def split_markdown_headings(text: str) -> list[tuple[str, str, int]]:
        """Split *text* on ATX ``##`` headings.

        Trailing ``#`` characters on the heading line are stripped
        (e.g. ``## Installation ##`` → ``"Installation"``).

        All headings are assigned a level of 2.  The body of a section
        runs from the line after the heading to the next ``##`` heading
        (or end of text).

        Returns:
            An empty list if no Markdown headings are found.
        """
        pattern = r"^## (.+)$"
        matches = list(re.finditer(pattern, text, re.MULTILINE))
        if not matches:
            return []

        sections: list[tuple[str, str, int]] = []
        for i, m in enumerate(matches):
            heading = re.sub(r"\s+#+\s*$", "", m.group(1)).strip()
            content_start = m.end()
            content_end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
            content = text[content_start:content_end].strip()
            sections.append((heading, content, 2))
        return sections

    def extract_section(self, heading: str, content: str, level: int) -> Concept | None:
        """Send a single section to the LLM and parse the response.

        The LLM response is expected to be valid JSON matching the
        :class:`LLMResponse` schema.  The response is parsed with
        :meth:`pydantic.BaseModel.model_validate_json`.

        Args:
            heading: The section heading text.
            content: The section body text (after the heading).
            level: The heading level (2-4).

        Returns:
            A :class:`~knowledge.models.Concept` instance, or ``None``
            if the LLM call fails or returns unparseable output.
        """
        prompt = self.EXTRACTION_PROMPT.safe_substitute(
            heading=heading, content=content, level=level
        )
        try:
            response = litellm.completion(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.0,
            )
        except LLMAPIError:
            logger.warning("LLM API error for section '%s'", heading, exc_info=True)
            return None

        text = response.choices[0].message.content
        if text is None:
            return None

        cleaned = strip_json_fence(text)
        try:
            parsed = LLMResponse.model_validate_json(cleaned)
        except (ValidationError, ValueError):
            logger.warning("Invalid LLM response for section '%s'", heading)
            return None

        return Concept(
            id=parsed.id,
            name=parsed.name,
            description=parsed.description,
            tags=parsed.tags,
        )


def strip_json_fence(text: str) -> str:
    """Strip a Markdown code fence (`` ```json ... ``` ``) from *text*.

    Many LLMs wrap JSON output in Markdown fences even when instructed
    not to.  This function removes leading and trailing fences, handling
    the optional ``json`` language tag case-insensitively.

    Args:
        text: The raw LLM output.

    Returns:
        The text with outer code fences removed, if present.
    """
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text, flags=re.IGNORECASE)
        text = re.sub(r"\s*```$", "", text)
    return text.strip()
