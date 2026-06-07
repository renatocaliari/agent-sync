## 2025-05-15 - Regex Newline Injection Bypass
**Vulnerability:** Regex patterns using `$` instead of `\Z` allowed trailing newlines to bypass validation.
**Learning:** In Python's `re` module, `$` matches at the end of the string OR just before a newline at the end of the string. This can be exploited to inject arguments if the validated string is passed to a shell command.
**Prevention:** Always use `\Z` for absolute end-of-string matching in security-critical regex validators.

## 2025-05-20 - Content Leakage via Symlink Following
**Vulnerability:** `shutil.copytree` and `shutil.copy2` follow symlinks by default, copying the content of the target file/directory.
**Learning:** If a user-controlled directory (like a skills hub) contains a symlink to sensitive files (e.g., `~/.ssh/id_rsa`), standard copy operations will leak the *content* of those files into the destination repository.
**Prevention:** Always use `symlinks=True` in `shutil.copytree` and `follow_symlinks=False` in `shutil.copy2` when processing directories that might contain user-created symlinks.
