## 2025-05-15 - [Path Traversal and Regex Bypass Prevention]
**Vulnerability:** User-provided skill names were not validated before being used in file path operations (deletion), potentially allowing path traversal attacks. Additionally, regex patterns used `$` instead of `\Z`, which could be bypassed with trailing newlines.
**Learning:** Python's `re.match` with `$` matches before a trailing newline, which is a common source of validation bypasses. Inputs used in file paths or shell commands must always be strictly validated against a whitelist of allowed characters.
**Prevention:** Use `\Z` for strict end-of-string matching in all security-critical regexes. Always implement and use specific validators for any user-provided string that will be used to construct file paths.
