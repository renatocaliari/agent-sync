## 2025-05-15 - Python Regex Bypass and Path Traversal Defense

**Vulnerability:** Path traversal in skill deletion and regex validation bypass via newline injection.
**Learning:** Python's `re` module `$` anchor matches the end of the string OR the position before a trailing newline. This allows attackers to bypass alphanumeric-only filters by appending a newline (e.g., `skill\n/../etc/passwd`). Additionally, `pathlib.Path` joining with `/` can be reset if the second argument is an absolute path.
**Prevention:**
1. Always use `\Z` instead of `$` in Python regex for absolute end-of-string matching.
2. Implement defense-in-depth for file operations by resolving paths and verifying they remain within the intended base directory using `.relative_to()`.
3. Explicitly handle symlinks using `.is_symlink()` and `.unlink()` to prevent `shutil.rmtree` from following links during cleanup.
