---
id: lint
title: "Lint"
type: concept
tags: [lint, pylint, static-analysis]

---

## Summary

Run pylint over your code using the provided pylintrc.

pylint is a tool for finding bugs and style problems in Python source code. It finds problems typically caught by a compiler for less dynamic languages.

**Decision:** Make sure you run pylint on your code. Suppress warnings if they are inappropriate using `# pylint: disable=warning-name` line-level comments. Prefer `pylint: disable` over the deprecated `pylint: disable-msg`.

Unused argument warnings can be suppressed by deleting the variables at the beginning of the function with a comment explaining why. Using `_` as identifier or prefixing with `unused_` is allowed but no longer encouraged.

Google-specific warnings start with `g-`. If the reason for suppression is not clear from the symbolic name, add an explanation.

```python
def do_PUT(self):  # pylint: disable=invalid-name
    ...

def viking_cafe_order(spam: str, beans: str, eggs: str | None = None) -> str:
    del beans, eggs  # Unused by vikings.
    return spam + spam + spam
```

## References

- https://google.github.io/styleguide/pylintrc
- https://google.github.io/styleguide/pyguide.html

*[Google Python Style Guide](https://google.github.io/styleguide/pyguide.html)*
