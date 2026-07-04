---
id: main
title: "Main"
type: concept
tags: [main, executables, entry-point]

---

## Summary

If a file is meant to be used as an executable, its main functionality should be in a main() function.

Code should always check `if __name__ == '__main__'` before executing the main program, so that it is not executed when the module is imported.

When using absl, use `app.run`:

```python
from absl import app

def main(argv: Sequence[str]):
    ...

if __name__ == '__main__':
    app.run(main)
```

*[Google Python Style Guide](https://google.github.io/styleguide/pyguide.html)*
