# Frequently Asked Questions

## General

### What is an OKF bundle?

OKF (Open Knowledge Format) v0.1 is a directory-based format for storing
structured knowledge. A bundle consists of an `index.md` at the root,
per-concept Markdown files with YAML frontmatter, and optional subdirectory
indexes for tag-grouped concepts.

See [ADR-002](adr/0002-bundle-format-v0-1.md) for the full specification.

### What LLM providers are supported?

Any provider supported by [litellm](https://litellm.ai) — OpenAI, Anthropic,
Ollama, vLLM, Google Gemini, AWS Bedrock, Azure OpenAI, and 100+ others.
Pass the model string via `--model` flag or `Knowledge(model="...")`.

### Do I need an API key?

Yes, if you use a cloud provider (OpenAI, Anthropic, etc.). For local
models via Ollama, no API key is needed.

## Usage

### Can I process local files?

Yes. Pass a file path instead of a URL:

```bash
knowledge create ./my-document.html ./output-bundle
```

### How are documents split?

The extractor looks for HTML `<h2>`–`<h4>` tags first. If none are found,
it falls back to Markdown `##` headings. If neither exists, the entire
content is treated as a single section.

### Can I choose which concepts to extract?

Not directly during extraction — the LLM processes each heading section
and returns one concept per section. However, you can surgically remove
unwanted concepts after extraction:

```bash
knowledge remove concept-id-1 concept-id-2 ./bundle
```

### Is the extraction deterministic?

With `temperature=0.0` (the default), the same input + model should
produce consistent results. However, LLM outputs can still vary slightly
between model versions.

## Development

### How do I add a new feature?

1. Open an issue describing the feature.
2. Fork the repo and create a feature branch.
3. Implement the change with tests.
4. Run all checks (`pytest`, `ruff`, `mypy`).
5. Open a pull request.

See [CONTRIBUTING.md](../CONTRIBUTING.md) for details.

### How is the project tested?

- **pytest** with pytest-cov for coverage.
- **ruff** for linting and formatting.
- **mypy** (strict mode) for type checking.
- No network calls in tests — all LLM and HTTP calls are mocked.

### Where can I report a bug?

Open a [GitHub issue](https://github.com/sachncs/knowledge/issues)
for non-security bugs. For security vulnerabilities, see
[SECURITY.md](../SECURITY.md).
