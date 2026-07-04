---
id: mathematical-notation
title: "Mathematical Notation"
type: concept
tags: [naming, mathematical-notation]

---

## Summary

For mathematically-heavy code, short variable names matching established notation are preferred.

When using names based on established notation:
1. Cite the source of all naming conventions in a comment or docstring.
2. Prefer PEP8-compliant `descriptive_names` for public APIs.
3. Use a narrowly-scoped `pylint: disable=invalid-name` directive to silence warnings.

*[Google Python Style Guide](https://google.github.io/styleguide/pyguide.html)*
