## 2025-05-15 - Regex Newline Injection Bypass
**Vulnerability:** Regex patterns using `$` instead of `\Z` allowed trailing newlines to bypass validation.
**Learning:** In Python's `re` module, `$` matches at the end of the string OR just before a newline at the end of the string. This can be exploited to inject arguments if the validated string is passed to a shell command.
**Prevention:** Always use `\Z` for absolute end-of-string matching in security-critical regex validators.

## 2025-05-16 - Symlink Content Leakage in File Sync
**Vulnerability:** Application followed symbolic links during sync and publish operations, potentially leaking sensitive files (e.g., SSH keys) if a user-controlled directory contained a symlink.
**Learning:** `pathlib.Path.is_file()` and `is_dir()` return `True` for symlinks. Standard `shutil` operations like `copy2` and `copytree` follow links by default, "flattening" them into regular files/directories at the destination and exposing the target's content.
**Prevention:** Always use `follow_symlinks=False` for `shutil.copy2` and `symlinks=True` for `shutil.copytree` when processing user-provided or potentially sensitive directories. Additionally, explicitly check `is_symlink()` to skip or handle links before reading file content.
