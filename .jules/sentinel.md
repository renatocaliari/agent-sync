## 2025-05-15 - Regex Newline Injection Bypass
**Vulnerability:** Regex patterns using `$` instead of `\Z` allowed trailing newlines to bypass validation.
**Learning:** In Python's `re` module, `$` matches at the end of the string OR just before a newline at the end of the string. This can be exploited to inject arguments if the validated string is passed to a shell command.
**Prevention:** Always use `\Z` for absolute end-of-string matching in security-critical regex validators.

## 2025-05-20 - Security Scanner Code Block Bypass
**Vulnerability:** The security scanner masked code blocks before scanning, allowing secrets inside markdown code blocks to be published without warning.
**Learning:** Over-aggressive redacting/masking during security analysis can lead to false negatives. Real secrets are often accidentally pasted into example code blocks.
**Prevention:** Scan the original raw content for secrets, then use the masked/parsed structure only to provide context (e.g. labeling a match as "code" vs "hardcoded") rather than to prevent the scan entirely.

## 2025-05-20 - Skill Discovery Symlink Leakage
**Vulnerability:** `get_available_skills` included symbolic links to `.md` files, which could point to sensitive files outside the skills directory and leak their content during public publishing.
**Learning:** `pathlib.Path.is_file()` returns `True` for symlinks pointing to files. Iterating over user-controlled directories without checking `is_symlink()` can lead to unintended access to external files.
**Prevention:** Always explicitly check and skip `is_symlink()` when discovering files for recursive operations or public sharing, unless symlinks are explicitly intended and validated.
