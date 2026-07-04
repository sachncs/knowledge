---
id: exceptions
title: "Exceptions"
type: concept
tags: [exceptions, error-handling, assert]

---

## Summary

Exceptions are allowed but must be used carefully.

**Decision:**
1. Make use of built-in exception classes when it makes sense (e.g. `ValueError` for programming mistakes).
2. Do not use `assert` statements in place of conditionals or validating preconditions. Asserts must not be critical to application logic. For pytest-based tests, assert is okay.
3. Libraries may define their own exceptions. They must inherit from an existing exception class. Exception names should end in `Error` and should not introduce repetition (`foo.FooError`).
4. Never use catch-all `except:` statements, or catch `Exception` or `StandardError`, unless re-raising or creating an isolation point.
5. Minimize the amount of code in a try/except block.
6. Use the `finally` clause to execute code whether or not an exception is raised.

```python
def connect_to_next_port(self, minimum: int) -> int:
    if minimum < 1024:
        raise ValueError(f'Min. port must be at least 1024, not {minimum}.')
    port = self._find_next_open_port(minimum)
    if port is None:
        raise ConnectionError(
            f'Could not connect to service on port {minimum} or higher.')
    assert port >= minimum, (
        f'Unexpected port {port} when minimum was {minimum}.')
    return port
```

*[Google Python Style Guide](https://google.github.io/styleguide/pyguide.html)*
