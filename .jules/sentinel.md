## 2026-03-29 - Regex End-of-String Anchors for Path Safety
**Vulnerability:** Newline injection in regex validators.
**Learning:** In Python's `re` module, `$` matches the end of the string OR before a newline at the end of the string. This allows malicious inputs like `repo-name\n` to pass validation if the pattern is `^[a-zA-Z0-9-]*$`.
**Prevention:** Always use `\Z` instead of `$` when validating inputs that will be used in file paths or shell commands to ensure the pattern matches the absolute end of the string.
