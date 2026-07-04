---
id: type-annotated-code
title: "Type Annotated Code"
type: concept
tags: [type-annotations, type-hints, pytype]

---

## Summary

You can annotate Python code with type hints. Type-check the code at build time.

**Decision:** You are strongly encouraged to enable Python type analysis when updating code. When adding or modifying public APIs, include type annotations and enable checking via pytype in the build system.

In most cases, when feasible, type annotations are in source files. For third-party or extension modules, annotations can be in stub `.pyi` files.

*[Google Python Style Guide](https://google.github.io/styleguide/pyguide.html)*
