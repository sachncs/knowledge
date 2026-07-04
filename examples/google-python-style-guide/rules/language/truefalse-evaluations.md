---
id: truefalse-evaluations
title: "True/False Evaluations"
type: concept
tags: [truthiness, boolean-context, implicit-false]

---

## Summary

Use the implicit false if at all possible.

**Decision:**
- Always use `if foo is None:` to check for None value.
- Never compare a boolean variable to `False` using `==`. Use `if not x:` instead.
- For sequences, use `if seq:` and `if not seq:` rather than `if len(seq):`.
- When handling integers, implicit false may involve more risk than benefit.
- Note that `'0'` (string) evaluates to true.
- Numpy arrays may raise an exception in an implicit boolean context. Prefer `.size` attribute.

```python
# Yes:
if not users:
    print('no users')
if i % 10 == 0:
    self.handle_multiple_of_ten()
def f(x=None):
    if x is None:
        x = []

# No:
if len(users) == 0:
    print('no users')
if not i % 10:
    self.handle_multiple_of_ten()
def f(x=None):
    x = x or []
```

*[Google Python Style Guide](https://google.github.io/styleguide/pyguide.html)*
