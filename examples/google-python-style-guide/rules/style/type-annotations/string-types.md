---
id: string-types
title: "String Types"
type: concept
tags: [string-types, type-annotations, str, bytes]

---

## Summary

Do not use typing.Text in new code. Use str for string/text data and bytes for binary data.

```python
def deals_with_text_data(x: str) -> str:
def deals_with_binary_data(x: bytes) -> bytes:
```

*[Google Python Style Guide](https://google.github.io/styleguide/pyguide.html)*
