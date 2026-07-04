---
id: todo-comments
title: "TODO Comments"
type: concept
tags: [todo, comments, technical-debt]

---

## Summary

Use TODO comments for code that is temporary, a short-term solution, or good-enough but not perfect.

A TODO comment begins with the word `TODO` in all caps, a following colon, and a link to a resource that contains the context, ideally a bug reference.

```python
# TODO: crbug.com/192795 - Investigate cpufreq optimizations.
```

Old style (discouraged): `# TODO(crbug.com/192795): Investigate.`

Avoid adding TODOs that refer to an individual or team as the context.

If your TODO is of the form "At a future date do something" include a very specific date or event.

*[Google Python Style Guide](https://google.github.io/styleguide/pyguide.html)*
