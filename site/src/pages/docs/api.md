---
layout: ../../layouts/DocsLayout.astro
title: Python API
description: Public Python classes, methods, data models, and exceptions in knowledge.
---

# Python API

The Python API is centered on `Knowledge`, which reads a source and creates a linked Markdown bundle.

## `Knowledge`

```python
from knowledge import Knowledge

knowledge = Knowledge(model="gpt-4o")
graph = knowledge.create("https://example.com/guide.html")
count = knowledge.create_bundle("https://example.com/guide.html", "./guide-bundle")
```

### Constructor

```python
Knowledge(model: str = DEFAULT_MODEL, path_map: dict[str, str] | None = None)
```

`model` selects the LiteLLM model/provider. `path_map` optionally maps concept tags to bundle subdirectories.

### Methods

| Method | Result | Description |
| --- | --- | --- |
| `create(source)` | `KnowledgeGraph` | Read a URL, file path, or text source and extract concepts into a graph. |
| `create_bundle(source, output_dir, path_map=None)` | `int` | Extract concepts and write an OKF bundle; returns the number of concepts written. |
| `update(source, bundle_dir, path_map=None)` | `int` | Rebuild the bundle from the source, replacing its generated contents. |
| `remove(concept_ids, bundle_dir, path_map=None)` | `int` | Remove the named concepts and rewrite the bundle; returns the number removed. |
| `remove_with_unknowns(concept_ids, bundle_dir, path_map=None)` | `tuple[int, list[str]]` | Remove known IDs and return the unknown IDs alongside the removal count. |
| `read_source(source)` | `str` | Static helper that reads a URL, local path, or supplied text. |

`source` accepts an HTTP(S) URL, a local file path, or text. Bundle update rewrites the generated bundle, so copy it first if you need to preserve manual edits.

## Data models

### `Concept`

A concept has an `id`, `name`, optional `description`, and a list of `tags`. IDs use lowercase letters, digits, and hyphens, and must start with a letter (for example, `install-python`).

### `KnowledgeGraph`

A graph stores concepts by ID. `add_concept` and `remove_concept` return updated graph values, leaving the original graph unchanged.

## Bundle serializer

`BundleSerializer(path_map=None)` writes a graph to the OKF v0.1 directory format. Its `serialize(graph, output_dir)` method returns the concept count. `validate(output_dir)` returns validation messages, while `find_path(tags)` and `dir_title(path)` support tag-based placement and directory indexes.

## Source fetching

`fetch_url(url)` retrieves HTTP or HTTPS content with retries and a 50 MiB response limit. Invalid URLs, network failures, and extraction errors are reported with `FetchError` or the common `KnowledgeError` base exception.
