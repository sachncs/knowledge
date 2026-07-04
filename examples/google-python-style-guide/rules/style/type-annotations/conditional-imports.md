---
id: conditional-imports
title: "Conditional Imports"
type: concept
tags: [conditional-imports, type-checking]

---

## Summary

Use conditional imports only when additional imports needed for type checking must be avoided at runtime.

Imports needed only for type annotations can be placed within an `if TYPE_CHECKING:` block.

```python
import typing
if typing.TYPE_CHECKING:
    import sketch
def f(x: "sketch.Sketch"): ...
```

*[Google Python Style Guide](https://google.github.io/styleguide/pyguide.html)*
