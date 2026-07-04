---
id: typing-imports
title: "Imports For Typing"
type: concept
tags: [typing-imports, type-annotations]

---

## Summary

Always import typing/collections.abc symbols themselves. Multiple imports on one line are allowed.

```python
from collections.abc import Mapping, Sequence
from typing import Any, Generic, cast, TYPE_CHECKING
```

When annotating function signatures, prefer abstract container types like `collections.abc.Sequence` over concrete types like `list`.

*[Google Python Style Guide](https://google.github.io/styleguide/pyguide.html)*
