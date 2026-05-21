## 2025-05-15 - Regex Newline Injection Bypass
**Vulnerability:** Regex patterns using `$` instead of `\Z` allowed trailing newlines to bypass validation.
**Learning:** In Python's `re` module, `$` matches at the end of the string OR just before a newline at the end of the string. This can be exploited to inject arguments if the validated string is passed to a shell command.
**Prevention:** Always use `\Z` for absolute end-of-string matching in security-critical regex validators.

## 2025-05-22 - Information Disclosure via Symbolic Links
**Vulnerability:** `shutil.copytree` and `shutil.copy2` follow symbolic links by default, which can lead to accidental leakage of sensitive files (e.g., `~/.ssh/id_rsa`) when publishing directories to public repositories.
**Learning:** Recursively copying user-controlled directories without explicitly disabling symlink following is dangerous. `pathlib.Path.is_file()` and `is_dir()` also return `True` for symlinks pointing to those types.
**Prevention:** Always use `symlinks=True` for `shutil.copytree` and `follow_symlinks=False` for `shutil.copy2` when handling directories that might contain user-created symbolic links.
