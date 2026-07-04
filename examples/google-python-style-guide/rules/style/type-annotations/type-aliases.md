---
id: type-aliases
title: "Type Aliases"
type: concept
tags: [type-aliases, type-annotations]

---

## Summary

You can declare aliases of complex types. The name should be CapWorded.

If the alias is used only in this module, it should be `_Private`. Note that the `: TypeAlias` annotation is only supported in versions 3.10+.

```python
from typing import TypeAlias
_LossAndGradient: TypeAlias = tuple[tf.Tensor, tf.Tensor]
```

*[Google Python Style Guide](https://google.github.io/styleguide/pyguide.html)*
