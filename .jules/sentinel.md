## 2025-05-15 - [Path Traversal and Regex Hardening]
**Vulnerability:** Path traversal in skill deletion and potential newline injection in validators.
**Learning:** `pathlib.Path` joining operator `/` can be dangerous if the second argument is a relative path like `..` or an absolute path (resets the root). Also, Python regex `$` matches before a trailing newline, which can bypass validation if the input is used in shell commands or file operations.
**Prevention:** Use `validate_skill_name` to restrict characters and enforce naming rules. Use `.resolve()` and `.relative_to()` to ensure file operations stay within the intended base directory. Always use `\Z` instead of `$` in regex for strict end-of-string matching.
