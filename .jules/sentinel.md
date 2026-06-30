## 2025-05-15 - Regex Newline Injection Bypass
**Vulnerability:** Regex patterns using `$` instead of `\Z` allowed trailing newlines to bypass validation.
**Learning:** In Python's `re` module, `$` matches at the end of the string OR just before a newline at the end of the string. This can be exploited to inject arguments if the validated string is passed to a shell command.
**Prevention:** Always use `\Z` for absolute end-of-string matching in security-critical regex validators.

## 2025-05-15 - [HIGH] Data Leakage and Newline Injection in Publish Flow
**Vulnerability:**
1. Brittle file exclusion logic in `git_publish.py` failed to ignore sensitive directories like `sessions/` and `cache/`.
2. Newline injection was possible in skill name validation regexes due to usage of `$` anchor.
3. Content leakage via symbolic links: `shutil.copytree` followed symlinks by default, potentially copying sensitive files from outside the skill directory.

**Learning:**
1. Hand-rolling directory exclusion logic is error-prone; standard libraries like `fnmatch` should be used for pattern matching.
2. The `$` anchor in Python regex matches either the end of the string or the position before a newline at the end of the string. `\Z` should always be used for strict end-of-string matching in security-sensitive validations.
3. `shutil.copytree` and `shutil.copy2` follow symlinks by default. In multi-tenant or user-controlled environments, this can lead to data leakage if a user can create a symlink to a sensitive file.

**Prevention:**
1. Use `fnmatch.filter` for robust file/directory exclusion patterns.
2. Use `\Z` instead of `$` in validation regexes.
3. Explicitly set `symlinks=True` in `copytree` or `follow_symlinks=False` in `copy2` when handling user-provided directory structures.
