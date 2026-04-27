## 2025-05-15 - Regex Newline Injection Bypass
**Vulnerability:** Regex patterns using `$` instead of `\Z` allowed trailing newlines to bypass validation.
**Learning:** In Python's `re` module, `$` matches at the end of the string OR just before a newline at the end of the string. This can be exploited to inject arguments if the validated string is passed to a shell command.
**Prevention:** Always use `\Z` for absolute end-of-string matching in security-critical regex validators.

## 2025-05-15 - Atomic File Permission Enforcement
**Vulnerability:** Files containing sensitive data (configs, state) were created with default system permissions (e.g., 0o644), creating a race condition window before `chmod` could restrict them.
**Learning:** Using `os.chmod` after file creation is non-atomic. In multi-user environments, a malicious process could open the file in the split second between its creation and the permission change.
**Prevention:** Use the `opener` parameter in Python's `open()` function to call `os.open(path, flags, 0o600)` ensuring the file is born with restricted permissions. Combine with `os.fchmod(f.fileno(), 0o600)` for hardening existing files securely.
