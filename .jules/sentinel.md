## 2025-05-14 - Path Traversal in Deletion Logic
**Vulnerability:** The `skills delete` command accepted unsanitized skill names that were joined with the skills hub directory. Python's `Path / absolute_path` resets the path to the absolute one, allowing deletion of arbitrary files.
**Learning:** Even when using `pathlib`, joining paths with user input is dangerous if the input is an absolute path or contains `..` segments.
**Prevention:** Always validate user-provided file/directory names against a strict whitelist (regex) and use `.resolve()` combined with `.relative_to()` to ensure the resulting path remains within the intended boundary.

## 2025-05-14 - Newline Injection in Regex Validation
**Vulnerability:** Regex patterns for repository names and GitHub URLs used `$` for end-of-string matching, which in Python can match before a trailing newline, allowing injection bypasses.
**Learning:** Python's `$` behavior in `re` module is a common source of security gaps when validating inputs for shell commands or file paths.
**Prevention:** Use `\Z` instead of `$` in Python regexes for absolute end-of-string matching.
