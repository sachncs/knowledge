---
id: python-language-rules
title: "Python Language Rules"
type: index

---

# Python Language Rules

Section 2 of the Google Python Style Guide covers rules about using Python language features correctly.

These rules define when and how to use specific Python features, evaluating each by definition, pros, cons, and a decision.

## Rules

- [2.1 Lint](lint.md) — Run pylint over your code
- [2.2 Imports](imports.md) — Use import for packages and modules only
- [2.3 Packages](packages.md) — Import each module using the full pathname
- [2.4 Exceptions](exceptions.md) — Exceptions are allowed but must be used carefully
- [2.5 Mutable Global State](mutable-global-state.md) — Avoid mutable global state
- [2.6 Nested/Local/Inner Classes and Functions](nested-classes-functions.md) — Fine when closing over a local variable
- [2.7 Comprehensions & Generator Expressions](comprehensions.md) — Okay for simple cases
- [2.8 Default Iterators and Operators](default-iterators-operators.md) — Use default iterators and operators
- [2.9 Generators](generators.md) — Use generators as needed
- [2.10 Lambda Functions](lambda-functions.md) — Okay for one-liners
- [2.11 Conditional Expressions](conditional-expressions.md) — Okay for simple cases
- [2.12 Default Argument Values](default-argument-values.md) — Okay in most cases
- [2.13 Properties](properties.md) — May be used for trivial computations
- [2.14 True/False Evaluations](truefalse-evaluations.md) — Use implicit false if possible
- [2.16 Lexical Scoping](lexical-scoping.md) — Okay to use
- [2.17 Function and Method Decorators](decorators.md) — Use judiciously
- [2.18 Threading](threading.md) — Do not rely on atomicity of built-in types
- [2.19 Power Features](power-features.md) — Avoid these features
- [2.20 Modern Python](modern-python.md) — Use from __future__ imports
- [2.21 Type Annotated Code](type-annotated-code.md) — Type annotations are encouraged

## References

- [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html)
