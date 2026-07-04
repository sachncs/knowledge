---
id: generics
title: "Generics"
type: concept
tags: [generics, type-annotations]

---

## Summary

Prefer to specify type parameters for generic types in a parameter list.

Otherwise, the generics' parameters will be assumed to be `Any`. If the best type parameter is `Any`, make it explicit (but consider whether `TypeVar` might be more appropriate).

```python
# Yes:
def get_names(employee_ids: Sequence[int]) -> Mapping[int, str]:

# No:
def get_names(employee_ids: Sequence) -> Mapping:
```

*[Google Python Style Guide](https://google.github.io/styleguide/pyguide.html)*
