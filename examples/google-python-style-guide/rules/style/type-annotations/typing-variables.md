---
id: typing-variables
title: "Typing Variables"
type: concept
tags: [type-annotations, variables, annotated-assignment]

---

## Summary

If an internal variable has a type that is hard or impossible to infer, specify its type with an annotated assignment.

```python
# Annotated assignment:
a: Foo = SomeUndecoratedFunction()

# Type comments (do not add new uses, pre-Python 3.6):
a = SomeUndecoratedFunction()  # type: Foo
```

*[Google Python Style Guide](https://google.github.io/styleguide/pyguide.html)*
