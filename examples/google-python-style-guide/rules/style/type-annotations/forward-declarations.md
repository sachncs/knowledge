---
id: forward-declarations
title: "Forward Declarations"
type: concept
tags: [forward-declarations, type-annotations]

---

## Summary

If you need to use a class name that is not yet defined, use from __future__ import annotations or a string.

```python
from __future__ import annotations

class MyClass:
    def __init__(self, stack: Sequence[MyClass], item: OtherClass) -> None:

class OtherClass:
    ...
```

*[Google Python Style Guide](https://google.github.io/styleguide/pyguide.html)*
