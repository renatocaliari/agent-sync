## 2025-05-15 - Regex Newline Injection Bypass
**Vulnerability:** Regex patterns using `$` instead of `\Z` allowed trailing newlines to bypass validation.
**Learning:** In Python's `re` module, `$` matches at the end of the string OR just before a newline at the end of the string. This can be exploited to inject arguments if the validated string is passed to a shell command.
**Prevention:** Always use `\Z` for absolute end-of-string matching in security-critical regex validators.

## 2025-05-16 - Atomic 0o600 File Creation
**Vulnerability:** Creating sensitive files and then calling `chmod` creates a race condition where the file is briefly readable by other users.
**Learning:** Python's built-in `open()` function accepts an `opener` parameter. This can be used to call `os.open` with a specific mode (e.g., `0o600`), ensuring the file is created with restricted permissions atomically.
**Prevention:** Use the `secure_open` utility in `src/agent_sync/security.py` for all files containing sensitive configuration or state.
