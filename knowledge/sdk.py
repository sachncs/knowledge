"""Public SDK — creates, updates, and removes OKF bundles from URLs or file paths.

Architecture
------------
The :class:`Knowledge` class is the single public entry point for
callers.  It follows a simple two-step pipeline::

    read_source()   →   LLM extraction / serialization
    (URL or file)       (delegated to sub-packages)

``read_source`` dispatches based on the *source* string:

* ``http://`` or ``https://`` → :func:`fetch_url` (with retries and
  size limits).
* Everything else → local file read (``OSError`` → ``FetchError``).

The extracted content is then handed to ``knowledge.llm`` for LLM-based
concept extraction and ``knowledge.kmd`` for OKF v0.1 bundle
serialization.
"""

from __future__ import annotations

import os
import time
import urllib.error
from urllib.parse import urlparse
from urllib.request import Request, urlopen

from knowledge.exceptions import FetchError
from knowledge.llm.extractor import LLMExtractor
from knowledge.llm.manager import KnowledgeBundleManager
from knowledge.models import KnowledgeGraph
from knowledge.version import DEFAULT_MODEL

USER_AGENT = "knowledge-sdk/0.1.0"
REQUEST_TIMEOUT = 30
MAX_RETRIES = 3
RETRY_DELAY = 1.0
MAX_BODY_SIZE = 50 * 1024 * 1024


class Knowledge:
    """Entry point for creating, updating, and removing OKF bundles.

    All public methods delegate to sub-packages:

    * :mod:`knowledge.llm` — LLM-based concept extraction.
    * :mod:`knowledge.kmd` — OKF v0.1 bundle serialization.

    **Example**

    .. code-block:: python

        from knowledge import Knowledge

        k = Knowledge()

        # Return an in-memory knowledge graph
        graph = k.create("https://example.com/doc.html")

        # Write an OKF v0.1 bundle to disk
        k.create_bundle("https://example.com/doc.html", "./my-bundle")

        # Re-extract from source and overwrite the bundle
        k.update("https://example.com/doc.html", "./my-bundle")

        # Remove specific concepts from a bundle
        k.remove(["obsolete-section"], "./my-bundle")
    """

    def __init__(
        self,
        model: str = DEFAULT_MODEL,
        path_map: dict[str, str] | None = None,
    ) -> None:
        """Initialize the SDK client.

        Args:
            model: The litellm-compatible model identifier
                (e.g. ``"gpt-4o"``, ``"claude-3-opus-20240229"``,
                ``"ollama/llama3"``).  Defaults to ``"gpt-4o"``.
            path_map: Optional mapping of tag → subdirectory path.
                Passed through to the :class:`~knowledge.kmd.bundle.BundleSerializer`.
        """
        self.model = model
        self.path_map = path_map

    def create(self, source: str) -> KnowledgeGraph:
        """Fetch or read *source* and return a ``KnowledgeGraph`` via LLM extraction.

        Args:
            source: URL (``http``/``https``) or local file path.

        Returns:
            A :class:`~knowledge.models.KnowledgeGraph` with one
            :class:`~knowledge.models.Concept` per section.

        Raises:
            FetchError: If the source cannot be fetched or read.
        """
        raw = self.read_source(source)
        return LLMExtractor(model=self.model).extract(raw)

    def create_bundle(
        self,
        source: str,
        output_dir: str,
        path_map: dict[str, str] | None = None,
    ) -> int:
        """Create an OKF v0.1 bundle from *source* and write to *output_dir*.

        The bundle consists of an ``index.md``, per-concept ``.md`` files
        with YAML frontmatter, and optional subdirectory groupings when
        a :attr:`~knowledge.kmd.bundle.BundleSerializer.path_map` is
        configured.

        Args:
            source: URL or file path.
            output_dir: Output directory for the bundle (created if it
                does not exist).
            path_map: Optional mapping of tag → subdirectory path.
                Overrides the instance-level path_map if provided.

        Returns:
            Number of concept files written.
        """
        raw = self.read_source(source)
        pm = path_map if path_map is not None else self.path_map
        manager = KnowledgeBundleManager(model=self.model, path_map=pm)
        return manager.create(raw, output_dir)

    def update(
        self,
        source: str,
        bundle_dir: str,
        path_map: dict[str, str] | None = None,
    ) -> int:
        """Re-extract concepts from *source* and overwrite an existing bundle.

        .. note::

            This performs a **complete replacement** — the bundle is
            regenerated from scratch.  There is no incremental diff or
            merge.  Any concepts present in the old bundle but not in
            the new extraction will be removed.

        Args:
            source: URL or file path.
            bundle_dir: Existing bundle directory to overwrite.
            path_map: Optional mapping of tag → subdirectory path.
                Overrides the instance-level path_map if provided.

        Returns:
            Number of concept files written.
        """
        raw = self.read_source(source)
        pm = path_map if path_map is not None else self.path_map
        manager = KnowledgeBundleManager(model=self.model, path_map=pm)
        return manager.update(raw, bundle_dir)

    def remove(
        self,
        concept_ids: list[str],
        bundle_dir: str,
        path_map: dict[str, str] | None = None,
    ) -> int:
        """Remove specific concepts from an existing bundle by ID.

        The bundle is read from disk, the specified concept IDs are
        removed from the in-memory graph, and the result is written
        back to the same directory.  Unknown IDs are logged as
        warnings and counted in :meth:`remove_with_unknowns`'s return
        value.

        Args:
            concept_ids: One or more concept IDs to remove.
            bundle_dir: Bundle directory to modify.
            path_map: Optional mapping of tag → subdirectory path.
                Overrides the instance-level path_map if provided.

        Returns:
            Number of concept files written after removal.
        """
        pm = path_map if path_map is not None else self.path_map
        manager = KnowledgeBundleManager(model=self.model, path_map=pm)
        written, _unknowns = manager.remove_with_unknowns(concept_ids, bundle_dir)
        return written

    def remove_with_unknowns(
        self,
        concept_ids: list[str],
        bundle_dir: str,
        path_map: dict[str, str] | None = None,
    ) -> tuple[int, list[str]]:
        """Remove concepts and return both the write count and unknown IDs.

        Use this method when callers need to detect typos.  Unknown IDs
        are returned in input order and are not raised as errors.

        Args:
            concept_ids: One or more concept IDs to remove.
            bundle_dir: Bundle directory to modify.
            path_map: Optional mapping of tag → subdirectory path.
                Overrides the instance-level path_map if provided.

        Returns:
            A tuple ``(written_count, unknown_ids)``.
        """
        pm = path_map if path_map is not None else self.path_map
        manager = KnowledgeBundleManager(model=self.model, path_map=pm)
        return manager.remove_with_unknowns(concept_ids, bundle_dir)

    @staticmethod
    def read_source(source: str) -> str:
        """Read *source* as a string, dispatching on scheme.

        ``http://`` and ``https://`` sources are fetched via
        :func:`fetch_url` (with retries and size limits).  All other
        values are treated as local file paths.

        .. caution::

            Only ``http``/``https`` schemes are recognised as URLs.
            ``ftp://``, ``file://``, etc. will be treated as file
            paths and likely fail with ``FetchError``.

        Args:
            source: URL or file path.

        Returns:
            The source content as a string.

        Raises:
            FetchError: If the URL cannot be fetched or the file does
                not exist / cannot be read.
        """
        scheme = urlparse(source).scheme
        if scheme in ("http", "https"):
            return fetch_url(source)
        if not os.path.isfile(source):
            raise FetchError(f"File not found: {source}")
        with open(source, encoding="utf-8") as f:
            return f.read()


