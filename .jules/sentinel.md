## 2025-05-22 - Regex Trailing Newline Bypass
**Vulnerability:** Input validation using the `$` anchor in Python's `re` module can be bypassed by a trailing newline, as `$` matches the end of the string OR the position before a trailing newline.
**Learning:** This behavior is specific to certain regex engines, including Python's. It can lead to argument injection or path traversal if the validated string is later used in shell commands or file operations.
**Prevention:** Always use `\Z` instead of `$` for absolute end-of-string matching in Python regexes when validating security-sensitive input.
