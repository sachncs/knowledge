---
id: properties
title: "Properties"
type: concept
tags: [properties, decorators, encapsulation]

---

## Summary

Properties may be used to control getting or setting attributes that require trivial computations or logic.

**Decision:** Properties are allowed, but should only be used when necessary and match expectations of typical attribute access.

Using a property to simply get and set an internal attribute isn't allowed (make the attribute public instead). Using a property to control attribute access or calculate a trivially derived value is allowed.

Properties should be created with the `@property` decorator. Manually implementing a property descriptor is considered a power feature.

Inheritance with properties can be non-obvious. Do not use properties to implement computations a subclass may want to override and extend.

*[Google Python Style Guide](https://google.github.io/styleguide/pyguide.html)*
