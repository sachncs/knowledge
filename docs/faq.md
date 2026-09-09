# Frequently asked questions

## General

### What is an OKF bundle?

OKF (Open Knowledge Format) v0.1 is a directory-based format for storing structured knowledge. A bundle consists of an `index.md` at the root, per-concept Markdown files with YAML frontmatter, and optional subdirectory indexes for tag-grouped concepts.

See [ADR-002](decisions/0002-okf-v0-1-bundle-format.md) for the full specification, or [Concepts](concepts.md) for a worked overview.

### Which LLM providers are supported?

Any provider that [litellm](https://litellm.ai) supports. As of litellm 1.99+ this includes OpenAI, Anthropic, Google Gemini, AWS Bedrock, Azure OpenAI, Ollama, vLLM, NVIDIA NIM, and many others. The exact list evolves with litellm — pass the model string you would use with litellm directly to `knowledge --model <model>`.

### Do I need an API key?

Yes, if you use a cloud provider. For local models via Ollama, no API key is needed — start the Ollama daemon and pass `ollama/<model-name>`.

## Usage

### Can I process local files?

Yes. Pass a file path instead of a URL:

```bash
knowledge create ./my-document.html ./output-bundle
```

See [Run the SDK without network access](tutorials/local-files.md) for details.

### How are documents split?

The extractor looks for HTML `<h1>`–`<h6>` tags first. If none are found, it falls back to Markdown `#`–`######` headings. If neither is found, the entire content is treated as a single section.

### Can I choose which concepts to extract?

Not directly during extraction — the LLM processes each heading section and returns one concept per section. After extraction, you can curate the bundle with `knowledge remove <concept-id>... <bundle-dir>`. See [Curate a bundle by removing concepts](tutorials/curate-bundle.md).

### Is the extraction deterministic?

With `temperature=0.0` (the default), the same input plus model should produce consistent results. Output can still vary slightly between model versions or provider rollouts.

### Can I use `knowledge` programmatically without the CLI?

Yes — the `Knowledge` class is the canonical entry point. The CLI is a thin wrapper. See [Python API](api.md).

## Bundles

### Can I edit concept files by hand?

Yes. Concept files are plain Markdown with simple YAML frontmatter. Edit them with any text editor, then re-validate with `knowledge create --validate <src> <bundle>` (validation does not modify files).

!!! warning

    Hand-edited concept files are overwritten the next time you run `knowledge update`. Back them up first.

### Can I write a bundle without calling the LLM?

Yes. Use `BundleSerializer.serialize(graph, output_dir)` directly. Build a `KnowledgeGraph` from your own data and serialise it — no LLM, no network.

### How do I add new tags to a concept?

Edit the concept's `.md` file directly. The `tags` field is a list in the YAML frontmatter:

```markdown
---
id: getting-started
title: "Getting Started"
type: concept
tags: ["guide", "tutorial"]
---
```

If you are using a `path_map`, adding a tag whose key matches the map will move the concept into the corresponding subdirectory the next time `knowledge create` runs.

## Development

### How do I add a new feature?

1. Open an issue describing the feature.
2. Fork the repo and create a feature branch.
3. Implement the change with tests.
4. Run all checks (`pytest`, `ruff check`, `ruff format --check`, `mypy`).
5. Open a pull request.

See [Contributing](contributing.md) for the full contribution guide.

### How is the project tested?

- `pytest` with `pytest-cov` for coverage.
- `ruff check` and `ruff format --check` for linting and formatting.
- `mypy --strict` with the `pydantic` plugin for type checking.
- No network calls in tests — every LLM and HTTP call is mocked.

### Where do I report a bug?

Open a [GitHub issue](https://github.com/sachncs/knowledge/issues). For security vulnerabilities, see [SECURITY.md](https://github.com/sachncs/knowledge/blob/master/SECURITY.md) — do not open a public issue.
