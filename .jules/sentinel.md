## 2025-05-22 - [Regex Newline Injection & Path Traversal]
**Vulnerability:** Regex patterns using `$` can be bypassed by appending a newline (`\n`) because Python's `re.match` (and others) may match before the newline. Also, user-provided identifiers (like skill names) used in file paths can lead to path traversal if not strictly validated.
**Learning:** Python regexes require `\Z` for absolute end-of-string matching. Input validation for identifiers used in file system operations must be centralized and strict (allowlist approach).
**Prevention:** Always use `\Z` instead of `$` in regex validation patterns. Validate all user-provided strings before using them to construct file paths or execute commands.
