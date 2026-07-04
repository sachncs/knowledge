---
id: imports
title: "Imports"
type: concept
tags: [imports, modules, namespaces]

---

## Summary

Use import statements for packages and modules only, not for individual types, classes, or functions.

**Decision:**
- Use `import x` for importing packages and modules.
- Use `from x import y` where x is the package prefix and y is the module name.
- Use `from x import y as z` when: two modules named y, y conflicts with a top-level name, y conflicts with a common parameter name, y is inconveniently long, y is too generic.
- Use `import y as z` only when z is a standard abbreviation (e.g. `import numpy as np`).

**Exemptions:** Symbols from `typing`, `collections.abc`, and `typing_extensions` modules are exempt. Redirects from `six.moves` module are exempt.

Do not use relative names in imports. Always use the full package name.

```python
# Yes:
from sound.effects import echo
echo.EchoFilter(input, output, delay=0.7, atten=4)
```

*[Google Python Style Guide](https://google.github.io/styleguide/pyguide.html)*
