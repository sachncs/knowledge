---
id: conditional-expressions
title: "Conditional Expressions"
type: concept
tags: [conditional-expressions, ternary, readability]

---

## Summary

Okay for simple cases.

**Decision:** Each portion must fit on one line: true-expression, if-expression, else-expression. Use a complete if statement when things get more complicated.

```python
# Yes:
one_line = 'yes' if predicate(value) else 'no'
slightly_split = ('yes' if predicate(value)
                  else 'no, nein, nyet')

# No:
bad_line_breaking = ('yes' if predicate(value) else
                     'no')
```

*[Google Python Style Guide](https://google.github.io/styleguide/pyguide.html)*
