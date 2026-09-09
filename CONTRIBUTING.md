# Contributing

Thank you for your interest in **knowledge**! We welcome contributions
of all kinds — bug fixes, features, documentation, and ideas.

---

## Table of Contents

- [Development Setup](#development-setup)
- [Branch Naming](#branch-naming)
- [Commit Conventions](#commit-conventions)
- [Pull Request Process](#pull-request-process)
- [Coding Standards](#coding-standards)
- [Testing](#testing)
- [Documentation](#documentation)
- [Code of Conduct](#code-of-conduct)

---

## Development Setup

```bash
# Fork and clone the repository
git clone https://github.com/your-username/knowledge.git
cd knowledge

# Install with dev dependencies
pip install -e ".[dev]"

# Verify everything works
pytest
ruff check knowledge/ tests/
mypy knowledge/
```

---

## Branch Naming

Use a short, descriptive name prefixed by the type of change:

| Prefix     | Example                          |
|------------|----------------------------------|
| `feat/`    | `feat/markdown-heading-support` |
| `fix/`     | `fix/content-length-crash`      |
| `docs/`    | `docs/api-reference`            |
| `refactor/`| `refactor/extractor-module`     |
| `test/`    | `test/round-trip-edge-cases`    |
| `chore/`   | `chore/update-ci`               |

---

## Commit Conventions

We follow **Conventional Commits** (`v1.0.0`):

```
<type>: <short description>

[optional body]
[optional footer]
```

### Types

| Type       | Usage                                      |
|------------|--------------------------------------------|
| `feat`     | A new feature                              |
| `fix`      | A bug fix                                  |
| `docs`     | Documentation changes only                 |
| `refactor` | Code change that neither fixes nor adds    |
| `test`     | Adding or updating tests                   |
| `chore`    | Build, CI, dependencies, tooling           |
| `style`    | Formatting (white-space, semicolons, etc.) |

The subject line must be 72 characters or less and use the imperative mood
("add" not "added" or "adds").

---

## Pull Request Process

1. **Create an issue** describing the bug or feature before starting work
   (unless it is a trivial fix).
2. **Fork the repo** and create a branch from `master`.
3. **Write tests** for your change (aim for 80%+ coverage on new code).
4. **Run all checks** locally:
   ```bash
   pytest
   ruff check knowledge/ tests/
   ruff format --check knowledge/ tests/
   mypy knowledge/
   ```
5. **Update documentation** if your change affects the public API or CLI.
6. **Open a pull request** with a clear title and description. Reference the
   issue number in the description.
7. **Address review feedback** — all CI checks must pass before merging.

---

## Coding Standards

- **Python**: 3.12+
- **Line length**: 100 characters
- **Quotes**: double (`"`) for all strings
- **Type hints**: required on all public function/method signatures
- **Naming**: all identifiers are public (no `_foo` semi-private naming)
- **Formatting**: run `ruff format` before committing
- **Imports**: standard library → third-party → local (separated by blank line)
- **Docstrings**: Google-style module, class, and public method docstrings

### Example

```python
"""Module-level docstring."""

from __future__ import annotations

import os

from pydantic import BaseModel


class MyModel(BaseModel):
    """Short description."""

    name: str

    def greet(self, greeting: str) -> str:
        """Return a greeting string."""
        return f"{greeting}, {self.name}!"
```

---

## Testing

- **Framework**: pytest
- **Location**: `tests/`
- **Coverage target**: 90%+
- **Naming**: `test_<module>.py` for files, `test_<method>_<scenario>` for functions
- **Fixtures**: prefer `conftest.py` for shared fixtures
- **No network calls**: mock `litellm.completion` and `urlopen` in tests

```bash
# Run all tests
pytest

# With coverage
pytest --cov=knowledge

# Specific test file
pytest tests/test_sdk.py

# Verbose
pytest -v
```

---

## Documentation

- **API docs**: docstrings in the source code (Pydocstyle-compatible).
- **User-facing docs**: Markdown files in `docs/`.
- **Architecture decisions**: ADR files in `docs/decisions/`.
- When adding a new public class or function, include a docstring with:
  - Short description
  - `Args:` section
  - `Returns:` section
  - `Raises:` section (if applicable)
  - Optional `Example:` code block

---

## Code of Conduct

This project adheres to the [Contributor Covenant v2.1](CODE_OF_CONDUCT.md).
By participating you agree to uphold this code. Report unacceptable behavior
to **sachncs@gmail.com**.
