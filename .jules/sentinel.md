## 2025-05-15 - Regex Newline Injection Bypass
**Vulnerability:** Regex patterns using `$` instead of `\Z` allowed trailing newlines to bypass validation.
**Learning:** In Python's `re` module, `$` matches at the end of the string OR just before a newline at the end of the string. This can be exploited to inject arguments if the validated string is passed to a shell command.
**Prevention:** Always use `\Z` for absolute end-of-string matching in security-critical regex validators.

## 2025-05-16 - Symlink Traversal Information Disclosure
**Vulnerability:** Python's `shutil.copytree` and `shutil.copy2` follow symbolic links by default. This allowed sensitive data from outside the intended directories to be leaked if a "skill" contained a symbolic link pointing to a sensitive file or directory (e.g., `~/.ssh`).
**Learning:** Default filesystem operations in many languages follow links. In applications that synchronize or package user-provided directories, this is a common source of Information Disclosure.
**Prevention:** Explicitly set `symlinks=True` in `shutil.copytree` or `follow_symlinks=False` in `shutil.copy2` to ensure the link itself is copied, not its target.
