---
id: decorators
title: "Function and Method Decorators"
type: concept
tags: [decorators, staticmethod, classmethod]

---

## Summary

Use decorators judiciously when there is a clear advantage.

**Decision:**
- Use decorators judiciously when there is a clear advantage.
- A decorator docstring should clearly state that the function is a decorator.
- Write unit tests for decorators.
- Avoid external dependencies in the decorator itself.
- Never use `staticmethod` unless forced to integrate with an existing library.
- Use `classmethod` only when writing a named constructor or a class-specific routine that modifies necessary global state.

*[Google Python Style Guide](https://google.github.io/styleguide/pyguide.html)*
