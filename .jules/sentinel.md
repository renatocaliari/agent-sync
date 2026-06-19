## 2025-05-15 - Regex Newline Injection Bypass
**Vulnerability:** Regex patterns using `$` instead of `\Z` allowed trailing newlines to bypass validation.
**Learning:** In Python's `re` module, `$` matches at the end of the string OR just before a newline at the end of the string. This can be exploited to inject arguments if the validated string is passed to a shell command.
**Prevention:** Always use `\Z` for absolute end-of-string matching in security-critical regex validators.

## 2025-05-15 - Broken File Exclusion Logic in Publish Flow
**Vulnerability:** Manual string matching for file exclusions in `git_publish.py` failed to ignore sensitive directories like `sessions` and files like `models.json` because it only checked for patterns starting with `*.` or `.`.
**Learning:** Hardcoding shell-style pattern matching is error-prone. The `shutil.copytree` ignore callable should leverage standard libraries like `fnmatch` to ensure consistent and robust filtering.
**Prevention:** Use `fnmatch.fnmatch` or similar standard utilities for matching ignore patterns, and always verify exclusion logic with integration tests that check for the *absence* of sensitive files in the destination.
