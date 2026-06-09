## 2025-05-15 - Regex Newline Injection Bypass
**Vulnerability:** Regex patterns using `$` instead of `\Z` allowed trailing newlines to bypass validation.
**Learning:** In Python's `re` module, `$` matches at the end of the string OR just before a newline at the end of the string. This can be exploited to inject arguments if the validated string is passed to a shell command.
**Prevention:** Always use `\Z` for absolute end-of-string matching in security-critical regex validators.

## 2025-05-16 - Symlink Content Leakage in File Operations
**Vulnerability:** `shutil.copytree` and `shutil.copy2` followed symbolic links by default, potentially leaking sensitive system files if an attacker placed a symlink in a user-controlled directory.
**Learning:** Default Python file operations often follow symlinks, which is dangerous when processing directories that can be influenced by users or external sources.
**Prevention:** Always use `symlinks=True` in `shutil.copytree` and `follow_symlinks=False` in `shutil.copy2` when working with potentially untrusted directory structures to ensure links are preserved, not traversed.
