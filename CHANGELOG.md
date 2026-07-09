# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

Dates are ISO 8601. Each entry references the short SHA of the originating
commit (merge commits and dependabot PRs are footnoted rather than
duplicated as features).

## [Unreleased]

## [0.1.0] - 2026-07-05

Initial alpha release. LLM-powered OKF v0.1 bundle creation from
documentation sources, distributed as a Python SDK with a CLI.

### Added

#### Core SDK
- `Knowledge` SDK class with `create`, `create_bundle`, `update`, and
  `remove` lifecycle methods (`f3baa2b`, `0089194`).
- `KnowledgeBundleManager` orchestrating extraction and bundle writing
  (`f3baa2b`).
- Resilient URL fetcher with retries, exponential backoff, size limits
  (50 MiB), charset detection, and HTTP error classification (`f3baa2b`,
  `d04295c`).
- Concept ID slug validation enforcing `^[a-z][a-z0-9-]*$` (`ca9d3a9`).
- `DEFAULT_MODEL` constant in `knowledge.version` and used consistently
  across all modules (`68de5ef`, `d537a03`).

#### Models
- Pydantic models `Concept` and `KnowledgeGraph` (frozen/immutable) with
  `KnowledgeGraph.merge()` and `KnowledgeGraph.diff()` (`190f43c`,
  `fe17398`, `ec03862`).
- Exception hierarchy in `knowledge.exceptions` (`f1d2072`,
  `4a385a9`).

#### LLM Extraction
- `LLMExtractor` with section-aware splitting for HTML (`<h2>`–`<h4>`)
  and Markdown (`##`) headings, routed through `litellm` to support
  OpenAI, Anthropic, Ollama, vLLM, NVIDIA NIM, and 100+ providers
  (`a7395b9`, `670b4c8`).
- `YAML` frontmatter serialization with proper escaping and unescaping
  (`ca9d3a9`).

#### OKF v0.1 Bundle Serialization
- `BundleSerializer` for the OKF v0.1 directory format (`index.md` plus
  per-concept Markdown files, YAML frontmatter, tag-based subdirectory
  grouping) (`d498bf5`, `6adc396`).
- Structural bundle validation: link resolution, orphan detection,
  absolute URL skipping in `links_in_index` (`9d79c3e`, `6adc396`).

#### CLI
- `knowledge` console script with `create`, `update`, and `remove`
  subcommands and a `--model` flag for LLM selection (`f3baa2b`,
  `cbdb936`).

#### Tooling
- Hatchling build backend with `py.typed` PEP 561 marker
  (`4c978da`, `391993e`).
- `pytest` test suite (66+ tests) covering SDK, bundle, CLI, and import
  paths (`3c1c5ad`, `24e06fb`).
- `ruff` (lint + format), `mypy --strict` with the `pydantic` plugin,
  and `vulture` for dead-code detection (`391993e`, `6b2b750`,
  `bfc54f6`).
- `cleanup.sh` for removing caches, build artifacts, and generated
  bundles (`b9d8a74`).

#### CI
- GitHub Actions CI on `master` for Python 3.12 and 3.13:
  `ruff check`, `ruff format --check`, `mypy`, `pytest --cov`,
  and `python -m build` (`7c3fa8b`, `80f56c9`).
- Release workflow publishing to PyPI on `release: published` events
  via `pypa/gh-action-pypi-publish` (`214852c`).
- Dependabot configuration for pip, GitHub Actions, and Docker
  (`214852c`).
- Issue templates (`bug_report.md`, `feature_request.md`) and a pull
  request template (`106265b`).

#### Documentation
- `README.md` with badges, features, configuration tables, quick-start
  examples, and tech stack (`5f43bdc`, `2685996`).
- MkDocs Material site with `index`, `getting-started`, `architecture`,
  and `faq` pages (`2aef421`, `214852c`).
- `docs/adr/0001-kmd-flat-format-v0.1.md` and
  `docs/adr/0002-bundle-format-v0-1.md` (the latter supersedes the
  former) (`0ec88a1`, `ce0e2e9`).
- `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md` (Contributor Covenant v2.1),
  and `SECURITY.md` (`e68d8a1`).
- `BENCHMARK.md` covering large-graph scenarios and a Google Python
  Style Guide OKF bundle example (`214852c`, `7d00c2a`,
  `730301a`).
- `ROADMAP.md` aligned with the bundle-only SDK direction
  (`b054124`, `81c3e41`).
- `.env.example` documenting `KNOWLEDGE_DEFAULT_MODEL`,
  `KNOWLEDGE_MAX_BODY_SIZE`, `KNOWLEDGE_REQUEST_TIMEOUT`,
  `KNOWLEDGE_MAX_RETRIES`, and provider keys (`9f09668`,
  `be7706b`).
