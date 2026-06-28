## 2025-05-15 - Regex Newline Injection Bypass
**Vulnerability:** Regex patterns using `$` instead of `\Z` allowed trailing newlines to bypass validation.
**Learning:** In Python's `re` module, `$` matches at the end of the string OR just before a newline at the end of the string. This can be exploited to inject arguments if the validated string is passed to a shell command.
**Prevention:** Always use `\Z` for absolute end-of-string matching in security-critical regex validators.

## 2025-05-20 - Incomplete File Exclusion Logic
**Vulnerability:** A custom `_ignore_func` used for `shutil.copytree` in the publish flow only handled patterns starting with `*.` or `.`. This caused many default security patterns (like `sessions`, `cache`, `models.json`) to be ignored by the ignore-function itself, resulting in them being published to public repositories.
**Learning:** Custom implementations of pattern matching are often brittle. `shutil.copytree` expects an ignore callable to return a list of names to skip, and it's easy to get the logic wrong when trying to match diverse patterns (exact matches vs. extensions vs. prefixes).
**Prevention:** Use standard libraries like `fnmatch.filter` to implement robust file filtering logic that handles glob and literal patterns consistently.
