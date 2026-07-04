---
id: function-docs
title: "Functions and Methods"
type: concept
tags: [functions, methods, documentation, docstrings]

---

## Summary

A docstring is mandatory for every function that is part of the public API, has nontrivial size, or has non-obvious logic.

The docstring may be descriptive-style or imperative-style, but consistent within a file.

**Sections:**
- **Args:** List each parameter by name. Description should follow, separated by colon.
- **Returns:** (or **Yields:** for generators) Describe the return value semantics.
- **Raises:** List all exceptions relevant to the interface.

```python
def fetch_smalltable_rows(
    table_handle: smalltable.Table,
    keys: Sequence[bytes | str],
    require_all_keys: bool = False,
) -> Mapping[bytes, tuple[str, ...]]:
    """Fetches rows from a Smalltable.

    Args:
        table_handle: An open smalltable.Table instance.
        keys: A sequence of strings representing the key of each table row.
        require_all_keys: If True only rows with values set for all keys.

    Returns:
        A dict mapping keys to the corresponding table row data.

    Raises:
        IOError: An error occurred accessing the smalltable.
    """
```

*[Google Python Style Guide](https://google.github.io/styleguide/pyguide.html)*
