---
id: default-iterators-operators
title: "Default Iterators and Operators"
type: concept
tags: [iterators, operators, containers]

---

## Summary

Use default iterators and operators for types that support them.

**Decision:** Use default iterators and operators for types that support them (lists, dictionaries, files). Prefer these to methods that return lists, except do not mutate a container while iterating over it.

```python
# Yes:
for key in adict: ...
if obj in alist: ...
for line in afile: ...
for k, v in adict.items(): ...

# No:
for key in adict.keys(): ...
for line in afile.readlines(): ...
```

*[Google Python Style Guide](https://google.github.io/styleguide/pyguide.html)*
