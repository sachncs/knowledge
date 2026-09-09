# Tutorials

These guided walkthroughs solve one specific job end-to-end. Read them in any order.

## Available tutorials

| Tutorial | What you build |
|----------|----------------|
| [Build a bundle from a URL](build-from-url.md) | Extract a public HTML documentation page into an OKF bundle. |
| [Refresh a bundle after the source changes](update-bundle.md) | Re-run extraction into an existing bundle directory. |
| [Curate a bundle by removing concepts](curate-bundle.md) | Trim unwanted concepts from a bundle. |
| [Run the SDK without network access](local-files.md) | Extract from a local file or from text already in memory. |

## Before you start

Every tutorial assumes you have:

1. Installed `knowledge` from PyPI (`pip install knowledge`).
2. Set the API key for your LLM provider (`export OPENAI_API_KEY=sk-...`).
3. Verified the install with `knowledge --help`.

If any of those steps are missing, start at [Getting started](../getting-started.md).
