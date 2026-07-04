---
id: default-argument-values
title: "Default Argument Values"
type: concept
tags: [default-arguments, mutable-defaults]

---

## Summary

Okay in most cases.

**Decision:** Do not use mutable objects as default values in the function or method definition. Default arguments are evaluated once at module load time.

```python
# Yes:
def foo(a, b=None):
    if b is None:
        b = []
def foo(a, b: Sequence | None = None):
    if b is None:
        b = []
def foo(a, b: Sequence = ()):  # Empty tuple OK since tuples are immutable
    ...

# No:
def foo(a, b=[]): ...
def foo(a, b=time.time()): ...
def foo(a, b=Mapping = {}): ...
```

*[Google Python Style Guide](https://google.github.io/styleguide/pyguide.html)*
