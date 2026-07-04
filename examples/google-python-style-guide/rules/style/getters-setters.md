---
id: getters-setters
title: "Getters and Setters"
type: concept
tags: [getters, setters, accessors, encapsulation]

---

## Summary

Getter and setter functions should be used when they provide a meaningful role or behavior.

If a pair of getters/setters simply read and write an internal attribute, the internal attribute should be made public instead. Properties may be an option when simple logic is needed.

Getters and setters should follow the Naming guidelines: `get_foo()` and `set_foo()`.

If the past behavior allowed access through a property, do not bind the new getter/setter functions to the property. Any code still attempting to access the variable by the old method should break visibly.

*[Google Python Style Guide](https://google.github.io/styleguide/pyguide.html)*
