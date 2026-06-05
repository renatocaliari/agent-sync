## 2025-05-15 - Regex Newline Injection Bypass
**Vulnerability:** Regex patterns using `$` instead of `\Z` allowed trailing newlines to bypass validation.
**Learning:** In Python's `re` module, `$` matches at the end of the string OR just before a newline at the end of the string. This can be exploited to inject arguments if the validated string is passed to a shell command.
**Prevention:** Always use `\Z` for absolute end-of-string matching in security-critical regex validators.

## 2025-06-12 - Symlink Content Leakage in File Operations
**Vulnerability:** Using `shutil.copytree` or `shutil.copy2` on user-controlled directories without disabling symlink following can lead to sensitive file leakage.
**Learning:** `pathlib.Path.is_file()` and `is_dir()` return `True` for symlinks pointing to those types. Standard `shutil` operations will follow these links, potentially copying files from outside the intended scope (e.g., `/etc/passwd`) into public repositories.
**Prevention:** Always use `symlinks=True` in `shutil.copytree` and `follow_symlinks=False` in `shutil.copy2` when processing user-controlled content. Explicitly skip symlinks during discovery if they are not intended to be supported.
