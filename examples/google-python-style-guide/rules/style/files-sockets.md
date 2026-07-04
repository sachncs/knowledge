---
id: files-sockets
title: "Files, Sockets, and similar Stateful Resources"
type: concept
tags: [files, sockets, resource-management, context-managers]

---

## Summary

Explicitly close files and sockets when done with them.

The preferred way to manage files and similar resources is using the `with` statement. For file-like objects that do not support the `with` statement, use `contextlib.closing()`.

In rare cases where context-based resource management is infeasible, code documentation must explain clearly how resource lifetime is managed.

*[Google Python Style Guide](https://google.github.io/styleguide/pyguide.html)*
