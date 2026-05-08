## 2025-05-15 - Regex Newline Injection Bypass
**Vulnerability:** Regex patterns using `$` instead of `\Z` allowed trailing newlines to bypass validation.
**Learning:** In Python's `re` module, `$` matches at the end of the string OR just before a newline at the end of the string. This can be exploited to inject arguments if the validated string is passed to a shell command.
**Prevention:** Always use `\Z` for absolute end-of-string matching in security-critical regex validators.
## 2025-05-16 - Symlink Following in Directory Copying
**Vulnerability:**  and  follow symbolic links by default, which can lead to sensitive files being copied into the synchronization repository or the public publishing package if a symlink exists in the skills directory.
**Learning:** Functions that copy directories or files often have default behaviors that are unsafe when processing user-controlled directories that might contain symbolic links pointing to sensitive system or user files.
**Prevention:** Always explicitly check  and skip or handle symlinks cautiously when copying contents from user-managed directories like .
## 2025-05-16 - Symlink Following in Directory Copying
**Vulnerability:** `shutil.copytree` and `shutil.copy2` follow symbolic links by default, which can lead to sensitive files being copied into the synchronization repository or the public publishing package if a symlink exists in the skills directory.
**Learning:** Functions that copy directories or files often have default behaviors that are unsafe when processing user-controlled directories that might contain symbolic links pointing to sensitive system or user files.
**Prevention:** Always explicitly check `Path.is_symlink()` and skip or handle symlinks cautiously when copying contents from user-managed directories like `~/.agents/skills/`.
