---
id: comprehensions
title: "Comprehensions & Generator Expressions"
type: concept
tags: [comprehensions, generator-expressions, readability]

---

## Summary

Okay to use for simple cases.

**Decision:** Comprehensions are allowed, however multiple `for` clauses or filter expressions are not permitted. Optimize for readability, not conciseness.

```python
# Yes:
result = [mapping_expr for value in iterable if filter_expr]
result = [is_valid(metric={'key': value})
          for value in interesting_iterable
          if a_longer_filter_expression(value)]

# No:
result = [(x, y) for x in range(10) for y in range(5) if x * y > 10]
```

*[Google Python Style Guide](https://google.github.io/styleguide/pyguide.html)*
