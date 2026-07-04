---
id: class-docs
title: "Classes"
type: concept
tags: [classes, documentation, docstrings]

---

## Summary

Classes should have a docstring below the class definition describing the class.

Public attributes, excluding properties, should be documented in an `Attributes` section.

All class docstrings should start with a one-line summary that describes what the class instance represents. Subclasses of `Exception` should describe what the exception represents, not the context.

```python
class SampleClass:
    """Summary of class here.

    Attributes:
        likes_spam: A boolean indicating if we like SPAM or not.
        eggs: An integer count of the eggs we have laid.
    """

class OutOfCheeseError(Exception):
    """No more cheese is available."""
```

*[Google Python Style Guide](https://google.github.io/styleguide/pyguide.html)*
