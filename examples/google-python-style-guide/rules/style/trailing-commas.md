---
id: trailing-commas
title: "Trailing Commas"
type: concept
tags: [trailing-commas, formatting]

---

## Summary

Trailing commas are recommended only when the closing container token is not on the same line as the final element.

Trailing commas in sequences of items are recommended only when the closing container token `]`, `)`, or `}` does not appear on the same line as the final element, as well as for tuples with a single element.

The presence of a trailing comma is also used as a hint to auto-formatters (Black/Pyink) to format the container to one item per line.

```python
# Yes:
golomb3 = [0, 1, 3]
golomb4 = [
    0,
    1,
    4,
    6,
]

# No:
golomb4 = [
    0,
    1,
    4,
    6,]
```

*[Google Python Style Guide](https://google.github.io/styleguide/pyguide.html)*
