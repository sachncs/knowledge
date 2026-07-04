# Contributing to knowledge

Thank you for considering contributing to the `knowledge` SDK.

## Development Setup

```bash
# Clone the repository
git clone https://github.com/anomalyco/knowledge.git
cd knowledge

# Install with dev dependencies
pip install -e ".[dev]"

# Run all checks
pytest
ruff check knowledge/ tests/
mypy knowledge/
```

## Project Structure

```
knowledge/           # Package source
tests/               # Test suite (pytest)
docs/                # Documentation (mkdocs)
examples/            # Usage examples
```

## Pull Request Process

1. Ensure all existing tests pass.
2. Add tests for any new functionality.
3. Run `ruff check knowledge/ tests/` — no violations.
4. Run `mypy knowledge/` — no type errors.
5. Update documentation if public APIs change.
6. Update `CHANGELOG.md` with the change description.
7. Open a pull request against the `master` branch.

## Code Style

- Target Python 3.12+
- Line length: 100 characters
- Use double quotes for strings
- Follow existing patterns in the codebase
- Prefer deterministic algorithms over semantic reasoning

## Design Principles

- Every mutation passes through verification.
- Prefer immutable transformations (return new instances).
- Use explicit provenance for all knowledge elements.
- Small, composable compiler passes with one responsibility each.
- Stable semantic identity for all knowledge elements.

## Testing

```bash
# Run all tests
pytest

# Run a specific test file
pytest tests/test_sdk.py -v

# Run with coverage
pytest --cov=knowledge
```

## Documentation

Docs are built with mkdocs:

```bash
mkdocs serve  # Live preview at http://localhost:8000
mkdocs build  # Static site in site/
```

## License

By contributing, you agree that your contributions will be licensed under
the MIT License.
