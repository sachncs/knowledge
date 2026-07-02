# knowledge

**Knowledge is software.**

`knowledge` is an open-source Python SDK for creating, maintaining, verifying, and
evolving **Open Knowledge Format (OKF)** documents.

Unlike traditional document generation tools, `knowledge` treats an OKF document
as a **living software artifact** — structured, versioned, verified, and
continuously improvable.

---

## Status

**Milestone: Foundation** — v0.1.0

The core domain model, OKF parser/serializer, and compiler pass framework are
complete. Knowledge extraction, normalization, semantic verification, and the
public API are under active development.

| Milestone | Status |
|---|---|
| Project Foundation | ✅ Complete |
| Core Domain Model | ✅ Complete |
| OKF Support | ✅ Complete |
| Compiler Framework | ✅ Complete |
| Knowledge Extraction | ✅ Complete |
| Normalization | ✅ Complete |
| Semantic Verification | ✅ Complete |
| Verification Engine | 🚧 In Progress |
| Repair Engine | ❌ Not Started |
| Public SDK | ❌ Not Started |
| CLI | ❌ Not Started |
| Extension System | 🚧 Partial |
| Documentation | 🚧 Partial |
| Release Preparation | 🚧 Partial |

See [SPEC.md](SPEC.md) for the full architecture and roadmap.

---

## Quick Start

```python
from knowledge.okf import OKFParser, OKFSerializer
from knowledge.models import Entity, KnowledgeGraph
from knowledge.passes import (
    ExtractionPass,
    AliasResolutionPass,
    DuplicateDetectionPass,
    SemanticValidationPass,
    PassManager,
    Phase,
)

# Build a pipeline
manager = PassManager()
manager.register(ExtractionPass())
manager.register(AliasResolutionPass())
manager.register(DuplicateDetectionPass())
manager.register(SemanticValidationPass())

# Extract knowledge from source text
graph = KnowledgeGraph()
result = manager.execute(graph, config={
    "extraction.pipeline": {
        "content": "Python is a programming language. "
                   "JavaScript is used for web development.",
        "source": "example.md",
        "format": "text",
    }
})

# Serialize to OKF Markdown
serializer = OKFSerializer()
okf_output = serializer.serialize(result.graph)
print(okf_output)
```

## Installation

```bash
pip install knowledge-sdk
```

## Development

```bash
pip install -e ".[dev]"
pytest
ruff check knowledge/ tests/
mypy knowledge/
```

## Documentation

- [Architecture](docs/architecture.md) — System design and layer overview
- [API Reference](docs/api.md) — Public API documentation
- [SPEC.md](SPEC.md) — Full specification and roadmap

## License

MIT
