---
id: block-inline-comments
title: "Block and Inline Comments"
type: concept
tags: [comments, inline-comments, documentation]

---

## Summary

The final place to have comments is in tricky parts of the code.

Complicated operations get a few lines of comments before the operations commence. Non-obvious ones get comments at the end of the line.

Comments should start at least 2 spaces away from the code with `#` followed by at least one space before the text.

Never describe the code. Assume the reader knows Python.

```python
# We use a weighted dictionary search to find out where i is in
# the array.
if i & (i-1) == 0:  # True if i is 0 or a power of 2.
```

*[Google Python Style Guide](https://google.github.io/styleguide/pyguide.html)*
