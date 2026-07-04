---
id: none-type
title: "NoneType"
type: concept
tags: [nonetype, optional, type-annotations]

---

## Summary

NoneType is a first class type. If an argument can be None, it has to be declared.

Use `X | None` instead of implicit. Earlier versions of type checkers allowed `a: str = None` to be interpreted as `a: str | None = None`, but that is no longer the preferred behavior.

```python
# Yes:
def modern_or_union(a: str | int | None, b: str | None = None) -> str:
def union_optional(a: Union[str, int, None], b: Optional[str] = None) -> str:

# No:
def implicit_optional(a: str = None) -> str:
```

*[Google Python Style Guide](https://google.github.io/styleguide/pyguide.html)*
