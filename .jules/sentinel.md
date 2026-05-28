## 2025-05-15 - Regex Newline Injection Bypass
**Vulnerability:** Regex patterns using `$` instead of `\Z` allowed trailing newlines to bypass validation.
**Learning:** In Python's `re` module, `$` matches at the end of the string OR just before a newline at the end of the string. This can be exploited to inject arguments if the validated string is passed to a shell command.
**Prevention:** Always use `\Z` for absolute end-of-string matching in security-critical regex validators.

## 2025-05-22 - Symlink Content Leakage via shutil
**Vulnerability:** Default `shutil.copytree` and `shutil.copy2` follow symbolic links, copying the target file's content instead of the link.
**Learning:** If a user-controlled directory (like skills or agent configs) contains a symlink to a sensitive file (e.g., `~/.ssh/id_rsa`), the content is leaked into the sync repository or publish target.
**Prevention:** Always use `symlinks=True` for `shutil.copytree` and `follow_symlinks=False` for `shutil.copy2` when handling user-provided files.
