# Getting Started

## Installation

```bash
pip install git+https://github.com/sachncs/knowledge.git
```

Or with dev dependencies:

```bash
pip install -e ".[dev]"
```

## Your First Bundle

### 1. Set up an LLM provider

Export the API key for your provider:

```bash
export OPENAI_API_KEY=sk-...
# or
export ANTHROPIC_API_KEY=sk-ant-...
```

### 2. Create a bundle

```bash
knowledge create https://google.github.io/styleguide/pyguide.html ./pyguide
```

This will:

1. Download the Google Python Style Guide HTML page.
2. Split it into sections by `<h2>` headings.
3. Send each section to the LLM for concept extraction.
4. Write an OKF v0.1 bundle to `./pyguide/`.

### 3. Inspect the output

```bash
ls ./pyguide/
# index.md  background.md  language-rules.md  style-rules.md  ...
```

Each concept file contains YAML frontmatter and the section content in
Markdown.

## Using the Python API

```python
from knowledge import Knowledge

k = Knowledge(model="gpt-4o")

# Get an in-memory KnowledgeGraph
graph = k.create("https://google.github.io/styleguide/pyguide.html")
for cid, concept in graph.concepts.items():
    print(f"{cid}: {concept.name}")

# Write to disk
k.create_bundle("https://google.github.io/styleguide/pyguide.html", "./pyguide")

# Update an existing bundle (re-extract from source)
k.update("https://google.github.io/styleguide/pyguide.html", "./pyguide")

# Remove specific concepts
k.remove(["deprecated-section"], "./pyguide")
```

## Next Steps

- [Architecture Guide](architecture.md)
- [CLI Reference](../README.md#quick-start)
- [FAQ](faq.md)
