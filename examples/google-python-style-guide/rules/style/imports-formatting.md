---
id: imports-formatting
title: "Imports Formatting"
type: concept
tags: [imports, formatting, organization]

---

## Summary

Imports should be on separate lines. They are always put at the top of the file.

**Groups (from most generic to least generic):**
1. Python future import statements
2. Python standard library imports
3. Third-party module or package imports
4. Code repository sub-package imports

Within each grouping, imports should be sorted lexicographically, ignoring case, according to each module's full package path. Code may optionally place a blank line between import sections.

*[Google Python Style Guide](https://google.github.io/styleguide/pyguide.html)*
