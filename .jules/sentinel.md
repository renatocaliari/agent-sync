## 2025-05-15 - Regex Newline Injection Bypass
**Vulnerability:** Regex patterns using `$` instead of `\Z` allowed trailing newlines to bypass validation.
**Learning:** In Python's `re` module, `$` matches at the end of the string OR just before a newline at the end of the string. This can be exploited to inject arguments if the validated string is passed to a shell command.
**Prevention:** Always use `\Z` for absolute end-of-string matching in security-critical regex validators.

## 2025-05-20 - Security Scanner Evasion via Code Blocks
**Vulnerability:** The security scanner redacted content inside code blocks before scanning, allowing real secrets to be published if they were placed inside a code block.
**Learning:** Redacting content to reduce false positives can lead to "blind spots" if the redaction is too aggressive.
**Prevention:** Scan the original content for secrets, then use the locations of known "false positive regions" (like code blocks) only to adjust the severity or context of the finding, rather than skipping the scan.

## 2025-05-20 - Symbolic Link Content Leakage during Publishing
**Vulnerability:** `shutil.copytree` and `shutil.copy2` follow symbolic links by default, which can lead to sensitive content being copied from outside the intended directory into a public repository.
**Learning:** `pathlib.Path.is_file()` and `is_dir()` return `True` for symlinks pointing to files/dirs. Standard `shutil` operations will follow these unless explicitly told not to.
**Prevention:** Always use `symlinks=True` with `shutil.copytree` and `follow_symlinks=False` with `shutil.copy2` when handling user-controlled paths or in security-sensitive flows.
