## 2025-05-15 - Regex Newline Injection Bypass
**Vulnerability:** Regex patterns using `$` instead of `\Z` allowed trailing newlines to bypass validation.
**Learning:** In Python's `re` module, `$` matches at the end of the string OR just before a newline at the end of the string. This can be exploited to inject arguments if the validated string is passed to a shell command.
**Prevention:** Always use `\Z` for absolute end-of-string matching in security-critical regex validators.

## 2025-05-15 - Symlink Content Leakage in Publish Flow
**Vulnerability:** `shutil.copytree` and `shutil.copy2` followed symlinks by default, copying their target content into the published repository.
**Learning:** In security-sensitive copy operations (like publishing user content), symlinks must be preserved as links to prevent accidental disclosure of sensitive files (e.g., `/etc/passwd`) that might be linked.
**Prevention:** Use `symlinks=True` in `shutil.copytree` and `follow_symlinks=False` in `shutil.copy2`.

## 2025-05-15 - Brittle File Exclusion Logic
**Vulnerability:** Hand-rolled string matching for file exclusions failed to catch many intended patterns (e.g., 'sessions', 'models.json').
**Learning:** Simple string prefix/suffix checks are insufficient for robust file filtering. `fnmatch.filter` provides a standard, reliable way to apply shell-style globbing.
**Prevention:** Use `fnmatch.filter` for file and directory name filtering against security exclusion lists.
