"""SDK — creates, updates, and removes OKF bundles from URLs or file paths."""

from __future__ import annotations

import os
import time
import urllib.error
from urllib.request import Request, urlopen

from knowledge.exceptions import FetchError
from knowledge.llm.extractor import LLMExtractor
from knowledge.llm.manager import KnowledgeBundleManager
from knowledge.models import KnowledgeGraph

USER_AGENT = "knowledge-sdk/0.1.0"
REQUEST_TIMEOUT = 30
MAX_RETRIES = 3
RETRY_DELAY = 1.0
MAX_BODY_SIZE = 50 * 1024 * 1024


class Knowledge:
    """Entry point for creating, updating, and removing OKF bundles."""

    def __init__(self, model: str = "gpt-4o") -> None:
        self.model = model

    def create(self, source: str) -> KnowledgeGraph:
        """Fetch or read source and return a KnowledgeGraph via LLM extraction.

        Args:
            source: URL (http/https) or file path.

        Returns:
            A KnowledgeGraph with one Concept per section.

        Raises:
            FetchError: If the source cannot be fetched or read.
        """
        raw = self._read_source(source)
        return LLMExtractor(model=self.model).extract(raw, source_url=source)

    def create_bundle(self, source: str, output_dir: str) -> int:
        """Create an OKF bundle from a source and write to a directory.

        Args:
            source: URL or file path.
            output_dir: Output directory for the bundle.

        Returns:
            Number of concept files written.
        """
        raw = self._read_source(source)
        manager = KnowledgeBundleManager(model=self.model)
        return manager.create(raw, output_dir, source_url=source)

    def update(self, source: str, bundle_dir: str) -> int:
        """Re-extract concepts from source and overwrite an existing bundle.

        Args:
            source: URL or file path.
            bundle_dir: Existing bundle directory to update.

        Returns:
            Number of concept files written.
        """
        raw = self._read_source(source)
        manager = KnowledgeBundleManager(model=self.model)
        return manager.update(raw, bundle_dir, source_url=source)

    def remove(self, concept_ids: list[str], bundle_dir: str) -> int:
        """Remove specific concepts from an existing bundle by ID.

        Args:
            concept_ids: One or more concept IDs to remove.
            bundle_dir: Bundle directory to modify.

        Returns:
            Number of concept files written.
        """
        manager = KnowledgeBundleManager(model=self.model)
        return manager.remove(concept_ids, bundle_dir)

    @staticmethod
    def _read_source(source: str) -> str:
        if source.startswith("http://") or source.startswith("https://"):
            return fetch_url(source)
        if not os.path.isfile(source):
            raise FetchError(f"File not found: {source}")
        with open(source, encoding="utf-8") as f:
            return f.read()


def fetch_url(url: str) -> str:
    """Fetch a URL with retries, timeout, and user-agent.

    Args:
        url: The URL to fetch.

    Returns:
        The response body as a string.

    Raises:
        FetchError: If all retries are exhausted or the response is too large.
    """
    last_error: Exception | None = None

    for attempt in range(MAX_RETRIES):
        try:
            req = Request(url, headers={"User-Agent": USER_AGENT})
            resp = urlopen(req, timeout=REQUEST_TIMEOUT)

            content_length = resp.headers.get("Content-Length")
            if content_length and int(content_length) > MAX_BODY_SIZE:
                resp.close()
                raise FetchError(
                    f"Response too large: {content_length} bytes "
                    f"(max {MAX_BODY_SIZE} bytes)"
                )

            raw: bytes = resp.read(MAX_BODY_SIZE + 1024)
            resp.close()

            if len(raw) > MAX_BODY_SIZE:
                raise FetchError(
                    f"Response too large: {len(raw)} bytes "
                    f"(max {MAX_BODY_SIZE} bytes)"
                )

            content_type = resp.headers.get("Content-Type", "")
            charset = "utf-8"
            if "charset=" in content_type:
                charset = content_type.split("charset=")[-1].split(";")[0].strip()
            return raw.decode(charset, errors="replace")

        except urllib.error.HTTPError as e:
            last_error = FetchError(f"HTTP {e.code}: {e.reason} for {url}")
            if 400 <= e.code < 500 and e.code not in (429,):
                break

        except (urllib.error.URLError, OSError, ConnectionError, TimeoutError) as e:
            last_error = FetchError(f"Connection failed: {e}")

        if attempt < MAX_RETRIES - 1:
            delay = RETRY_DELAY * (2**attempt)
            time.sleep(delay)

    raise FetchError(str(last_error)) if last_error else FetchError(f"Failed to fetch {url}")
