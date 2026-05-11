## 2025-05-15 - Regex Newline Injection Bypass
**Vulnerability:** Regex patterns using `$` instead of `\Z` allowed trailing newlines to bypass validation.
**Learning:** In Python's `re` module, `$` matches at the end of the string OR just before a newline at the end of the string. This can be exploited to inject arguments if the validated string is passed to a shell command.
**Prevention:** Always use `\Z` for absolute end-of-string matching in security-critical regex validators.

## 2025-05-16 - Symlink Data Leakage in File Sync
**Vulnerability:** File synchronization logic followed symbolic links, copying their target content into the repository.
**Learning:** Default behaviors of `shutil.copy2` and `shutil.copytree` follow symlinks. If a user-controlled directory contains a symlink to a sensitive file (e.g., `~/.ssh/id_rsa`), sync operations will leak that file's content into the backup repository.
**Prevention:** Always use `follow_symlinks=False` for `shutil.copy2` and `symlinks=True` for `shutil.copytree` when handling files in user-controlled or agent-managed directories.
