## 2025-05-15 - Regex Newline Injection Bypass
**Vulnerability:** Regex patterns using `$` instead of `\Z` allowed trailing newlines to bypass validation.
**Learning:** In Python's `re` module, `$` matches at the end of the string OR just before a newline at the end of the string. This can be exploited to inject arguments if the validated string is passed to a shell command.
**Prevention:** Always use `\Z` for absolute end-of-string matching in security-critical regex validators.

## 2026-05-18 - Symlink Content Leakage in Publishing
**Vulnerability:** Use of `shutil.copytree` and `shutil.copy2` without explicitly disabling symlink following leads to content leakage. Symlinks pointing to files outside the intended directory are resolved, and their content is copied into the staging area for public publishing.
**Learning:** Default behavior of `shutil` functions is often to follow symlinks. In security-sensitive operations like publishing to public repositories, this can accidentally expose private files (e.g., `~/.ssh/id_rsa`) if a symlink exists in the source directory.
**Prevention:** Always use `symlinks=True` in `shutil.copytree` and `follow_symlinks=False` in `shutil.copy2` (or `shutil.copytree`'s `copy_function`) when staging files for public distribution.
