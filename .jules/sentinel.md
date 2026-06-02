## 2025-05-15 - Regex Newline Injection Bypass
**Vulnerability:** Regex patterns using `$` instead of `\Z` allowed trailing newlines to bypass validation.
**Learning:** In Python's `re` module, `$` matches at the end of the string OR just before a newline at the end of the string. This can be exploited to inject arguments if the validated string is passed to a shell command.
**Prevention:** Always use `\Z` for absolute end-of-string matching in security-critical regex validators.

## 2025-05-22 - Symlink Content Leakage in File Sync
**Vulnerability:** `shutil.copytree` and `shutil.copy2` follow symlinks by default, causing content of files outside the intended directory to be copied into the sync repository or destination agents.
**Learning:** `pathlib.Path.is_file()` and `is_dir()` return `True` for symlinks pointing to those types. Standard `shutil` copy operations will read the target's content unless explicitly told not to.
**Prevention:** Always use `symlinks=True` in `shutil.copytree` and `follow_symlinks=False` in `shutil.copy2` when handling user-controlled directories that may contain symlinks.
