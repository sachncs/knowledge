# Roadmap

## v0.1.0 — Current (pre-release)

- Core Pydantic models: `Concept`, `KnowledgeGraph` (frozen/immutable).
- OKF v0.1 bundle serializer (`BundleSerializer`) with YAML frontmatter,
  tag-based subdirectory grouping, and structural validation.
- LLM-powered extraction (`LLMExtractor`) via litellm with HTML/Markdown
  heading splitting.
- Resilient URL fetching with retries, size limits, and charset detection.
- `Knowledge` SDK class (create, create_bundle, update, remove).
- CLI (`knowledge` command) with create, update, remove subcommands.
- Bundle validation (link resolution, orphan detection, absolute URL skipping).
- Concept ID slug validation (`^[a-z][a-z0-9-]*$`).
- Test suite: 66+ tests.
- GitHub Actions CI (ruff, mypy, pytest with coverage, build).
- MkDocs documentation skeleton.
- Architecture Decision Records (ADR-001, ADR-002).

## v0.2.0 — Planned

- Property-based testing (Hypothesis).
- PDF source reader.
- Configurable pass ordering.
- Expanded bundle validation (description non-empty, glossary completeness,
  cross-reference consistency).
- Community-contributed features and bugfixes.

## v1.0.0 — Stable Release

- Stable public API (semver 1.0).
- PyPI release with automated publishing workflow.
- Comprehensive user documentation with tutorials.
- Benchmark regression tracking.
