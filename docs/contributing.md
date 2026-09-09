# Contributing

Thank you for your interest in **knowledge** — bug reports, feature ideas, documentation improvements, and pull requests are all welcome.

This page summarises the contribution workflow. The full guide lives in [`CONTRIBUTING.md`](https://github.com/sachncs/knowledge/blob/master/CONTRIBUTING.md) at the repository root.

## Code of conduct

This project follows the [Contributor Covenant v2.1](https://github.com/sachncs/knowledge/blob/master/CODE_OF_CONDUCT.md). By participating you agree to uphold its terms. Report unacceptable behaviour to **sachncs@gmail.com**.

## Development setup

```bash
git clone https://github.com/sachncs/knowledge.git
cd knowledge
pip install -e ".[dev,docs]"
pytest
ruff check knowledge/ tests/
ruff format --check knowledge/ tests/
mypy knowledge/
```

## Branch naming

Use a short, descriptive name prefixed by the change type:

| Prefix      | Example                              |
|-------------|--------------------------------------|
| `feat/`     | `feat/markdown-heading-support`      |
| `fix/`      | `fix/content-length-crash`           |
| `docs/`     | `docs/api-reference`                 |
| `refactor/` | `refactor/extractor-module`          |
| `test/`     | `test/round-trip-edge-cases`         |
| `chore/`    | `chore/update-ci`                    |

## Commit conventions

We follow [Conventional Commits](https://www.conventionalcommits.org/). The subject line must be 72 characters or less and use the imperative mood ("add" not "added" or "adds").

```text
feat: add markdown heading detection
fix: handle oversized Content-Length header
docs: add API reference
refactor: extract yaml_escape to a static method
test: add round-trip serialization tests
chore: update ruff config
```

## Coding standards

- Python 3.12+
- Line length: 100 characters
- Quotes: double (`"`)
- Type hints: required on all public function and method signatures
- Naming: all identifiers are public (no `_foo` semi-private naming)
- Imports: standard library, then third-party, then local (separated by blank lines)
- Docstrings: Google-style on modules, classes, and public methods

## Testing

- Framework: `pytest`
- Location: `tests/`
- Coverage target: 90 %+
- No network calls — mock `litellm.completion` and `urlopen`

```bash
pytest                    # full suite
pytest --cov=knowledge    # with coverage
pytest tests/test_sdk.py  # one module
```

## Documentation

- Docstrings document the public API and are rendered into the [Python API](api.md) page via `mkdocstrings`.
- User-facing pages live in `docs/` as Markdown files.
- Architecture decisions live in `docs/decisions/` as ADRs.

When you add a new public class or function, include a docstring with `Args:`, `Returns:`, and `Raises:` sections where applicable.

## Pull request process

1. Create an issue describing the change (unless it is trivial).
2. Fork the repo and create a branch from `master`.
3. Write tests for your change. Aim for 90 %+ coverage on new code.
4. Run every check locally: `pytest`, `ruff check`, `ruff format --check`, `mypy`.
5. Update documentation if the public API or CLI changed.
6. Open a pull request with a clear title and description. Reference the issue number.
7. Address review feedback. All CI checks must pass before merge.

## Reporting security issues

**Do not** open a public GitHub issue for security vulnerabilities. Email **sachncs@gmail.com** or follow the process in [SECURITY.md](https://github.com/sachncs/knowledge/blob/master/SECURITY.md).

## Release process

Releases are tagged in [CHANGELOG.md](changelog.md) and published to PyPI via the `release.yml` GitHub Actions workflow on a `release: published` event. See [Changelog](changelog.md) for the version history.
