---
id: logging
title: "Logging"
type: concept
tags: [logging, string-formatting]

---

## Summary

For logging functions that expect a pattern-string, always call them with a string literal (not an f-string!) as their first argument.

Some logging implementations collect the unexpanded pattern-string as a queryable field. It also prevents spending time rendering a message that no logger is configured to output.

```python
# Yes:
logger.info('TensorFlow Version is: %s', tf.__version__)
logging.info('Current $PAGER is: %s', os.getenv('PAGER', default=''))

# No:
logging.info(f'Cannot write to home directory, $HOME={homedir!r}')
```

*[Google Python Style Guide](https://google.github.io/styleguide/pyguide.html)*
