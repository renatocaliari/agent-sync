## 2025-05-15 - Regex Newline Injection Bypass
**Vulnerability:** Regex patterns using `$` instead of `\Z` allowed trailing newlines to bypass validation.
**Learning:** In Python's `re` module, `$` matches at the end of the string OR just before a newline at the end of the string. This can be exploited to inject arguments if the validated string is passed to a shell command.
**Prevention:** Always use `\Z` for absolute end-of-string matching in security-critical regex validators.

## 2025-05-16 - Symlink Content Leakage in File Operations
**Vulnerability:** Using shutil.copy2 and shutil.copytree without explicit symlink handling allowed following links to targets outside the intended directory.
**Learning:** pathlib.Path.is_file() and is_dir() return True for symlinks pointing to files/dirs. Without follow_symlinks=False or symlinks=True, shutil will follow these links and copy the target content, which can leak sensitive data from the host system if a symlink points to something like /etc/passwd.
**Prevention:** Always use symlinks=True in copytree or follow_symlinks=False in copy2 when processing user-controlled or potentially untrusted directory structures.
