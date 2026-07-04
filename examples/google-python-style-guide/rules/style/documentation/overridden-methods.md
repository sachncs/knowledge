---
id: overridden-methods
title: "Overridden Methods"
type: concept
tags: [overrides, inheritance, documentation]

---

## Summary

A method that overrides a method from a base class does not need a docstring if decorated with @override.

If the overriding method's behavior materially refines the base contract or has additional side effects, a docstring with at least those differences is required.

```python
from typing_extensions import override

class Child(Parent):
    @override
    def do_something(self):
        pass  # No docstring needed
```

*[Google Python Style Guide](https://google.github.io/styleguide/pyguide.html)*
