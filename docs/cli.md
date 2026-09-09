# CLI reference

The `knowledge` command-line tool creates, updates, and removes OKF bundles. Every command accepts a shared `--model` flag; some commands also accept command-specific options.

## Synopsis

```text
knowledge [--model <model>] <command> [options]
```

## Global options

| Option | Description | Default |
|--------|-------------|---------|
| `--model <model>` | A [litellm](https://litellm.ai)-compatible model identifier. The provider is selected from the model string. | `gpt-4o` |

The `--model` flag is accepted by every subcommand for consistency, but `knowledge remove` does not invoke the LLM.

## Commands

### `create`

Extract concepts from a source and write a new OKF bundle to a directory.

```text
knowledge create [--validate] <input> <output>
```

| Argument | Description |
|----------|-------------|
| `input`  | URL (`http://` or `https://`) or local file path. |
| `output` | Directory to write the bundle into. Created if it does not exist. |

| Option | Description |
|--------|-------------|
| `--validate` | Run `BundleSerializer.validate()` after writing and report any structural issues. |

**Example**

```bash
knowledge create https://google.github.io/styleguide/pyguide.html ./pyguide
```

**Exit codes**

| Code | Meaning |
|------|---------|
| `0` | Bundle written successfully. |
| `1` | Source could not be fetched or read. |

### `update`

Re-extract concepts from a source and overwrite an existing bundle.

```text
knowledge update <input> <bundle_dir>
```

!!! warning "Destructive"

    `update` performs a **complete replacement** of the bundle directory. Concepts present in the old bundle but missing from the new extraction are removed. If you have hand-edited any concept file, back it up before running `update`.

**Example**

```bash
knowledge update https://google.github.io/styleguide/pyguide.html ./pyguide
```

### `remove`

Delete one or more concepts from an existing bundle by ID.

```text
knowledge remove <concept_id>... <bundle_dir>
```

| Argument | Description |
|----------|-------------|
| `concept_id` | One or more concept IDs to remove. Repeatable. |
| `bundle_dir` | Bundle directory to modify. |

**Example**

```bash
knowledge remove outdated-section deprecated-topic ./pyguide
```

**Exit codes**

| Code | Meaning |
|------|---------|
| `0` | Every requested concept ID was found and removed. |
| `2` | At least one requested concept ID was not in the bundle. The CLI prints a warning listing every missing ID. |
| `1` | The bundle directory could not be read or written. |

## Environment variables

| Variable | Purpose | Default |
|----------|---------|---------|
| `OPENAI_API_KEY` | OpenAI authentication | — |
| `ANTHROPIC_API_KEY` | Anthropic authentication | — |
| `OLLAMA_HOST` | Ollama base URL | `http://localhost:11434` |
| `KNOWLEDGE_MAX_BODY_SIZE` | Maximum HTTP response body in bytes | `52428800` (50 MiB) |
| `KNOWLEDGE_REQUEST_TIMEOUT` | HTTP request timeout in seconds | `30` |
| `KNOWLEDGE_MAX_RETRIES` | Retries for transient failures | `3` |

See [Configuration](configuration.md) for the full list.

## Exit code summary

| Code | Meaning |
|------|---------|
| `0` | Success. |
| `1` | Unrecoverable error (fetch failure, write failure, etc.). |
| `2` | Partial success: at least one requested concept ID was unknown. |

## Logging

The CLI writes log output to **stderr** at `INFO` level using the `%(message)s` format. This keeps stdout clean for future pipe-friendly output. Pass `--quiet` (planned) to suppress progress messages in scripts.
