---
id: line-length
title: "Line Length"
type: concept
tags: [line-length, formatting]

---

## Summary

Maximum line length is 80 characters.

**Exceptions:**
- Long import statements
- URLs, pathnames, or long flags in comments
- Long string module-level constants not containing whitespace
- Pylint disable comments

Do not use backslash for explicit line continuation. Use implicit line joining inside parentheses, brackets and braces.

Prefer to break lines at the highest possible syntactic level.

*[Google Python Style Guide](https://google.github.io/styleguide/pyguide.html)*
