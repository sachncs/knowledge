---
id: circular-dependencies
title: "Circular Dependencies"
type: concept
tags: [circular-dependencies, type-annotations, refactoring]

---

## Summary

Circular dependencies caused by typing are code smells and should be refactored.

Replace modules that create circular dependency imports with `Any`. Set an alias with a meaningful name.

```python
from typing import Any
some_mod = Any  # some_mod.py imports this module.
```

*[Google Python Style Guide](https://google.github.io/styleguide/pyguide.html)*