- `.editorconfig` and `.gitattributes` for consistent editor and
  line-ending behaviour (`9f09668`).

### Changed

- **Architecture:** The package was stripped to a bundle-only SDK;
  the KMD flat format, extraction pipeline, pass framework, verification
  engine, and normalization modules from the v0.1.0 design phase were
  removed before tagging (`2cc9e68`).
- **API:** Removed dead `source_url` parameter, dead `check_duplicates`
  helper, and the unused `ValidationError` exception class
  (`ca9d3a9`, `c4d03f9`).
- **CLI:** Replaced `print()` calls with structured `logging` and
  removed semi-private naming throughout (`6b2b750`,
  `2677c94`).
- **Tooling:** Removed the redundant `black` dependency, aligned
  formatter line-length to 100, and removed stale entries from
  `.gitignore` (`6376a93`).
- **Documentation:** Replaced `anomalyco/knowledge` and the
  `knowledge-sdk.dev` placeholder with the canonical
  `sachncs/knowledge` repository URL across all files
  (`98dccc3`, `1885059`).
- **Documentation:** Corrected Ollama env-var documentation
  (`OLLAMA_HOST`) and vLLM endpoint guidance (`356c1b5`).
- **Documentation:** Replaced the older KMD and verification-engine
  content in `README`, `CONTRIBUTING`, and `SECURITY` with material
  that matches the current bundle-only SDK (`005674b`).
- **License:** Copyright year updated to 2026 (`1e6cb09`).

### Fixed

- Corrected 6 bugs in extraction, URL fetching, and YAML
  serialization (`d04295c`).
- `BundleSerializer` now skips empty intermediate directories in the
  root `index.md`, restricts the link regex to bundle-relative paths,
  and removes stale files on re-serialization (`6adc396`).
- The bundle validator now skips absolute URLs in `links_in_index`
  rather than flagging them as broken (`9d79c3e`).
- `StrEnum` is used in place of `str + Enum`, and a redundant
  `cast` was removed (`32d1d97`).
- Fixed brittle version-format tests and strengthened validation
  assertions (`8db14f7`).
- Renamed a CLI test to clarify the intent of the `--model` flag
  (`6116211`).
- Benchmarks run without requiring `pytest-benchmark` as a hard
  dependency (`f38ee07`).
- Confidence range is now enforced by the repair pass rather than the
  Pydantic model, restoring model responsibility for semantics
  (`5a5f17a`).
- `CONTRIBUTING.md` references the `master` branch rather than `main`
  (`5cbaee0`).
- Ruff format pass applied to source files with long docstrings
  (`947a5e9`, `acb5892`).
- Unused imports removed from the test tree (`af2cb8c`).

### Dependencies

- Runtime: `pydantic>=2.0`, `litellm>=1.91.0` (`dd50451`).
- Dev: `pytest>=9.1.1` (`9bec050`), `pytest-cov>=7.1.0` (`5d84af7`),
  `ruff>=0.15.20` (`5f80933`), `mypy>=2.1.0` (`09d6501`),
  `vulture>=2.7`.
- Docs: `mkdocs>=1.6.1` (`d302fb2`), `mkdocstrings[python]>=0.25.0`,
  `mkdocs-material>=9.5.0`.
- CI: `actions/setup-python` bumped from 5 to 6 (`6da0b5e`).

### Dependabot PRs merged into 0.1.0

- #2 — `actions/setup-python` 5 → 6 (`6da0b5e`, merged `fba210b`).
- #6 — ruff 0.6.0 → 0.15.20 (`5f80933`, merged `690990c`).
- #7 — pytest 8.0 → 9.1.1 (`9bec050`, merged `0994e7c`).
- #8 — mypy 1.11.0 → 2.1.0 (`09d6501`, merged `f2497d5`).
- #9 — mkdocs 1.6.0 → 1.6.1 (`d302fb2`, merged `debc595`).
- #13 — litellm 1.40.0 → 1.91.0 (`dd50451`, merged `cf87a2f`).
- #14 — pytest-cov 5.0 → 7.1.0 (`5d84af7`, merged `066c380`).

### Release

- Tagged `0.1.0-alpha` (`7b4cc36`).
- Version constant `0.1.0` in `knowledge/version.py` and
  `pyproject.toml`.
- `User-Agent` header for HTTP requests set to `knowledge-sdk/0.1.0`
  (`knowledge/sdk.py`).

[Unreleased]: https://github.com/sachncs/knowledge/compare/0.1.0...HEAD
[0.1.0]: https://github.com/sachncs/knowledge/releases/tag/0.1.0
