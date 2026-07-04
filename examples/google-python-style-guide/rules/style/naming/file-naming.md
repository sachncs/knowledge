---
id: file-naming
title: "File Naming"
type: concept
tags: [file-naming, extensions]

---

## Summary

Python filenames must have a .py extension and must not contain dashes.

This allows them to be imported and unittested. If you want an executable to be accessible without the extension, use a symbolic link or a simple bash wrapper containing `exec "$0.py" "$@"`.

*[Google Python Style Guide](https://google.github.io/styleguide/pyguide.html)*
