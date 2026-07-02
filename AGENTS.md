# AGENTS.md

Instructions for AI agents working on the `knowledge` SDK.

## Development Commands

```bash
# Install with dev dependencies
pip install -e ".[dev]"

# Run all checks
ruff check knowledge/
mypy knowledge/
pytest

# Run a single test
pytest tests/test_import.py -v
```

## Project Structure

```
knowledge/           # Package source
tests/               # Test suite
docs/                # Documentation source (mkdocs)
examples/            # Usage examples
```

## Design Principles

Refer to SPEC.md for complete architecture and design rules.

Key principles:
- Knowledge Model is internal; OKF is the persistence format.
- Every mutation passes through verification.
- Deterministic before intelligent.
- Immutable transformations preferred.
- Stable semantic identity for all knowledge elements.
- Small, composable compiler passes.
