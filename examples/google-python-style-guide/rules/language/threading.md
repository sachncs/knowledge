---
id: threading
title: "Threading"
type: concept
tags: [threading, concurrency, atomicity]

---

## Summary

Do not rely on the atomicity of built-in types.

While Python's built-in data types such as dictionaries appear to have atomic operations, there are corner cases where they aren't atomic (e.g. if `__hash__` or `__eq__` are implemented as Python methods).

Use the `queue.Queue` data type as the preferred way to communicate data between threads. Otherwise, use the `threading` module and its locking primitives. Prefer condition variables and `threading.Condition` instead of using lower-level locks.

*[Google Python Style Guide](https://google.github.io/styleguide/pyguide.html)*
