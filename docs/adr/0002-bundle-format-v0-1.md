# ADR-002: Implement OKF v0.1 bundle format in v0.1.0

**Status:** Accepted

**Date:** 2026-07-04

**Drivers:** @anomalyco

**Supersedes:** ADR-001

## Context

ADR-001 deferred the OKF v0.1 directory-bundle format to v0.2.0. Two factors
motivate revisiting this decision:

1. **Real-world demand:** The Google Python Style Guide bundle at
   `examples/google-python-style-guide/` demonstrated that OKF bundles are
   the primary output users want from `knowledge create`. A flat KMD file is
   not suitable for documentation consumption.

2. **Section-aware extraction:** Processing HTML sources by section headings
   produces higher-quality concepts than tag-stripped flat text. The bundle
   format naturally maps to this section-per-concept structure.

Since the internal `KnowledgeGraph` model is format-agnostic, adding bundle
support requires only a new serializer (not model changes). The section-aware
HTML reader is an orthogonal improvement to the source-reader layer.

## Options Considered

### Option A: Implement bundle + section-aware extraction now

- **Pro:** Satisfies real user workflow (`knowledge create <url> -o <dir>`).
- **Pro:** Bundle serializer reuses existing `Concept` model — no data loss.
- **Pro:** Section-aware HTML reader is a new source reader (like
  `MarkdownSourceReader`), not a pipeline rewrite.
- **Pro:** The example bundle at `examples/` validates the output format.
- **Con:** Adds surface area before v0.1.0 release.
- **Con:** `OKFDocument.save()` needs a second output path (directory vs file).

### Option B: Keep deferring to v0.2.0

- **Pro:** No new code before release.
- **Con:** `knowledge create <url> -o <dir>` still produces a flat KMD file
  instead of the documented example bundle.
- **Con:** Users must use a separate (removed) scripts to generate bundles.

### Option C: Only implement bundle serializer, skip section-aware extraction

- **Pro:** Less code.
- **Con:** Extracted concepts from HTML are still low-quality (entities like
  "NoneType", "Pros") because flat tag-stripping loses section structure.

## Decision

**Accept Option A.** Implement both the OKF v0.1 bundle serializer and the
section-aware HTML source reader in v0.1.0.

## Implementation

### Bundle serializer (`knowledge/kmd/bundle.py`)

- `BundleSerializer(graph, output_dir)` writes each `Concept` to a Markdown
  file with YAML frontmatter (`id`, `title`, `type`, `tags`, `source`).
- Concepts are grouped into subdirectories by `tags` matching known category
  prefixes (e.g. `language` → `rules/language/`).
- Auto-generates `index.md` for each directory.
- Writes `type: concept` for leaf entries, `type: index` for directory
  indexes, `type: bundle` for the root index.

### Section-aware source reader (`knowledge/llm/extractor.py`)

- `LLMExtractor` splits source text by top-level headings (HTML `<h2>` or
  markdown `##`) using regex, then sends each section to an LLM via litellm.
- The LLM converts the raw section content (HTML or markdown) into clean
  Markdown and returns a structured JSON concept object with `id`, `name`,
  `description`, `tags`, and `level`.
- Supports any litellm-compatible model (OpenAI, Anthropic, Ollama, vLLM, etc.).
- Falls back to treating the entire document as a single section when no
  heading structure is detected.

### SDK integration (`knowledge/sdk.py`)

- `Knowledge.create(source)`: fetches or reads the source, delegates to
  `LLMExtractor.extract()`, and returns a `KnowledgeGraph`.
- `Knowledge.create_bundle(source, output_dir)`: fetches/reads, extracts,
  and serializes via `BundleSerializer`.
- `Knowledge.update(source, bundle_dir)`: re-extracts from source and
  overwrites the existing bundle.
- `Knowledge.remove(concept_ids, bundle_dir)`: reads the existing bundle,
  removes the specified concept IDs, and re-serializes.

### CLI (`knowledge/cli.py`)

- `knowledge create <input> <output>` extracts concepts and writes OKF bundle.
- `knowledge update <input> <bundle_dir>` re-extracts and overwrites an
  existing bundle.
- `knowledge remove <concept_id>... <bundle_dir>` removes specific concepts
  from a bundle by their IDs.
- All commands accept `--model` to select the LLM (default `gpt-4o`).

## Consequences

### Positive

- `knowledge create <url> <dir>` produces the documented bundle format.
- LLM-based extraction produces high-quality concepts from HTML sources,
  converting HTML formatting to clean Markdown faithfully.
- The `KnowledgeGraph` model is format-agnostic; `BundleSerializer` is a pure
  serialization layer.

### Negative

- Bundle output requires filesystem directory I/O, which is more complex than
  flat file writes.
- LLM extraction requires API access (OpenAI, Anthropic, or local model via
  Ollama) and adds latency and per-request cost compared to rule-based parsing.
