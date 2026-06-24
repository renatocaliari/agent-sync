## 2025-05-15 - Regex Newline Injection Bypass
**Vulnerability:** Regex patterns using `$` instead of `\Z` allowed trailing newlines to bypass validation.
**Learning:** In Python's `re` module, `$` matches at the end of the string OR just before a newline at the end of the string. This can be exploited to inject arguments if the validated string is passed to a shell command.
**Prevention:** Always use `\Z` for absolute end-of-string matching in security-critical regex validators.

## 2025-05-22 - Incomplete File Exclusion in Publish Flow
**Vulnerability:** A custom `_ignore_func` used with `shutil.copytree` failed to exclude sensitive directories and files (e.g., `sessions/`, `models.json`) because it only handled certain pattern prefixes.
**Learning:** Custom file filtering logic for `shutil` operations is error-prone and often fails on edge cases or direct matches.
**Prevention:** Use standard library utilities like `shutil.ignore_patterns` which are well-tested and handle a wider range of glob patterns correctly.
