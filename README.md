<p align="center">
  <h1 align="center">knowledge</h1>
  <p align="center">LLM-powered OKF bundle creation from documentation sources.</p>
  <p align="center">
    <a href="#installation"><img src="https://img.shields.io/badge/python-3.12%20%7C%203.13-blue" alt="Python"></a>
    <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-green" alt="License"></a>
    <a href="https://github.com/sachn-cs/knowledge/actions"><img src="https://img.shields.io/github/actions/workflow/status/sachn-cs/knowledge/ci.yml?branch=master" alt="CI"></a>
    <a href="https://pypi.org/project/knowledge/"><img src="https://img.shields.io/pypi/v/knowledge" alt="PyPI"></a>
    <a href="https://github.com/sachn-cs/knowledge/stargazers"><img src="https://img.shields.io/github/stars/sachn-cs/knowledge" alt="Stars"></a>
  </p>
</p>

**knowledge** is a Python SDK that downloads a URL (or reads a local file),
splits the document into sections by headings, sends each section to an LLM
for structured concept extraction, and writes the results as an
[**OKF v0.1**](docs/adr/0002-bundle-format-v0-1.md) directory bundle.

---

## Features

- **LLM-Powered Extraction** — Uses [litellm](https://litellm.ai) to support
  OpenAI, Anthropic, Ollama, vLLM, and 100+ other models with a single interface.
- **OKF v0.1 Bundles** — Standard directory-based format with `index.md`,
  per-concept Markdown files, YAML frontmatter, and tag-based subdirectory
  grouping.
- **Section-Aware Splitting** — Handles both HTML (`<h2>`–`<h4>`) and Markdown
  (`##`) headings, extracting one concept per section.
- **Resilient Fetching** — Retries with exponential backoff, size limits (50 MiB),
  charset detection, and HTTP error classification.
- **CLI + Python API** — Use the `knowledge` CLI or import the SDK directly.
- **Bundle Validation** — Structural consistency checks (link resolution, orphan
  detection).
- **Immutable Models** — `Concept` and `KnowledgeGraph` are frozen Pydantic
  objects; every mutation returns a new instance.

---

## Installation

### From PyPI (when published)

```bash
pip install knowledge
```

### From source

```bash
git clone https://github.com/sachn-cs/knowledge.git
cd knowledge
pip install -e .
```

### With dev dependencies

```bash
pip install -e ".[dev]"
```

---

## Quick Start

### CLI

```bash
# Create a bundle from a URL
knowledge create https://google.github.io/styleguide/pyguide.html style-guide/

# Use a different LLM model
knowledge --model claude-3-opus-20240229 create https://example.com/docs.html ./bundle

# Update an existing bundle by re-extracting from source
knowledge update https://example.com/docs.html ./bundle

# Remove specific concepts by ID
knowledge remove obsolete-section outdated-topic ./bundle
```

### Python API

```python
from knowledge import Knowledge

k = Knowledge(model="gpt-4o")

# Return an in-memory KnowledgeGraph
graph = k.create("https://google.github.io/styleguide/pyguide.html")
print(graph.concepts)  # Dict[str, Concept]

# Write an OKF bundle to disk
count = k.create_bundle("https://google.github.io/styleguide/pyguide.html", "style-guide/")
print(f"Wrote {count} concept files")

# Update an existing bundle
k.update("https://google.github.io/styleguide/pyguide.html", "style-guide/")

# Remove specific concepts
k.remove(["deprecated-section"], "style-guide/")
```

---

## Configuration

### LLM Provider

Set the API key for your provider as an environment variable:

| Provider   | Env Variable       | Example Model String              |
|------------|--------------------|------------------------------------|
| OpenAI     | `OPENAI_API_KEY`   | `gpt-4o`                           |
| Anthropic  | `ANTHROPIC_API_KEY`| `claude-3-opus-20240229`           |
| Ollama     | `OLLAMA_HOST`      | `ollama/llama3` (default `http://localhost:11434`) |
| vLLM       | *(custom endpoint)*| `open-mistral-nemo` (set `api_base` in litellm) |

Pass the model via the `--model` CLI flag or `Knowledge(model=...)`.

### HTTP Client

| Setting              | Env Variable               | Default    |
|----------------------|----------------------------|------------|
| Max body size        | `KNOWLEDGE_MAX_BODY_SIZE`  | 50 MiB     |
| Request timeout      | `KNOWLEDGE_REQUEST_TIMEOUT`| 30 s       |
| Max retries          | `KNOWLEDGE_MAX_RETRIES`    | 3          |

See [`.env.example`](.env.example) for all options.

---

## Project Structure

```
knowledge/
├── knowledge/              # SDK package
│   ├── __init__.py         # Public API exports
│   ├── cli.py              # CLI (argparse)
│   ├── sdk.py              # Knowledge class, fetch_url
│   ├── models.py           # Concept, KnowledgeGraph (Pydantic)
│   ├── exceptions.py       # KnowledgeError hierarchy
│   ├── version.py          # PEP 440 version
│   ├── kmd/                # Bundle serialization
│   │   ├── __init__.py
│   │   └── bundle.py       # BundleSerializer
│   └── llm/                # LLM extraction
│       ├── __init__.py
│       ├── extractor.py    # LLMExtractor
│       └── manager.py      # KnowledgeBundleManager
├── tests/                  # Test suite
│   ├── test_sdk.py         # 35 tests
│   ├── test_bundle.py      # 14 tests
│   ├── test_cli.py         # 14 tests
│   └── test_import.py      # 3 tests
├── docs/                   # Documentation
├── pyproject.toml          # Build & tool config
└── .github/                # CI, templates
```

---

## Development

```bash
# Install with dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Lint
ruff check knowledge/ tests/

# Format
ruff format knowledge/ tests/

# Type check
mypy knowledge/

# All checks
pytest && ruff check knowledge/ tests/ && mypy knowledge/
```

### Code Style

- Line length: 100
- Quotes: double (`"`)
- Formatting: ruff (auto-format with `ruff format`)
- Type hints: required on all public signatures
- No semi-private naming (`_foo`) — all identifiers are public

### Commit Conventions

We use [Conventional Commits](https://www.conventionalcommits.org/):

```
feat: add markdown heading detection
fix: handle oversized Content-Length header
docs: add API reference
refactor: extract yaml_escape to static method
test: add round-trip serialization tests
chore: update ruff config
```

---

## Tech Stack

| Category       | Technology                                  |
|----------------|---------------------------------------------|
| Language       | Python 3.12+                                |
| LLM Interface  | [litellm](https://litellm.ai)               |
| Validation     | [Pydantic](https://docs.pydantic.dev/) 2+   |
| Build          | [Hatchling](https://hatch.pypa.io/)         |
| Lint/Format    | [ruff](https://docs.astral.sh/ruff/)        |
| Type Check     | [mypy](https://mypy-lang.org/) (strict)     |
| Testing        | [pytest](https://docs.pytest.org/) + pytest-cov |
| Docs           | [MkDocs](https://www.mkdocs.org/) + Material |

---

## Roadmap

See [ROADMAP.md](ROADMAP.md) for planned features and milestones.

- **v0.1.0** — Current pre-release: core extraction, serialization, CLI
- **v0.2.0** — Property-based testing, PDF support, configurable pass ordering
- **v1.0.0** — Stable API, PyPI release, full OKF v0.1 compliance

---

## Contributing

We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md) for:

- Development setup
- Pull request process
- Coding standards
- Test expectations

## Code of Conduct

This project follows the [Contributor Covenant v2.1](CODE_OF_CONDUCT.md).
By participating you agree to abide by its terms.

## Security

Report vulnerabilities to **sachncs@gmail.com** — see [SECURITY.md](SECURITY.md).

## License

[MIT](LICENSE) © 2026 knowledge contributors
