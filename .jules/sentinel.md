## 2025-05-15 - Regex Newline Injection Bypass
**Vulnerability:** Regex patterns using `$` instead of `\Z` allowed trailing newlines to bypass validation.
**Learning:** In Python's `re` module, `$` matches at the end of the string OR just before a newline at the end of the string. This can be exploited to inject arguments if the validated string is passed to a shell command.
**Prevention:** Always use `\Z` for absolute end-of-string matching in security-critical regex validators.

## 2025-05-16 - Restricted File/Directory Permissions Pattern
**Vulnerability:** Configuration and state files containing sensitive metadata (repo URLs, sync state) were created with default system permissions (often 0o644), potentially exposing them to other users on multi-user systems.
**Learning:** Python's `open()` and `Path.mkdir()` use system `umask`, which is often too permissive for sensitive data.
**Prevention:** Use a centralized security utility (`secure_open` and `ensure_secure_dir`) that leverages `os.open` with specific mode flags and explicit `os.chmod` to enforce 0o600 for files and 0o700 for directories.
