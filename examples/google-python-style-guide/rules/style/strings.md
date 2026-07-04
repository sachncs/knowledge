---
id: strings
title: "Strings"
type: concept
tags: [strings, formatting, f-strings]

---

## Summary

Use an f-string, the % operator, or the format method for formatting strings.

Avoid using the `+` and `+=` operators to accumulate a string within a loop (can lead to quadratic runtime). Add each substring to a list and `''.join` the list after the loop terminates, or write each substring to an `io.StringIO` buffer.

Be consistent with your choice of string quote character within a file. Pick `'` or `"` and stick with it.

Prefer `"""` for multi-line strings rather than `'''`. Docstrings must use `"""` regardless.

*[Google Python Style Guide](https://google.github.io/styleguide/pyguide.html)*