def fetch_url(url: str) -> str:
    """Fetch *url* with retries, timeout, and user-agent header.

    **Retry algorithm**

    Up to :obj:`MAX_RETRIES` attempts with exponential backoff::

        delay = RETRY_DELAY * 2 ** attempt   # 1s, 2s, 4s

    * Network errors (``URLError``, ``OSError``, ``ConnectionError``,
      ``TimeoutError``) → retry.
    * HTTP 429 (rate limit) → retry (transient).
    * Other HTTP 4xx errors → **no retry** (client error, likely
      permanent).
    * HTTP 5xx errors → retry (server may recover).

    **Size limits**

    Responses are rejected (without reading the full body) if:

    1. The ``Content-Length`` header exceeds :obj:`MAX_BODY_SIZE` (50 MiB).
    2. The actual bytes read exceed :obj:`MAX_BODY_SIZE`.

    An extra 1 KiB is read beyond the limit to reliably detect
    oversized responses.

    Args:
        url: The URL to fetch.  Only ``http``/``https`` are supported.

    Returns:
        The response body decoded as a string.  Character encoding is
        determined from the ``Content-Type`` header (default ``utf-8``).
        Invalid byte sequences are replaced with the Unicode replacement
        character (``errors="replace"``).

    Raises:
        FetchError: If all retries are exhausted or the response is too
            large.
    """
    last_error: Exception | None = None

    for attempt in range(MAX_RETRIES):
        try:
            req = Request(url, headers={"User-Agent": USER_AGENT})
            with urlopen(req, timeout=REQUEST_TIMEOUT) as resp:
                # --- Check Content-Length header (trusted) ----------------
                content_length = resp.headers.get("Content-Length")
                if content_length is not None:
                    try:
                        cl = int(content_length)
                    except (ValueError, TypeError):
                        # Malformed header — ignore and read up to the
                        # actual limit instead.
                        pass
                    else:
                        if cl > MAX_BODY_SIZE:
                            raise FetchError(
                                f"Response too large: {cl} bytes (max {MAX_BODY_SIZE} bytes)"
                            )

                # --- Read body (bounded) ----------------------------------
                raw: bytes = resp.read(MAX_BODY_SIZE + 1024)

                if len(raw) > MAX_BODY_SIZE:
                    raise FetchError(
                        f"Response too large: {len(raw)} bytes (max {MAX_BODY_SIZE} bytes)"
                    )

                # --- Decode with detected charset -------------------------
                content_type = resp.headers.get("Content-Type", "")
                charset = "utf-8"
                if "charset=" in content_type:
                    charset = content_type.split("charset=")[-1].split(";")[0].strip().strip("\"'")
                return raw.decode(charset, errors="replace")

        except urllib.error.HTTPError as e:
            last_error = FetchError(f"HTTP {e.code}: {e.reason} for {url}")
            # Retry 429 (transient rate limit) but bail on other 4xx
            # (client errors — 401, 403, 404, etc. — are permanent).
            if 400 <= e.code < 500 and e.code not in (429,):
                break

        except (urllib.error.URLError, OSError, ConnectionError, TimeoutError) as e:
            last_error = FetchError(f"Connection failed: {e}")

        if attempt < MAX_RETRIES - 1:
            delay = RETRY_DELAY * (2**attempt)
            time.sleep(delay)

    raise (FetchError(str(last_error)) if last_error else FetchError(f"Failed to fetch {url}"))
