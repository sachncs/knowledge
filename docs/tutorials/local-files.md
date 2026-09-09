# Run the SDK without network access

`knowledge` works equally well on local files and on text already in memory. This tutorial covers both cases.

## Before you start

- `knowledge` is installed.
- You have a Markdown or HTML file on disk, or a string you want to extract from.

## Option A: Extract from a local file

```bash
knowledge create ./my-document.html ./my-bundle
```

`./my-document.html` is read as UTF-8. The bundle directory is created if it does not exist.

### Combine with `--model` and `--validate`

```bash
knowledge --model claude-3-opus-20240229 create --validate ./my-document.md ./my-bundle
```

### Use Python for finer control

```python
from knowledge import Knowledge

k = Knowledge(model="gpt-4o")

# Read a local file directly
raw = Knowledge.read_source("./my-document.html")

# Extract from the in-memory text
graph = k.create("./my-document.html")
```

`Knowledge.create` accepts the file path and handles the read internally; use `Knowledge.read_source` only when you need the raw text for another purpose.

## Option B: Extract from text already in memory

When the source is a string you have already loaded (from a database, a queue, a previous step in a pipeline), use `LLMExtractor` directly:

```python
from knowledge.llm.extractor import LLMExtractor

text = """
## Installation

Run `pip install knowledge`.

## Configuration

Set `OPENAI_API_KEY` before invoking the CLI.
"""

graph = LLMExtractor(model="gpt-4o").extract(text)
for cid, concept in graph.concepts.items():
    print(f"{cid}: {concept.name}")
```

This skips the URL or file read entirely. The extractor splits by headings, sends each section to the LLM, and returns a `KnowledgeGraph`.

## Option C: Write an OKF bundle from a KnowledgeGraph

Once you have a `KnowledgeGraph`, write it to disk with `BundleSerializer`:

```python
from knowledge.kmd.bundle import BundleSerializer
from knowledge.llm.extractor import LLMExtractor
from knowledge.models import Concept, KnowledgeGraph

graph = LLMExtractor().extract("# Hello\n\nWorld.")
# ... mutate graph as needed ...
graph = graph.add_concept(Concept(id="extra", name="Extra", description="..."))

BundleSerializer().serialize(graph, "./my-bundle")
```

`BundleSerializer` does not call the LLM or perform network I/O — it is a pure filesystem operation.

## When to use which

| Situation | Use |
|-----------|-----|
| Source is a URL | `knowledge create <url> <dir>` |
| Source is a local file | `knowledge create <path> <dir>` |
| Source is a string you already loaded | `LLMExtractor(model=...).extract(text)` |
| You have a graph and want to write it | `BundleSerializer().serialize(graph, dir)` |

## What you learned

- `knowledge` works on local files and in-memory text, not only URLs.
- `LLMExtractor.extract` takes a string; the SDK's `Knowledge.create` adds URL and file reading.
- `BundleSerializer.serialize` is a pure filesystem operation with no LLM or network calls.
