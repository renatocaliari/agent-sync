## 2025-05-15 - Regex Newline Injection Bypass
**Vulnerability:** Regex patterns using `$` instead of `\Z` allowed trailing newlines to bypass validation.
**Learning:** In Python's `re` module, `$` matches at the end of the string OR just before a newline at the end of the string. This can be exploited to inject arguments if the validated string is passed to a shell command.
**Prevention:** Always use `\Z` for absolute end-of-string matching in security-critical regex validators.

## 2026-07-04 - Sensitive Data Leakage via Brittle File Exclusion
**Vulnerability:** Hand-rolled exclusion logic in `git_publish.py` failed to match exact filenames and directories, leading to leakage of sensitive files (e.g., `.env`, `models.json`) and directories (e.g., `sessions/`, `cache/`) during the publish flow.
**Learning:** Manual string matching for file exclusions is error-prone. `shutil.copytree`'s `ignore` parameter works on a per-directory basis and requires a list of names to skip within that directory.
**Prevention:** Use `fnmatch.filter` to robustly match filenames and directories against patterns in security filters.
