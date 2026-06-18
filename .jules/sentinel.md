## 2025-05-15 - Regex Newline Injection Bypass
**Vulnerability:** Regex patterns using `$` instead of `\Z` allowed trailing newlines to bypass validation.
**Learning:** In Python's `re` module, `$` matches at the end of the string OR just before a newline at the end of the string. This can be exploited to inject arguments if the validated string is passed to a shell command.
**Prevention:** Always use `\Z` for absolute end-of-string matching in security-critical regex validators.

## 2025-05-20 - Broken Exclusion Logic in Git Publish
**Vulnerability:** The `_ignore_func` in `git_publish.py` failed to ignore most patterns in `DEFAULT_IGNORE_PATTERNS` (like `sessions/`, `cache/`, `models.json`) because it only handled patterns starting with `.` or `*`.
**Learning:** Manual implementation of glob/pattern matching is error-prone. The previous logic was overly restrictive in how it interpreted patterns, leading to potential leakage of sensitive session data and local configurations during the publish process.
**Prevention:** Use standard library functions like `fnmatch.fnmatch` for robust and idiomatic pattern matching when implementing file exclusion or inclusion filters.
