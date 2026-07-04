---
id: naming-conventions
title: "Naming Conventions"
type: concept
tags: [naming, conventions, underscore]

---

## Summary

Internal means internal to a module or protected/private within a class.

- Prepending a single underscore (`_`) protects module variables and functions.
- Prepending a double underscore (`__`) invokes name mangling; we discourage its use.
- Place related classes and top-level functions together in a module.
- Use CapWords for class names, but lower_with_under.py for module names.
- New unit test files follow PEP 8 compliant lower_with_under method names.

*[Google Python Style Guide](https://google.github.io/styleguide/pyguide.html)*
