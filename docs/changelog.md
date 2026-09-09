# Changelog

All notable changes to `knowledge` are documented here. The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and the project adheres to [Semantic Versioning](https://semver.org/).

Dates are ISO 8601. Each entry references the short SHA of the originating commit.

## [Unreleased]

### Added

- `Knowledge.remove_with_unknowns()` and
  `KnowledgeBundleManager.remove_with_unknowns()` return the list of
  requested concept IDs that did not match a concept in the bundle, so
  callers can detect typos.
- LLM extractor now recognises HTML `<h1>` and `<h5>`–`<h6>` headings
  (previously only `<h2>`–`<h4>`), and Markdown `#` through `######`
  headings (previously only `##`).
- `strip_json_fence()` removes any prose that follows the closing
  Markdown fence (or follows raw JSON output), so a model that
  "explains" its answer no longer drops the concept silently.
- Symmetric litellm error handling in `LLMExtractor.extract_section`:
  the full `OpenAIError` hierarchy is caught and logged, so a failing
  section no longer aborts the rest of the extraction.
- `BundleSerializer` rejects `path_map` entries that are absolute,
  contain `..` segments, or contain empty segments, closing a path
  traversal attack surface.
- CLI exit code `2` is returned by `knowledge remove` when any requested
  concept ID is not found in the bundle. The CLI also prints a warning
  listing every missing ID.
- `mkdocstrings`-rendered [Python API](api.md) page generated
  automatically from source docstrings.
- MkDocs site redesign with a new information architecture, branded
  logo, social preview image, and developer-oriented quickstart,
  tutorials, and troubleshooting pages.

### Changed

- `knowledge remove` now honours the `--model` flag (it is accepted but
  ignored because removal does not invoke the LLM).
- `litellm` is now pinned to `>=1.99.0,<2.0.0` so a future major bump
  cannot silently change the LLM API surface.
- CHANGELOG no longer references `KnowledgeGraph.merge()` or
  `KnowledgeGraph.diff()` (those methods do not exist in the SDK).

### Fixed

- `yaml_escape` / `yaml_unescape` round-trip is now lossless for inputs
  containing a backslash followed by `n`, `r`, `t`, or `"`. The unescape
  order was rewritten so a literal backslash is collapsed before the
  escape sequences are expanded.
- `BundleSerializer.serialize` scopes stale `.md` removal to
  directories the serializer owns, so user-authored assets are never
  touched.

## [0.1.0] - 2026-07-05

Initial alpha release. LLM-powered OKF v0.1 bundle creation from
documentation sources, distributed as a Python SDK with a CLI.

### Added

#### Core SDK

- `Knowledge` SDK class with `create`, `create_bundle`, `update`, and
  `remove` lifecycle methods.
- `KnowledgeBundleManager` orchestrating extraction and bundle writing.
- Resilient URL fetcher with retries, exponential backoff, size limits
  (50 MiB), charset detection, and HTTP error classification.
- Concept ID slug validation enforcing `^[a-z][a-z0-9-]*$`.
- `DEFAULT_MODEL` constant in `knowledge.version`, used consistently
  across all modules.

#### Models

- Pydantic models `Concept` and `KnowledgeGraph` (frozen / immutable)
  with `KnowledgeGraph.add_concept()` and
  `KnowledgeGraph.remove_concept()`.
- Exception hierarchy in `knowledge.exceptions`.

#### LLM Extraction

- `LLMExtractor` with section-aware splitting for HTML (`<h2>`–`<h4>`)
  and Markdown (`##`) headings, routed through `litellm` to support
  OpenAI, Anthropic, Ollama, vLLM, NVIDIA NIM, and other providers.
- YAML frontmatter serialization with proper escaping and unescaping.

#### OKF v0.1 Bundle Serialization

- `BundleSerializer` for the OKF v0.1 directory format: `index.md` plus
  per-concept Markdown files, YAML frontmatter, and tag-based
  subdirectory grouping.
- Structural bundle validation: link resolution, orphan detection, and
  absolute URL skipping.

#### CLI

- `knowledge` console script with `create`, `update`, and `remove`
  subcommands and a `--model` flag for LLM selection.

#### Tooling

- Hatchling build backend with `py.typed` PEP 561 marker.
- `pytest` test suite (66+ tests) covering SDK, bundle, CLI, and import
  paths.
- `ruff` (lint + format), `mypy --strict` with the `pydantic` plugin,
  and `vulture` for dead-code detection.
- `cleanup.sh` for removing caches, build artifacts, and generated
  bundles.

#### CI

- GitHub Actions CI on `master` for Python 3.12 and 3.13: `ruff check`,
  `ruff format --check`, `mypy`, `pytest --cov`, and `python -m build`.
- Release workflow publishing to PyPI on `release: published` events.
- Dependabot configuration for pip and GitHub Actions.
- Issue templates (`bug_report.md`, `feature_request.md`) and a pull
  request template.

#### Documentation

- `README.md` with badges, features, configuration tables, quick-start
  examples, and tech stack.
- MkDocs Material site with `index`, `getting-started`, `architecture`,
  and `faq` pages.
- ADR-001 (KMD flat format, superseded) and ADR-002 (OKF v0.1 bundle
  format).
- `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md` (Contributor Covenant v2.1),
  and `SECURITY.md`.
- `BENCHMARK.md` covering large-graph scenarios and a Google Python
  Style Guide OKF bundle example.
- `ROADMAP.md` aligned with the bundle-only SDK direction.
- `.env.example` documenting `KNOWLEDGE_DEFAULT_MODEL`,
  `KNOWLEDGE_MAX_BODY_SIZE`, `KNOWLEDGE_REQUEST_TIMEOUT`,
  `KNOWLEDGE_MAX_RETRIES`, and provider keys.
- `.editorconfig` and `.gitattributes` for consistent editor and
  line-ending behaviour.

### Changed

- **Architecture** — the package was stripped to a bundle-only SDK;
  the KMD flat format, extraction pipeline, pass framework, verification
  engine, and normalization modules from the v0.1.0 design phase were
  removed before tagging.
- **API** — removed dead `source_url` parameter, dead
  `check_duplicates` helper, and the unused `ValidationError` exception
  class.
- **CLI** — replaced `print()` calls with structured `logging` and
  removed semi-private naming throughout.
- **Tooling** — removed the redundant `black` dependency, aligned
  formatter line-length to 100, and removed stale entries from
  `.gitignore`.
- **Documentation** — replaced `anomalyco/knowledge` and the
  `knowledge-sdk.dev` placeholder with the canonical
  `sachncs/knowledge` repository URL across all files.
- **License** — copyright year updated to 2026.

### Dependencies

- Runtime: `pydantic>=2.0`, `litellm>=1.91.0`.
- Dev: `pytest>=9.1.1`, `pytest-cov>=7.1.0`, `ruff>=0.15.20`,
  `mypy>=2.1.0`, `vulture>=2.7`.
- Docs: `mkdocs>=1.6.1`, `mkdocstrings[python]>=0.25.0`,
  `mkdocs-material>=9.5.0`.
- CI: `actions/setup-python` bumped from 5 to 6.

### Release

- Tagged `0.1.0-alpha`.
- Version constant `0.1.0` in `knowledge/version.py` and
  `pyproject.toml`.
- `User-Agent` header for HTTP requests set to `knowledge-sdk/0.1.0`.

[Unreleased]: https://github.com/sachncs/knowledge/compare/0.1.0...HEAD
[0.1.0]: https://github.com/sachncs/knowledge/releases/tag/0.1.0
