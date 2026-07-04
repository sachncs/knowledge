---
id: mutable-global-state
title: "Mutable Global State"
type: concept
tags: [global-state, encapsulation, constants]

---

## Summary

Avoid mutable global state.

Module-level values or class attributes that can get mutated during program execution.

**Cons:**
- Breaks encapsulation
- Has the potential to change module behavior during import

**Decision:** Avoid mutable global state. In rare cases where it is warranted, mutable global entities should be declared at the module level or as a class attribute and made internal by prepending `_` to the name. External access must be through public functions or class methods.

Module-level constants are permitted and encouraged. Constants must be named using all caps with underscores.

```python
_MAX_HOLY_HANDGRENADE_COUNT = 3       # Internal constant
SIR_LANCELOTS_FAVORITE_COLOR = "blue" # Public API constant
```

*[Google Python Style Guide](https://google.github.io/styleguide/pyguide.html)*
