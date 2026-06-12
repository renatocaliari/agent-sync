## 2025-05-15 - Regex Newline Injection Bypass
**Vulnerability:** Regex patterns using `$` instead of `\Z` allowed trailing newlines to bypass validation.
**Learning:** In Python's `re` module, `$` matches at the end of the string OR just before a newline at the end of the string. This can be exploited to inject arguments if the validated string is passed to a shell command.
**Prevention:** Always use `\Z` for absolute end-of-string matching in security-critical regex validators.

## 2025-05-22 - Symlink Content Leakage in File Operations
**Vulnerability:** `shutil.copytree` and `shutil.copy2` follow symbolic links by default, copying the linked file's content instead of the link itself.
**Learning:** When an application copies user-controlled directories (like skills or agent configs), following symlinks can lead to sensitive host files being "leaked" into a repository or destination directory if a symlink points outside the intended scope.
**Prevention:** Always use `symlinks=True` in `shutil.copytree` and `follow_symlinks=False` in `shutil.copy2` when handling directories that may contain user-provided or third-party symlinks.
