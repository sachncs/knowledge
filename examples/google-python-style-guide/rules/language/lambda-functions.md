---
id: lambda-functions
title: "Lambda Functions"
type: concept
tags: [lambdas, anonymous-functions]

---

## Summary

Okay for one-liners. Prefer generator expressions over map() or filter() with a lambda.

**Decision:** Lambdas are allowed. If the code spans multiple lines or is longer than 60-80 chars, define it as a regular nested function.

For common operations like multiplication, use the `operator` module instead of lambda functions. For example, prefer `operator.mul` to `lambda x, y: x * y`.

*[Google Python Style Guide](https://google.github.io/styleguide/pyguide.html)*
