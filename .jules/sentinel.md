## 2025-05-15 - Regex Newline Injection Bypass
**Vulnerability:** Regex patterns using `$` instead of `\Z` allowed trailing newlines to bypass validation.
**Learning:** In Python's `re` module, `$` matches at the end of the string OR just before a newline at the end of the string. This can be exploited to inject arguments if the validated string is passed to a shell command.
**Prevention:** Always use `\Z` for absolute end-of-string matching in security-critical regex validators.

## 2026-07-04 - Publish Flow Content Leakage and Fragile Exclusions
**Vulnerability:** The publish flow followed symbolic links by default during directory and file copy operations, and used a brittle hand-rolled matching logic for file exclusions.
**Learning:** `shutil.copytree` and `shutil.copy2` default to following symbolic links, which can lead to accidental leakage of sensitive files outside the intended source directory if a user-controlled link exists. Additionally, manual string parsing for ignore patterns is error-prone compared to standard libraries.
**Prevention:** Explicitly set `symlinks=True` (for `copytree`) and `follow_symlinks=False` (for `copy2`) in security-sensitive paths. Use `fnmatch.filter` for robust, standard glob-based file exclusion logic.
