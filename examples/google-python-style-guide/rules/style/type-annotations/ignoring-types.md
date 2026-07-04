---
id: ignoring-types
title: "Ignoring Types"
type: concept
tags: [type-checking, pytype, ignore]

---

## Summary

You can disable type checking on a line with # type: ignore.

pytype has a disable option for specific errors (similar to lint):

```python
# pytype: disable=attribute-error
```

*[Google Python Style Guide](https://google.github.io/styleguide/pyguide.html)*
