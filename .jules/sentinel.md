# Sentinel's Security Journal 🛡️

## 2025-05-15 - Regex Newline Injection Bypass
**Vulnerability:** Use of `$` in regex patterns for validation allowed bypasses via trailing newlines.
**Learning:** In Python, `re.match` with `$` can match before a trailing newline. `validate_github_url` was vulnerable if a user provided a URL with a newline followed by malicious arguments, although `any(c in url for c in " \n\r\t;'\"<>|")` was also present as a first line of defense.
**Prevention:** Always use `\Z` instead of `$` to ensure the pattern matches the absolute end of the string.

## 2025-05-15 - Path Traversal in Skills Deletion
**Vulnerability:** `SkillsDeleter.delete_skills` accepted arbitrary strings as skill names and used them to construct file paths for `shutil.rmtree`.
**Learning:** Even if the input comes from an interactive TUI, the underlying API should be secure. A malicious caller or a bug in the TUI selection could lead to unintended deletions (e.g., `../../.ssh`).
**Prevention:** Implement and enforce strict input validation for skill names using a whitelist of allowed characters and absolute end-of-string matching.
