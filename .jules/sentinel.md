## 2025-05-15 - Regex Newline Injection Bypass
**Vulnerability:** Regex patterns using `$` instead of `\Z` allowed trailing newlines to bypass validation.
**Learning:** In Python's `re` module, `$` matches at the end of the string OR just before a newline at the end of the string. This can be exploited to inject arguments if the validated string is passed to a shell command.
**Prevention:** Always use `\Z` for absolute end-of-string matching in security-critical regex validators.

## 2026-07-01 - Publish Flow Content Leakage
**Vulnerability:** The public skill publishing flow was vulnerable to information disclosure via symbolic link traversal and brittle file exclusion logic.  followed symlinks into sensitive areas, and the hand-rolled ignore function only handled a subset of intended patterns.
**Learning:**  (before 3.12 or if not specified) and  follow symlinks by default. Hand-rolling glob matching is error-prone;  is the robust standard.
**Prevention:** Always use `symlinks=True` in `shutil.copytree` and `follow_symlinks=False` in `shutil.copy2` for security-sensitive copies. Use `fnmatch` for pattern matching.

## 2025-05-15 - Publish Flow Content Leakage & Regex Injection
**Vulnerability:** The public skill publishing flow was vulnerable to information disclosure via symbolic link traversal and brittle file exclusion logic. Additionally, `_is_valid_skill_name` regex allowed newline injection.
**Learning:** `shutil.copytree` and `shutil.copy2` follow symlinks by default, potentially leaking content from outside the source directory. Hand-rolling glob matching is error-prone; `fnmatch.filter` is the robust standard. The `$` regex anchor in Python matches before a trailing newline.
**Prevention:** Always use `symlinks=True` in `shutil.copytree` and `follow_symlinks=False` in `shutil.copy2` for security-sensitive copies. Use `fnmatch.filter` for pattern matching. Always use `\Z` for absolute end-of-string regex matching.
