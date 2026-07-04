---
id: type-variables
title: "Type Variables"
type: concept
tags: [typevar, generics, paramspec]

---

## Summary

TypeVar and ParamSpec are common ways to use generics.

A TypeVar can be constrained. A common predefined type variable is `AnyStr`.

A type variable must have a descriptive name, unless it is not externally visible and not constrained.

```python
_T = TypeVar("_T")
_P = ParamSpec("_P")
AddableType = TypeVar("AddableType", int, float, str)
AnyFunction = TypeVar("AnyFunction", bound=Callable)
```

*[Google Python Style Guide](https://google.github.io/styleguide/pyguide.html)*
