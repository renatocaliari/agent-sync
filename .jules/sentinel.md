## 2025-05-15 - Regex Newline Injection Bypass
**Vulnerability:** Regex patterns using `$` instead of `\Z` allowed trailing newlines to bypass validation.
**Learning:** In Python's `re` module, `$` matches at the end of the string OR just before a newline at the end of the string. This can be exploited to inject arguments if the validated string is passed to a shell command.
**Prevention:** Always use `\Z` for absolute end-of-string matching in security-critical regex validators.

## 2025-05-18 - Symlink Content Leakage in Sync/Publish
**Vulnerability:** Default `shutil.copytree` and `shutil.copy2` follow symbolic links, causing content from outside the intended directory to be copied (leaked) into the sync repository or published output.
**Learning:** `pathlib.Path.is_file()` and `is_dir()` return `True` for symlinks pointing to those types. When `shutil` encounters these, it treats them as real files/directories and copies their content unless `symlinks=True` or `follow_symlinks=False` is explicitly set.
**Prevention:** Always use `symlinks=True` for `shutil.copytree` and `follow_symlinks=False` for `shutil.copy2` when processing user-controlled directories. For discovery/scanning, explicitly check `is_symlink()` to skip or handle them specially.
