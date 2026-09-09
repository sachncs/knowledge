# Concepts

The terms used throughout this documentation, defined once so the rest of the docs can use them freely.

## OKF bundle

An **OKF (Open Knowledge Format) v0.1 bundle** is a directory that contains an `index.md`, one `.md` file per concept, and optional subdirectories for grouped concepts. Each concept file uses YAML frontmatter between `---` delimiters.

A minimal bundle looks like this:

```text
my-bundle/
├── index.md
└── getting-started.md
```

`my-bundle/getting-started.md`:

```markdown
---
id: getting-started
title: "Getting Started"
type: concept
tags: ["guide"]
---

## Getting Started

Welcome to the documentation.
```

The full specification is in [ADR-002](decisions/0002-okf-v0-1-bundle-format.md).

## Concept

A `Concept` is a single extracted unit — one heading-level section from the source document, converted to clean Markdown by the LLM. Every `Concept` has:

- `id` — a kebab-case slug, also used as the filename (`^[a-z][a-z0-9-]*$`).
- `name` — the canonical name or heading text.
- `description` — the section body in Markdown (may be `None`).
- `tags` — short categorisation terms, used by `path_map` to group concepts into subdirectories.

## KnowledgeGraph

A `KnowledgeGraph` is an immutable container of `Concept` objects, keyed by `id`. The model is frozen (Pydantic `frozen=True`), so every mutation returns a **new** instance. This makes graphs safe to share between threads and easy to reason about in pipelines.

```python
from knowledge.models import Concept, KnowledgeGraph

graph = KnowledgeGraph()
graph = graph.add_concept(Concept(id="intro", name="Introduction"))
graph = graph.remove_concept("intro")
```

## Source

A **source** is the input to extraction. It can be:

- An `http://` or `https://` URL — fetched via `fetch_url` with retries, size limits, and charset detection.
- A local file path — read directly with UTF-8 encoding.

Anything else (including `ftp://` or `file://`) is treated as a file path and likely fails with `FetchError`.

## Section

A **section** is a contiguous block of text under one heading. The extractor recognises:

| Format | Headings recognised |
|--------|---------------------|
| HTML   | `<h1>` through `<h6>` (HTML comments stripped first) |
| Markdown | ATX `#` through `######`, plus trailing-`#` and Setext-style underlines |

When no headings are found, the entire document is treated as a single section named `Document`.

## LLM extraction

**LLM extraction** is the process of converting raw section text into a structured `Concept`. `LLMExtractor` sends each section to the configured model with a prompt that asks for a JSON object matching the `LLMResponse` schema:

```json
{
  "id": "installing-the-sdk",
  "name": "Installing the SDK",
  "description": "...",
  "tags": ["setup"],
  "level": 2
}
```

Failures are isolated per section: a bad prompt or malformed response logs a warning and skips the section, but does not abort the entire extraction.

## Bundle validation

`BundleSerializer.validate()` walks a written bundle and reports structural issues:

- Missing root `index.md`.
- Broken Markdown links in any `index.md`.
- Orphan `.md` files that no `index.md` links to.

Run validation from the CLI after a create with `--validate`, or directly from Python:

```python
from knowledge.kmd.bundle import BundleSerializer

issues = BundleSerializer().validate("./my-bundle")
```

## path_map

A `path_map` is an optional `{tag: subdirectory}` mapping. Concepts whose `tags` list contains one of the keys are placed in the corresponding subdirectory instead of the bundle root. For example, `{"guide": "docs/guides"}` sends every concept tagged `guide` to `docs/guides/`.

## Resilient fetching

`fetch_url` is the HTTP client used internally. It:

- Retries network errors, `URLError`, `ConnectionError`, `TimeoutError`, HTTP 429 and HTTP 5xx with exponential backoff (`1s, 2s, 4s`).
- Rejects responses whose `Content-Length` header exceeds `MAX_BODY_SIZE` (50 MiB by default) **before** reading the body.
- Reads up to `MAX_BODY_SIZE + 1 KiB` of body and fails if the actual size exceeds the limit.
- Detects the response encoding from the `Content-Type` charset, falling back to UTF-8.
- Decodes invalid byte sequences as the Unicode replacement character instead of raising.
