## 2025-05-14 - Regex Newline Injection in Python
**Vulnerability:** Trailing newlines `\n` can bypass regex patterns that use `$` for end-of-string matching in Python's `re.match` and `re.search` (without `re.MULTILINE`), because `$` matches both the end of the string and the position just before a trailing newline.
**Learning:** Python's `re` module behavior with `$` is a common pitfall. Using `\Z` instead of `$` ensures the pattern matches only at the absolute end of the string, preventing injection of malicious commands or data via newlines.
**Prevention:** Always use `\Z` for strict end-of-string validation in Python regexes, especially when validating inputs that might be used in shell commands or file paths.
