# Getting started

This page walks you from a clean install to a working bundle in about five minutes.

## Prerequisites

`knowledge` requires **Python 3.12 or later**. Check your version:

```bash
python --version
```

You also need an API key for the LLM provider you plan to use. For local models served by [Ollama](https://ollama.com) you do not need an API key, but you do need the Ollama daemon running locally.

## Install

### From PyPI

```bash
pip install knowledge
```

### From source

```bash
git clone https://github.com/sachncs/knowledge.git
cd knowledge
pip install -e .
```

### With dev dependencies

Install `pytest`, `ruff`, `mypy`, and `vulture` for local development and verification:

```bash
pip install -e ".[dev]"
```

### With documentation dependencies

Install `mkdocs`, `mkdocstrings`, and `mkdocs-material` if you want to build the docs site locally:

```bash
pip install -e ".[docs]"
```

## Configure an LLM provider

`knowledge` uses [litellm](https://litellm.ai) to route prompts to the right provider. The provider is selected by the model string you pass; authentication is handled through environment variables.

=== "OpenAI"

    ```bash
    export OPENAI_API_KEY=sk-...
    knowledge --model gpt-4o create https://example.com/docs.html ./out
    ```

=== "Anthropic"

    ```bash
    export ANTHROPIC_API_KEY=sk-ant-...
    knowledge --model claude-3-opus-20240229 create https://example.com/docs.html ./out
    ```

=== "Ollama (local)"

    ```bash
    # Ollama runs locally — no API key required.
    ollama pull llama3
    knowledge --model ollama/llama3 create https://example.com/docs.html ./out
    ```

=== "vLLM"

    ```bash
    # Point litellm at your vLLM endpoint via OPENAI_API_BASE.
    export OPENAI_API_BASE=http://localhost:8000/v1
    export OPENAI_API_KEY=not-required
    knowledge --model open-mistral-nemo create https://example.com/docs.html ./out
    ```

See [Configuration](configuration.md) for every supported environment variable.

## Create your first bundle

```bash
knowledge create https://google.github.io/styleguide/pyguide.html ./pyguide
```

This command:

1. Downloads the Google Python Style Guide HTML page.
2. Splits it into sections by `<h1>`–`<h6>` headings.
3. Sends each section to the LLM with a structured prompt.
4. Writes an OKF v0.1 bundle to `./pyguide/`.

Inspect the result:

```bash
ls ./pyguide/
# index.md  background.md  language-rules.md  style-rules.md  ...
```

Open `index.md` to see the bundle's root index; open any concept file to see its YAML frontmatter and Markdown body.

## Use the Python API

```python
from knowledge import Knowledge

k = Knowledge(model="gpt-4o")

# Return an in-memory KnowledgeGraph
graph = k.create("https://google.github.io/styleguide/pyguide.html")
for cid, concept in graph.concepts.items():
    print(f"{cid}: {concept.name}")

# Write the same content to disk as an OKF bundle
k.create_bundle("https://google.github.io/styleguide/pyguide.html", "./pyguide")
```

`Knowledge` is the single entry point for `create`, `create_bundle`, `update`, and `remove`. See [Python API](api.md) for the full surface.

## Refresh an existing bundle

If the source document has changed, re-run the extraction into the same directory:

```bash
knowledge update https://google.github.io/styleguide/pyguide.html ./pyguide
```

!!! warning "Updates are destructive"

    `knowledge update` overwrites every file in the bundle directory. Any concepts present in the old bundle but missing from the new extraction are removed. If you have edited a concept file by hand, back it up first or use `knowledge remove` after `update` to prune unwanted concepts.

## Curate a bundle

```bash
knowledge remove outdated-section deprecated-topic ./pyguide
```

If any requested concept ID is not in the bundle, the CLI prints a warning listing the missing IDs and exits with status code `2`. Exit code `0` means every ID was found and removed.

## Next steps

- Walk through a guided workflow in [Tutorials](tutorials/index.md).
- Read the [Architecture](architecture.md) page to learn how the layers fit together.
- Browse the [Python API](api.md) or [CLI reference](cli.md).
