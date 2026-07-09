# knowledge SDK

**LLM-powered OKF bundle creation from documentation sources.**

`knowledge` is an open-source Python SDK that downloads a URL (or reads a
local file), splits the document into sections by headings, sends each
section to an LLM for structured concept extraction, and writes the
results as an **OKF v0.1** directory bundle.

---

## Quick Start

```bash
pip install git+https://github.com/sachncs/knowledge.git
```

```python
from knowledge import Knowledge

k = Knowledge(model="gpt-4o")

# Create an OKF bundle from a URL
k.create_bundle("https://google.github.io/styleguide/pyguide.html", "./pyguide")
```

Result: `./pyguide/index.md` + one `.md` per section, each with YAML frontmatter.

---

## Documentation

| Guide | Description |
|-------|-------------|
| [Getting Started](getting-started.md) | Installation, first bundle, Python API walkthrough |
| [Architecture](architecture.md) | Three-layer design, data flow, key decisions |
| [FAQ](faq.md) | Common questions about usage and development |

## CLI

```
knowledge [--model <model>] <command> [options]

Commands:
  create    Create a bundle from a URL or file
  update    Re-extract from source and overwrite a bundle
  remove    Remove specific concepts by ID
```

## API

| Method | Description |
|--------|-------------|
| `Knowledge.create(source)` | Return a `KnowledgeGraph` via LLM extraction |
| `Knowledge.create_bundle(source, output_dir)` | Extract + serialize as OKF v0.1 bundle |
| `Knowledge.update(source, bundle_dir)` | Re-extract and overwrite an existing bundle |
| `Knowledge.remove(concept_ids, bundle_dir)` | Remove concepts by ID |

## Key Concepts

- **LLM Extraction** — Documents are split by section headings; each
  section is sent to an LLM (via litellm) for structured concept extraction.
- **Knowledge Graph** — An immutable collection of `Concept` objects.
  Every mutation returns a new instance.
- **OKF v0.1 Bundle** — Directory-based persistence: `index.md`,
  per-concept `.md` files, YAML frontmatter, tag-based subdirectory
  grouping.
- **Update & Remove** — Bundles can be regenerated or surgically modified.

## Status — v0.1.0 (pre-release)

| Component | Status |
|-----------|--------|
| Core models (Concept, KnowledgeGraph) | ✅ |
| OKF v0.1 bundle serializer | ✅ |
| LLM-based extraction (via litellm) | ✅ |
| URL/file fetching with retries | ✅ |
| CLI (create, update, remove) | ✅ |
| Bundle validation | ✅ |

---

## Links

- [ADR-001: KMD flat format (superseded)](adr/0001-kmd-flat-format-v0.1.md)
- [ADR-002: OKF v0.1 bundle format](adr/0002-bundle-format-v0-1.md)
- [GitHub](https://github.com/sachncs/knowledge)
