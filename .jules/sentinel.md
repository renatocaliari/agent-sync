## 2025-05-15 - [Regex Newline Injection]
**Vulnerability:** Newline characters in user-provided strings could bypass regex validation when using `$` to match the end of the line.
**Learning:** In Python's `re` module, `$` matches the end of the string OR the position just before a newline at the end of the string. This allows malicious input like `name\n--injection` to partially match a pattern intended for the whole string.
**Prevention:** Always use `\Z` instead of `$` in regex patterns for absolute end-of-string matching in security-critical validations.
