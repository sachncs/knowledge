---
id: parentheses
title: "Parentheses"
type: concept
tags: [parentheses, formatting]

---

## Summary

Use parentheses sparingly.

It is fine, though not required, to use parentheses around tuples. Do not use them in return statements or conditional statements unless using parentheses for implied line continuation or to indicate a tuple.

```python
# Yes:
if foo: bar()
while x: x = bar()
if x and y: bar()
if not x: bar()
onesie = (foo,)
return foo
return spam, beans
return (spam, beans)

# No:
if (x): bar()
if not(x): bar()
return (foo)
```

*[Google Python Style Guide](https://google.github.io/styleguide/pyguide.html)*
