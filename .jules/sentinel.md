## 2025-05-15 - [Path Traversal in Skills Deletion]
**Vulnerability:** The `SkillsDeleter.delete_skills` method was susceptible to path traversal because it joined user-provided skill names directly with base directories without prior validation or path resolution checks.
**Learning:** Python's `pathlib.Path` joining operator `/` resets the path if the second argument is an absolute path (starts with `/`), and it does not automatically block `..` sequences.
**Prevention:** Always validate user-provided strings used in path construction against a strict regex (e.g., `validate_skill_name`). Additionally, use `.resolve()` and verify that the resulting path is still a child of the intended base directory using `.relative_to()` (which raises `ValueError` on escape).

## 2025-05-15 - [Newline Injection in Regex Validation]
**Vulnerability:** Existing regex validators used `$` to anchor the end of strings, which in Python's `re` module can match before a trailing newline, potentially allowing injection in scenarios where the validated string is passed to shell commands.
**Learning:** `$` matches the end of the string or just before a newline at the end of the string. `\Z` matches ONLY the absolute end of the string.
**Prevention:** Use `\Z` instead of `$` for absolute end-of-string matching in security-critical regex validations.
