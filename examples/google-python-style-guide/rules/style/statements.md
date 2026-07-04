---
id: statements
title: "Statements"
type: concept
tags: [statements, formatting]

---

## Summary

Generally only one statement per line.

You may put the result of a test on the same line as the test only if the entire statement fits on one line. You can never do so with `try`/`except` since they can't both fit on the same line. You can only do so with `if` if there is no `else`.

```python
# Yes:
if foo: bar(foo)

# No:
if foo: bar(foo)
else:   baz(foo)
```

*[Google Python Style Guide](https://google.github.io/styleguide/pyguide.html)*
