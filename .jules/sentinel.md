## 2025-05-15 - Regex Newline Injection Bypass
**Vulnerability:** Regex patterns using `$` instead of `\Z` allowed trailing newlines to bypass validation.
**Learning:** In Python's `re` module, `$` matches at the end of the string OR just before a newline at the end of the string. This can be exploited to inject arguments if the validated string is passed to a shell command.
**Prevention:** Always use `\Z` for absolute end-of-string matching in security-critical regex validators.

## 2025-05-18 - Symlink Content Leakage in Publishing and Sync
**Vulnerability:** `shutil.copytree` and `shutil.copy2` followed symbolic links by default, potentially leaking sensitive data from outside the intended scope (e.g., SSH keys, credentials) into public repositories or backups.
**Learning:** Python's `shutil` operations follow symlinks unless explicitly told otherwise. `pathlib.Path.is_file()` also returns `True` for symlinks pointing to files, leading to accidental content reads when copying "files".
**Prevention:** Always set `symlinks=True` in `shutil.copytree` and `follow_symlinks=False` in `shutil.copy2` (and related functions) when handling directories that might contain user-provided symlinks.
