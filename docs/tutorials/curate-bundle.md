# Curate a bundle by removing concepts

After extraction, you usually want to drop a few concepts — duplicates, low-value sections, or material that is now out of date. `knowledge remove` lets you do that without re-running the LLM.

## Before you start

- A bundle exists at `./pyguide/`.
- You know which concept IDs you want to remove. If you are not sure, open `index.md` and find the IDs you want to drop.

## What `remove` does

`remove` reads every concept file from the bundle, removes the specified IDs from the in-memory `KnowledgeGraph`, and writes the result back to the same directory. Unknown IDs are not a hard failure — they are reported as a warning and the CLI exits with status code `2`.

## Steps

### 1. List the IDs you want to remove

Open `./pyguide/index.md` and look at the list of concept links. Each link target is the concept ID.

For example, if `index.md` contains:

```markdown
- [Background](background.md)
- [Language Rules](language-rules.md)
- [Style Rules](style-rules.md)
- [Parting Words](parting-words.md)
```

And you want to drop `parting-words.md`, the ID is `parting-words`.

### 2. Run `remove`

```bash
knowledge remove parting-words ./pyguide
```

Expected output:

```text
Removing concepts [parting-words]...
done (0.2s)
Wrote 65 concepts to ./pyguide
```

Exit code `0` means the ID was found.

### 3. Remove multiple IDs

Pass as many IDs as you need:

```bash
knowledge remove parting-words deprecated-section old-api ./pyguide
```

If every ID exists, exit code is `0`. If any ID is missing, exit code is `2` and the CLI lists the unknown IDs:

```text
WARNING: 1 requested concept ID(s) were not found in the bundle:
  - deprecated-section
```

### 4. Validate

After curation, run validation to confirm the bundle is still well-formed:

```bash
knowledge create --validate https://google.github.io/styleguide/pyguide.html ./pyguide
```

You should see `Validation: OK`.

## Detecting typos in scripts

Because `remove` exits with `2` when an ID is missing, you can guard scripts with `set -e` or check `$?` directly:

```bash
if knowledge remove parting-words ./pyguide; then
  echo "OK"
else
  case $? in
    2) echo "Some IDs were unknown — check the warnings above." ;;
    *) echo "Removal failed." ;;
  esac
fi
```

## What you learned

- How to look up concept IDs from `index.md`.
- How to remove one or many concepts in a single command.
- How to detect unknown concept IDs (CLI exit code `2`).
- How to validate the bundle after curation.

## Next steps

- [Run the SDK without network access](local-files.md) — extract from local files instead of URLs.
