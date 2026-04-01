## 2025-05-15 - Regex End-of-String Matching with \Z
**Vulnerability:** Use of `$` in regex for input validation allowed for potential newline injection bypasses.
**Learning:** In Python's `re` module, `$` matches either the end of the string or the position just before a trailing newline. This can be exploited to bypass validation if the system later processes the input in a way that is sensitive to newlines (e.g., shell commands or file paths).
**Prevention:** Always use `\Z` instead of `$` when you want to ensure a pattern matches the absolute end of the string, preventing any trailing characters including newlines.
