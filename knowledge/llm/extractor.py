"""LLM-based concept extraction from documents using litellm."""

from __future__ import annotations

import json
import re

import litellm

from knowledge.models import Concept, KnowledgeGraph


class LLMExtractor:
    """Extracts knowledge concepts from documents via an LLM.

    Splits the source by top-level headings, sends each section to the LLM,
    and assembles the results into a KnowledgeGraph.
    """

    EXTRACTION_PROMPT = """\
You are a knowledge extraction system. Given a section from a technical \
document, return a JSON object describing the concept.

Rules:
- Convert any HTML formatting to clean Markdown
- Preserve code blocks, inline code, links, lists, and emphasis faithfully
- The id must be a kebab-case slug (e.g. "installing-the-sdk")
- tags should be short categorization terms
- Return ONLY a JSON object. No markdown fences, no explanation.

Section heading: {heading}
Content:
{content}

Return exactly this JSON shape:
{{
    "id": "...",
    "name": "...",
    "description": "...",
    "tags": ["..."],
    "level": {level}
}}"""

    def __init__(self, model: str = "gpt-4o") -> None:
        self.model = model

    def extract(self, source_text: str, source_url: str = "") -> KnowledgeGraph:
        """Extract concepts from source text, returning a KnowledgeGraph."""
        graph = KnowledgeGraph()
        sections = self._split_sections(source_text)

        for heading, content, level in sections:
            concept = self._extract_section(heading, content, level)
            if concept is not None:
                graph = graph.add_concept(concept)

        return graph

    def _split_sections(
        self, text: str
    ) -> list[tuple[str, str, int]]:
        """Split text into (heading, content, level) tuples.

        Handles both HTML and Markdown sources. Falls back to treating
        the entire content as a single section.
        """
        sections = self._split_html_headings(text)
        if sections:
            return sections

        sections = self._split_markdown_headings(text)
        if sections:
            return sections

        return [("Document", text, 1)]

    @staticmethod
    def _split_html_headings(text: str) -> list[tuple[str, str, int]]:
        pattern = r"<h([2-4])(?:[^>]*)>(.*?)</h\1>"
        matches = list(re.finditer(pattern, text, re.IGNORECASE | re.DOTALL))
        if not matches:
            return []

        sections: list[tuple[str, str, int]] = []
        for i, m in enumerate(matches):
            level = int(m.group(1))
            heading = re.sub(r"<[^>]+>", "", m.group(2)).strip()
            content_start = m.end()
            content_end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
            content = text[content_start:content_end].strip()
            sections.append((heading, content, level))
        return sections

    @staticmethod
    def _split_markdown_headings(text: str) -> list[tuple[str, str, int]]:
        pattern = r"^## (.+)$"
        matches = list(re.finditer(pattern, text, re.MULTILINE))
        if not matches:
            return []

        sections: list[tuple[str, str, int]] = []
        for i, m in enumerate(matches):
            heading = m.group(1).strip()
            content_start = m.end()
            content_end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
            content = text[content_start:content_end].strip()
            sections.append((heading, content, 2))
        return sections

    def _extract_section(
        self, heading: str, content: str, level: int
    ) -> Concept | None:
        prompt = self.EXTRACTION_PROMPT.format(
            heading=heading, content=content, level=level
        )
        try:
            response = litellm.completion(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.0,
            )
            text = response.choices[0].message.content
            if text is None:
                return None
            data = self._parse_json(text)
            if data is None:
                return None
            return Concept(
                id=data.get("id", heading.lower().replace(" ", "-")),
                name=data.get("name", heading),
                description=data.get("description"),
                tags=data.get("tags", []),
            )
        except Exception:
            return None

    @staticmethod
    def _parse_json(text: str) -> dict[str, object] | None:
        text = text.strip()
        if text.startswith("```"):
            text = re.sub(r"^```(?:json)?\s*", "", text)
            text = re.sub(r"\s*```$", "", text)
        try:
            result = json.loads(text)
            assert isinstance(result, dict)
            return result
        except json.JSONDecodeError:
            return None
