---
id: modern-python
title: "Modern Python: from __future__ imports"
type: concept
tags: [future-imports, compatibility, modern-python]

---

## Summary

New language version semantic changes may be gated behind a special future import.

**Decision:** Use of `from __future__ import` statements is encouraged. It allows a source file to start using more modern Python syntax features today. Once you no longer need to run on a version where the features are hidden, feel free to remove those lines.

In code that may execute on versions as old as 3.5 rather than >= 3.7, import `generator_stop`.

Do not remove these imports until you are confident the code is only ever used in a sufficiently modern environment.

*[Google Python Style Guide](https://google.github.io/styleguide/pyguide.html)*
