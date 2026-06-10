## 2025-05-15 - Regex Newline Injection Bypass
**Vulnerability:** Regex patterns using `$` instead of `\Z` allowed trailing newlines to bypass validation.
**Learning:** In Python's `re` module, `$` matches at the end of the string OR just before a newline at the end of the string. This can be exploited to inject arguments if the validated string is passed to a shell command.
**Prevention:** Always use `\Z` for absolute end-of-string matching in security-critical regex validators.

## 2025-05-16 - Symlink Content Leakage in File Operations
**Vulnerability:** Default `shutil.copytree` and `shutil.copy2` follow symbolic links, potentially leaking sensitive data from outside the intended directory.
**Learning:** `pathlib.Path.is_file()` returns `True` for symlinks pointing to files. Without `symlinks=True` or `follow_symlinks=False`, `shutil` follows these links.
**Prevention:** Always use `symlinks=True` in `shutil.copytree` and `follow_symlinks=False` in `shutil.copy2` when handling user-controlled directories.
