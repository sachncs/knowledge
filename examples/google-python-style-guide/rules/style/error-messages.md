---
id: error-messages
title: "Error Messages"
type: concept
tags: [error-messages, exceptions, logging]

---

## Summary

Error messages should precisely match the actual error condition, clearly identify interpolated pieces, and allow simple automated processing.

```python
# Yes:
if not 0 <= p <= 1:
    raise ValueError(f'Not a probability: {p=}')

try:
    os.rmdir(workdir)
except OSError as error:
    logging.warning('Could not remove directory (reason: %r): %r', error, workdir)
```

*[Google Python Style Guide](https://google.github.io/styleguide/pyguide.html)*
