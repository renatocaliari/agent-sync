## 2025-05-15 - Regex Newline Injection Bypass
**Vulnerability:** Regex patterns using `$` instead of `\Z` allowed trailing newlines to bypass validation.
**Learning:** In Python's `re` module, `$` matches at the end of the string OR just before a newline at the end of the string. This can be exploited to inject arguments if the validated string is passed to a shell command.
**Prevention:** Always use `\Z` for absolute end-of-string matching in security-critical regex validators.

## 2025-05-16 - Symlink Content Leakage during File Sync
**Vulnerability:** `shutil.copytree` and `shutil.copy2` follow symbolic links by default. If a user-controlled directory (like a skill or agent config) contains a symlink pointing to a sensitive file (e.g., `~/.ssh/id_rsa`), the sync/backup process will read and copy the *content* of that sensitive file into the backup repository.
**Learning:** `pathlib.Path.is_file()` and `is_dir()` return `True` for symlinks pointing to those types. Standard `shutil` copy operations will follow these links unless explicitly instructed otherwise.
**Prevention:** Always use `symlinks=True` in `shutil.copytree()` and `follow_symlinks=False` in `shutil.copy2()` when handling files from potentially untrusted or user-defined directory structures to ensure links are preserved as links and not traversed.
