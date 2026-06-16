## 2025-05-15 - Regex Newline Injection Bypass
**Vulnerability:** Regex patterns using `$` instead of `\Z` allowed trailing newlines to bypass validation.
**Learning:** In Python's `re` module, `$` matches at the end of the string OR just before a newline at the end of the string. This can be exploited to inject arguments if the validated string is passed to a shell command.
**Prevention:** Always use `\Z` for absolute end-of-string matching in security-critical regex validators.

## 2025-05-22 - Symlink Content Leakage in File Operations
**Vulnerability:** `shutil.copytree` and `shutil.copy2` follow symbolic links by default, copying the content of the target file instead of the link. This can lead to sensitive information leakage if a user-controlled directory (like a skill or agent config) contains a symlink pointing to sensitive files outside the expected scope (e.g., `/etc/passwd`, private keys).
**Learning:** Default behavior of standard library file operations may have security implications in applications that process user-controlled structures. Path traversal isn't the only risk; dereferencing symlinks can also leak out-of-bounds data.
**Prevention:** Always use `symlinks=True` with `shutil.copytree` and `follow_symlinks=False` with `shutil.copy2` (and similar functions like `shutil.move` or `shutil.chown` if applicable) when handling directories that might contain untrusted or user-defined symlinks.
