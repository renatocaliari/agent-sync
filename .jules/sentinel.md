## 2025-05-15 - Regex Newline Injection Bypass
**Vulnerability:** Regex patterns using `$` instead of `\Z` allowed trailing newlines to bypass validation.
**Learning:** In Python's `re` module, `$` matches at the end of the string OR just before a newline at the end of the string. This can be exploited to inject arguments if the validated string is passed to a shell command.
**Prevention:** Always use `\Z` for absolute end-of-string matching in security-critical regex validators.

## 2026-05-12 - Symlink Content Leakage in Recursive Copy
**Vulnerability:** `shutil.copytree` and `shutil.copy2` follow symbolic links by default when the source itself is a symlink. This allowed "skill" directories that were actually symlinks to external sensitive folders (like `~/.ssh` or `~/Documents`) to be fully copied into the staging area for publishing or syncing.
**Learning:** `pathlib.Path.is_dir()` returns `True` for symlinks pointing to directories, leading developers to use `shutil.copytree`, which then follows the link and copies the entire target directory's content.
**Prevention:** Always use `symlinks=True` in `shutil.copytree` and `follow_symlinks=False` in `shutil.copy2` when handling user-controlled directories. Additionally, explicitly skip top-level symlinks when performing security-sensitive recursive operations.
