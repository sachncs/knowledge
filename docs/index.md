# knowledge SDK

**A Python package for knowledge engineering.**

`knowledge` is an open-source Python SDK for creating, maintaining, and evolving
**Open Knowledge Format (OKF)** bundles from documentation sources.

## Quick Start

```bash
pip install git+https://github.com/sachn-cs/knowledge.git
```

```python
from knowledge import Knowledge

# Create an OKF bundle from a URL
knowledge = Knowledge(model="gpt-4o")
bundle = knowledge.create("https://google.github.io/styleguide/pyguide.html")
# bundle is a KnowledgeGraph with one Concept per section

# Write the bundle to disk
knowledge.create_bundle("https://google.github.io/styleguide/pyguide.html", "./pyguide")
```

## CLI

```bash
# Create a bundle from a URL or file
knowledge create https://example.com/docs.html ./output

# Update an existing bundle by re-extracting from source
knowledge update https://example.com/docs.html ./output

# Remove specific concepts from a bundle by ID
knowledge remove concept-id-1 concept-id-2 ./output

# Select a different LLM model
knowledge --model claude-3-opus-20240229 create https://example.com/docs.html ./output
```

## API

| Method | Description |
|--------|-------------|
| `Knowledge.create(source)` | Fetch/read source, extract concepts via LLM, return a `KnowledgeGraph` |
| `Knowledge.create_bundle(source, output_dir)` | Fetch/read + extract + serialize as OKF v0.1 directory bundle |
| `Knowledge.update(source, bundle_dir)` | Re-extract from source and overwrite an existing bundle |
| `Knowledge.remove(concept_ids, bundle_dir)` | Remove specific concepts from a bundle by their IDs |

## Key Concepts

- **LLM Extraction** — Documents are split by section headings; each section is sent to an LLM (litellm) for concept extraction as structured JSON.
- **Knowledge Graph** — An immutable collection of `Concept` objects. Each operation returns a new instance.
- **OKF v0.1 Bundle** — A directory-based persistence format: `index.md`, per-concept `.md` files, YAML frontmatter, tag-based subdirectory grouping.
- **Update & Remove** — Bundles can be incrementally modified: re-extract from source with `update()`, or surgically remove concepts with `remove()`.

## Status — v0.1.0 (pre-release)

| Component | Status |
|-----------|--------|
| Core models (Concept, KnowledgeGraph) | ✅ |
| OKF v0.1 bundle serializer | ✅ |
| LLM-based extraction (via litellm) | ✅ |
| URL/file fetching with retries | ✅ |
| CLI (create, update, remove) | ✅ |
| Bundle validation | ✅ |

## Links

- [ADR-001: KMD flat format (superseded)](adr/0001-kmd-flat-format-v0.1.md)
- [ADR-002: OKF v0.1 bundle format](adr/0002-bundle-format-v0-1.md)
