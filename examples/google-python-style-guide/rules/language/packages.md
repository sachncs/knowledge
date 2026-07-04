---
id: packages
title: "Packages"
type: concept
tags: [packages, imports, modules]

---

## Summary

Import each module using the full pathname location of the module.

All new code should import each module by its full package name.

**Decision:**
```python
# Yes:
import absl.flags
from doctor.who import jodie

# No:
import jodie  # Unclear what module the author wanted
```

The directory the main binary is located in should not be assumed to be in sys.path.

*[Google Python Style Guide](https://google.github.io/styleguide/pyguide.html)*
