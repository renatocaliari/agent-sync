## 2025-05-22 - [Regex Newline Injection Bypass]
**Vulnerability:** Regex patterns using `$` instead of `\Z` for end-of-string matching.
**Learning:** In Python's `re` module, `$` matches at the end of the string OR just before a newline at the end of the string. This allows malicious input like `repo-name\n` to pass validation if the regex is `^[a-z]+$`.
**Prevention:** Always use `\Z` instead of `$` in security-critical validators to ensure the pattern matches the absolute end of the string.

## 2025-05-22 - [Path Traversal in Skill Deletion]
**Vulnerability:** Use of unsanitized user input in file path construction for deletion.
**Learning:** Even with basic validation, `pathlib.Path` joining can be tricky. If a user provides `..`, they can traverse up from the intended directory. Also, if they provide an absolute path as the second argument to `/`, it resets the entire path.
**Prevention:** Implement strict input validation (alphanumeric only) AND defense-in-depth by resolving paths and verifying they are children of the intended base directory using `path.relative_to(base)`.
