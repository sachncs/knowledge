---
id: generators
title: "Generators"
type: concept
tags: [generators, yield, iterators]

---

## Summary

Use generators as needed.

**Decision:** Use "Yields:" rather than "Returns:" in the docstring for generator functions. If the generator manages an expensive resource, make sure to force the clean up. A good way is by wrapping the generator with a context manager (PEP-533).

Note: Local variables in the generator will not be garbage collected until the generator is either consumed to exhaustion or itself garbage collected.

*[Google Python Style Guide](https://google.github.io/styleguide/pyguide.html)*
