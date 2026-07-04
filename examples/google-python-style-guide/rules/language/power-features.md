---
id: power-features
title: "Power Features"
type: concept
tags: [metaclasses, reflection, bytecode]

---

## Summary

Avoid these features.

Python provides features such as custom metaclasses, access to bytecode, on-the-fly compilation, dynamic inheritance, object reparenting, import hacks, reflection, modification of system internals, `__del__` methods.

**Decision:** Avoid these features in your code. Standard library modules that internally use these features are okay to use (e.g. `abc.ABCMeta`, `dataclasses`, `enum`).

*[Google Python Style Guide](https://google.github.io/styleguide/pyguide.html)*
