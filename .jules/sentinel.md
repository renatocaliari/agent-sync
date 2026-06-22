## 2025-05-15 - Regex Newline Injection Bypass
**Vulnerability:** Regex patterns using `$` instead of `\Z` allowed trailing newlines to bypass validation.
**Learning:** In Python's `re` module, `$` matches at the end of the string OR just before a newline at the end of the string. This can be exploited to inject arguments if the validated string is passed to a shell command.
**Prevention:** Always use `\Z` for absolute end-of-string matching in security-critical regex validators.

## 2025-05-16 - Broken Publish Exclusion Logic
**Vulnerability:** The `_ignore_func` in `git_publish.py` used brittle logic that failed to match most default ignore patterns (e.g., `sessions`, `cache`, `models.json`), potentially leaking sensitive data during public publishing.
**Learning:** Custom implementations of glob-like matching are error-prone. The previous logic only handled `*.` and `.` prefixes, missing bare directory names and other common patterns.
**Prevention:** Use standard library functions like `fnmatch.fnmatchcase` for robust pattern matching against file/directory names.
