---
id: test-modules
title: "Test Modules"
type: concept
tags: [tests, documentation, test-modules]

---

## Summary

Module-level docstrings for test files are not required. They should be included only when there is additional information.

Docstrings that do not provide any new information should not be used (e.g. `"""Tests for foo.bar."""`).

```python
"""This blaze test uses golden files.

You can update those files by running
`blaze run //foo/bar:foo_test -- --update_golden_files` from the `google3`
directory.
"""
```

*[Google Python Style Guide](https://google.github.io/styleguide/pyguide.html)*
