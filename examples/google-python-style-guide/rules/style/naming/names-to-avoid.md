---
id: names-to-avoid
title: "Names to Avoid"
type: concept
tags: [naming, anti-patterns]

---

## Summary

Single character names, dashes, dunder names, offensive terms, and type-including names should be avoided.

**Allowed single-character names:**
- Counters or iterators (e.g. `i`, `j`, `k`, `v`)
- `e` as an exception identifier in `try/except`
- `f` as a file handle in `with` statements
- Private type variables with no constraints (`_T`, `_P`)
- Names matching established notation in a reference paper

Also avoid: dashes in package/module names, `__double_leading_and_trailing_underscore__` names (reserved by Python), offensive terms, and names that needlessly include the type of the variable.

*[Google Python Style Guide](https://google.github.io/styleguide/pyguide.html)*
