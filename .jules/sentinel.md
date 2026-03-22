# Sentinel Security Journal

## 2025-05-15 - [HIGH] Path Traversal in Skills Deletion
**Vulnerability:** User-provided skill names were used directly in `Path` joining operations in `SkillsDeleter.delete_skills`, allowing for arbitrary file deletion via path traversal (e.g., `../../etc/passwd`).
**Learning:** Python's `pathlib.Path` joining operator `/` resets the path if the second argument is absolute (starts with `/`), which is a common but dangerous behavior when handling unsanitized user input.
**Prevention:** Always validate user-provided strings used in file paths against a strict whitelist (e.g., `^[a-zA-Z0-9][a-zA-Z0-9._-]*\Z`) before path construction.

## 2025-05-15 - [MEDIUM] Regex Newline Injection Bypass
**Vulnerability:** Existing validators for GitHub URLs and repository names used the `$` anchor in regex patterns, which in Python can match before a trailing newline, potentially allowing malicious payloads to bypass validation.
**Learning:** In Python's `re` module, `$` matches the end of the string OR the position just before a newline at the end. `\Z` matches ONLY the absolute end of the string.
**Prevention:** Use `\Z` instead of `$` for strict end-of-string matching in security-critical validation logic.
