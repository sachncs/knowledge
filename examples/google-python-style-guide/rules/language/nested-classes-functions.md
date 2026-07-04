---
id: nested-classes-functions
title: "Nested/Local/Inner Classes and Functions"
type: concept
tags: [nested, closures, inner-classes]

---

## Summary

Nested local functions or classes are fine when used to close over a local variable.

**Decision:** Avoid nested functions or classes except when closing over a local value other than `self` or `cls`. Do not nest a function just to hide it from users of a module. Instead, prefix its name with `_` at the module level so that it can still be accessed by tests.

*[Google Python Style Guide](https://google.github.io/styleguide/pyguide.html)*
