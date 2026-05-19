## 2025-05-15 - Regex Newline Injection Bypass
**Vulnerability:** Regex patterns using `$` instead of `\Z` allowed trailing newlines to bypass validation.
**Learning:** In Python's `re` module, `$` matches at the end of the string OR just before a newline at the end of the string. This can be exploited to inject arguments if the validated string is passed to a shell command.
**Prevention:** Always use `\Z` for absolute end-of-string matching in security-critical regex validators.

## 2025-05-19 - Symlink Content Leakage during Publishing
**Vulnerability:** The publishing process followed symbolic links in the skills and agent instructions directories, potentially leaking sensitive content from outside those directories into public repositories.
**Learning:** shutil.copytree and shutil.copy2 follow symbolic links by default. pathlib.Path.is_file() and is_dir() return True for symbolic links pointing to files or directories respectively.
**Prevention:** Use is_symlink() to explicitly check and skip symlinks during file discovery. When copying, use symlinks=True in copytree and follow_symlinks=False in copy2 to preserve links as links rather than following them.
