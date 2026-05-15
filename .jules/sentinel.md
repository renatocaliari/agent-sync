## 2025-05-15 - Regex Newline Injection Bypass
**Vulnerability:** Regex patterns using `$` instead of `\Z` allowed trailing newlines to bypass validation.
**Learning:** In Python's `re` module, `$` matches at the end of the string OR just before a newline at the end of the string. This can be exploited to inject arguments if the validated string is passed to a shell command.
**Prevention:** Always use `\Z` for absolute end-of-string matching in security-critical regex validators.

## 2025-05-16 - Content Leakage via Symlink Following
**Vulnerability:** `shutil.copy2` and `shutil.copytree` followed symbolic links by default, potentially copying sensitive file content from outside the intended directories into public repositories.
**Learning:** `pathlib.Path.is_file()` returns `True` for symlinks to files, and `shutil`'s default behavior follows these links. This is dangerous when scanning user-controlled directories like `~/.agents/skills/`.
**Prevention:** Always use `is_symlink()` to skip links during discovery, and explicitly set `follow_symlinks=False` in `shutil.copy2` or `symlinks=True` in `shutil.copytree` to handle links safely.
