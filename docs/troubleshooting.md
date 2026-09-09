# Troubleshooting

Common problems and how to fix them. If your problem is not here, open an issue on [GitHub](https://github.com/sachncs/knowledge/issues) or check the [FAQ](faq.md).

## The CLI exits with code 1 and "Connection failed"

The HTTP client could not reach the URL after `KNOWLEDGE_MAX_RETRIES` attempts.

**Fix**

1. Verify the URL in a browser or with `curl -I <url>`.
2. If the URL is correct but flaky, raise the retry count by editing `MAX_RETRIES` in `knowledge/sdk.py` (planned: environment override in v0.2).
3. If your network blocks the request, configure a proxy or use a local source file instead (see [Run the SDK without network access](tutorials/local-files.md)).

## "Response too large"

The HTTP response body exceeds `KNOWLEDGE_MAX_BODY_SIZE` (50 MiB by default).

**Fix**

- If the source has a smaller "printable" version, use that URL instead.
- For local files, you can bypass the limit by reading the file directly with `Knowledge.read_source` and passing the string to `LLMExtractor.extract`.
- For very large documents, split the source into multiple files and run `knowledge create` on each, then merge the bundles by hand.

## "Invalid LLM response for section '<heading>'"

The LLM returned text that could not be parsed as JSON, even after stripping the Markdown fence.

**Fix**

1. The section is logged at `WARNING` level and skipped — extraction continues.
2. If many sections fail, the prompt may be poorly suited to your model. Try a different `--model` value.
3. If the failure is consistent for a specific heading, edit the source document to remove the offending heading.

## "Concept id must be a kebab-case slug"

The LLM returned an `id` field that does not match `^[a-z][a-z0-9-]*$`.

**Fix**

- The concept is logged at `WARNING` level and skipped. Extraction continues.
- If a particular model keeps producing invalid IDs, lower the `temperature` (the SDK uses `0.0` by default; customise `LLMExtractor` directly if you need to change it).

## "Knowledge.update destroyed my hand-edits"

`update` is destructive — see [Refresh a bundle after the source changes](tutorials/update-bundle.md). Hand-edited files in the bundle are overwritten.

**Fix**

The cleanest fix is prevention: keep hand-edits in a separate directory or in a separate branch and merge them in after `update`. If you have already lost edits, look in the git history if the bundle was tracked, or restore from your editor's autosave.

## "Concept ID was not found in the bundle"

`knowledge remove` reported one or more unknown IDs (exit code `2`). This is a warning, not a hard failure — typos in the requested IDs are visible to operators without aborting the whole command.

**Fix**

1. Open the bundle's `index.md` and find the correct IDs.
2. Re-run `knowledge remove` with the corrected IDs.

## "ModuleNotFoundError: No module named 'knowledge'"

The package is not installed in the active Python environment.

**Fix**

```bash
pip install knowledge
```

If you are working from a checkout of the repository:

```bash
pip install -e ".[dev]"
```

## "litellm.AuthenticationError"

The API key for your provider is missing or invalid.

**Fix**

```bash
export OPENAI_API_KEY=sk-...
```

or for Anthropic:

```bash
export ANTHROPIC_API_KEY=sk-ant-...
```

For local Ollama, ensure the daemon is running and `OLLAMA_HOST` points at it.

## Getting more help

- Read the [FAQ](faq.md) for high-level questions.
- Open an issue at <https://github.com/sachncs/knowledge/issues> — include the command you ran, the full output, and the version (`python -c "import knowledge; print(knowledge.__version__)"`).
- For security issues, follow [SECURITY.md](https://github.com/sachncs/knowledge/blob/master/SECURITY.md) — **do not** open a public issue.
