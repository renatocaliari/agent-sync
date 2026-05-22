## 2025-05-15 - Regex Newline Injection Bypass
**Vulnerability:** Regex patterns using `$` instead of `\Z` allowed trailing newlines to bypass validation.
**Learning:** In Python's `re` module, `$` matches at the end of the string OR just before a newline at the end of the string. This can be exploited to inject arguments if the validated string is passed to a shell command.
**Prevention:** Always use `\Z` for absolute end-of-string matching in security-critical regex validators.

## 2025-05-16 - Symlink Content Leakage in Publishing
**Vulnerability:** The publishing flow used `shutil.copytree` and `shutil.copy2` with default settings, which follow symbolic links. This could lead to sensitive files outside the intended skill or agent directory being copied into a public repository.
**Learning:** `pathlib.Path.is_file()` and `is_dir()` return `True` for symlinks pointing to files/dirs. Default `shutil` behavior dereferences these links, leading to accidental "Information Disclosure".
**Prevention:** Always use `symlinks=True` with `shutil.copytree` and `follow_symlinks=False` with `shutil.copy2` when handling user-controlled or agent-generated directories to ensure symlinks are preserved as links.
