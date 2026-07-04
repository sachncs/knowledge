---
id: shebang-line
title: "Shebang Line"
type: concept
tags: [shebang, executables]

---

## Summary

Most .py files do not need to start with a #! line.

Start the main file of a program with `#!/usr/bin/env python3` (to support virtualenvs) or `#!/usr/bin/python3` per PEP-394. This line is used by the kernel to find the Python interpreter, but is ignored by Python when importing modules.

*[Google Python Style Guide](https://google.github.io/styleguide/pyguide.html)*
