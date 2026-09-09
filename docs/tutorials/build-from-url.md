# Build a bundle from a URL

This tutorial walks through extracting a public HTML documentation page into an OKF bundle.

## What you will build

A `./pyguide/` directory containing:

```text
pyguide/
├── index.md
├── background.md
├── language-rules.md
├── style-rules.md
└── ...
```

Each `.md` file has YAML frontmatter (`id`, `title`, `type`, `tags`) and a Markdown body summarising one section of the source.

## Before you start

- `knowledge` is installed (`pip install knowledge`).
- Your LLM provider API key is exported (for example `export OPENAI_API_KEY=sk-...`).

## Steps

### 1. Run the extraction

```bash
knowledge create https://google.github.io/styleguide/pyguide.html ./pyguide
```

The CLI:

1. Downloads the page with retries, size limits, and charset detection.
2. Splits the page into sections by `<h1>`–`<h6>` headings.
3. Sends each section to the LLM with a structured prompt.
4. Writes the OKF bundle to `./pyguide/`.

You should see something like:

```text
Creating bundle from pyguide.html...
done (3.4s)
Wrote 66 concepts to ./pyguide
```

### 2. Inspect the bundle

```bash
ls ./pyguide/
# index.md  background.md  language-rules.md  style-rules.md  ...
```

Open `index.md` to see the bundle's root listing:

```markdown
- [Background](background.md)
- [Language Rules](language-rules.md)
- [Style Rules](style-rules.md)
```

Open any concept file, for example `background.md`, to see the YAML frontmatter and the Markdown body:

```markdown
---
id: background
title: "Background"
type: concept
tags: ["guide"]
---

## Background

Python is a dynamic, strongly typed language...
```

### 3. Validate the bundle

```bash
knowledge create --validate https://google.github.io/styleguide/pyguide.html ./pyguide
```

The CLI runs `BundleSerializer.validate()` and reports any structural issues (missing `index.md`, broken links, orphan files). For a clean bundle you should see `Validation: OK`.

You can also validate directly from Python:

```python
from knowledge.kmd.bundle import BundleSerializer

issues = BundleSerializer().validate("./pyguide")
print("OK" if not issues else issues)
```

### 4. Customise the layout

By default, all concepts are placed in the bundle root. To group concepts by tag into subdirectories, pass a `path_map`:

```python
from knowledge import Knowledge

k = Knowledge(model="gpt-4o", path_map={"guide": "docs/guides"})
k.create_bundle("https://google.github.io/styleguide/pyguide.html", "./pyguide")
```

Concepts tagged `guide` now live under `./pyguide/docs/guides/` instead of the root.

## What you learned

- How to run `knowledge create` against an HTML source.
- How to inspect the resulting bundle structure.
- How to validate the bundle.
- How to use `path_map` to group concepts by tag.

## Next steps

- [Refresh a bundle after the source changes](update-bundle.md) — re-run extraction into the same directory.
- [Curate a bundle by removing concepts](curate-bundle.md) — trim unwanted concepts.
