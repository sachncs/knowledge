---
id: typing-default-values
title: "Default Values"
type: concept
tags: [type-annotations, default-values, formatting]

---

## Summary

Use spaces around the = only for arguments that have both a type annotation and a default value.

```python
# Yes:
def func(a: int = 0) -> int:

# No:
def func(a:int=0) -> int:
```

*[Google Python Style Guide](https://google.github.io/styleguide/pyguide.html)*
