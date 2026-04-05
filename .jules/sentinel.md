## 2025-05-15 - [Python Regex End-of-String Bypass]
**Vulnerability:** Input validation bypass using trailing newlines in Python `re` module.
**Learning:** By default, the `$` anchor in Python's `re` module matches at the end of the string OR just before a newline at the end of the string. This allows malicious input like `repo-name\n` to pass a validation intended to match only alphanumeric characters if the pattern is `^[a-zA-Z0-9]+$`.
**Prevention:** Always use `\Z` instead of `$` in Python regex for strict absolute end-of-string matching when validating security-sensitive inputs.
