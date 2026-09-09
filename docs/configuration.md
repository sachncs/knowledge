# Configuration

`knowledge` is configured through a small set of environment variables. Most users only need to set the API key for their LLM provider; everything else has a sensible default.

## LLM provider configuration

The model is selected by the model string passed to `--model` or `Knowledge(model=...)`. Authentication uses provider-specific environment variables, which litellm reads directly.

### OpenAI

| Variable | Required | Example |
|----------|----------|---------|
| `OPENAI_API_KEY` | Yes | `sk-...` |
| `OPENAI_API_BASE` | No | `https://api.openai.com/v1` |

```bash
export OPENAI_API_KEY=sk-...
knowledge --model gpt-4o create https://example.com/docs.html ./out
```

### Anthropic

| Variable | Required | Example |
|----------|----------|---------|
| `ANTHROPIC_API_KEY` | Yes | `sk-ant-...` |

```bash
export ANTHROPIC_API_KEY=sk-ant-...
knowledge --model claude-3-opus-20240229 create https://example.com/docs.html ./out
```

### Google Gemini

| Variable | Required | Example |
|----------|----------|---------|
| `GEMINI_API_KEY` | Yes | `AIza...` |

```bash
export GEMINI_API_KEY=AIza...
knowledge --model gemini/gemini-1.5-pro create https://example.com/docs.html ./out
```

### Ollama (local)

| Variable | Required | Example |
|----------|----------|---------|
| `OLLAMA_HOST` | No | `http://localhost:11434` |

Ollama runs locally, so no API key is required.

```bash
ollama pull llama3
knowledge --model ollama/llama3 create https://example.com/docs.html ./out
```

### vLLM

vLLM exposes an OpenAI-compatible endpoint. Point litellm at it with `OPENAI_API_BASE` and any non-empty `OPENAI_API_KEY`.

```bash
export OPENAI_API_BASE=http://localhost:8000/v1
export OPENAI_API_KEY=not-required
knowledge --model open-mistral-nemo create https://example.com/docs.html ./out
```

## HTTP client configuration

These variables control the resilience behaviour of `fetch_url`.

| Variable | Default | Purpose |
|----------|---------|---------|
| `KNOWLEDGE_MAX_BODY_SIZE` | `52428800` (50 MiB) | Reject responses whose `Content-Length` exceeds this value before reading the body. |
| `KNOWLEDGE_REQUEST_TIMEOUT` | `30` | Timeout in seconds for each HTTP request. |
| `KNOWLEDGE_MAX_RETRIES` | `3` | Maximum attempts for transient failures (network errors, HTTP 429, HTTP 5xx). |

The current values are baked into the SDK at build time. To override them today, edit `knowledge/sdk.py` (the constants `MAX_BODY_SIZE`, `REQUEST_TIMEOUT`, `MAX_RETRIES`); runtime overrides are planned for v0.2.

## User-Agent

The HTTP client sends `User-Agent: knowledge-sdk/0.1.0`. If your downstream service filters by User-Agent and you need a custom value, fork the `USER_AGENT` constant in `knowledge/sdk.py`.

## `.env.example`

The repository ships an annotated `.env.example` at the root. Copy it to `.env` and fill in your values:

```bash
cp .env.example .env
```

The CLI does **not** read `.env` automatically. Source the file into your shell, or use a tool like [direnv](https://direnv.net) or [dotenv](https://pypi.org/project/python-dotenv/) to load it before running `knowledge`.

## Recommended workflow

1. Export the API key for the provider you will use.
2. Run `knowledge --model <model> create <url> <out>` to make a small bundle and verify the provider works.
3. Scale up to a larger source.
4. If you hit a transient error, increase `KNOWLEDGE_MAX_RETRIES`. If you hit a body-size error, increase `KNOWLEDGE_MAX_BODY_SIZE`.
