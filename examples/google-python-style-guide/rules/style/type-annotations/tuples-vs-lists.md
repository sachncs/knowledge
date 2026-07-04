---
id: tuples-vs-lists
title: "Tuples vs Lists"
type: concept
tags: [tuples, lists, type-annotations]

---

## Summary

Typed lists can only contain objects of a single type. Typed tuples can have a single repeated type or a set number of elements.

```python
a: list[int] = [1, 2, 3]
b: tuple[int, ...] = (1, 2, 3)
c: tuple[int, str, float] = (1, "2", 3.5)
```

*[Google Python Style Guide](https://google.github.io/styleguide/pyguide.html)*
