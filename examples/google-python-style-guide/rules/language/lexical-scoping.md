---
id: lexical-scoping
title: "Lexical Scoping"
type: concept
tags: [scoping, closures, nested-functions]

---

## Summary

Okay to use.

A nested Python function can refer to variables defined in enclosing functions, but cannot assign to them. Variable bindings are resolved using lexical scoping.

Any assignment to a name in a block will cause Python to treat all references to that name as a local variable, even if the use precedes the assignment.

```python
def get_adder(summand1: float) -> Callable[[float], float]:
    def adder(summand2: float) -> float:
        return summand1 + summand2
    return adder
```

*[Google Python Style Guide](https://google.github.io/styleguide/pyguide.html)*
