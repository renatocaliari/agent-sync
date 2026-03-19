# Sentinel's Security Journal

## 2025-05-15 - Regex End-of-String Bypass (Newline Injection)
**Vulnerability:** Regex patterns using `$` for end-of-string matching in Python's `re` module can be bypassed by appending a newline (`\n`) to the input, as `$` matches before a trailing newline.
**Learning:** Python's `re` behavior for `$` is consistent with many other languages but can lead to security bypasses if developers expect it to match only the absolute end of the string.
**Prevention:** Always use `\Z` instead of `$` in Python regular expressions when strict end-of-string matching is required for security validations.

## 2025-05-15 - Path Traversal in Skill Deletion
**Vulnerability:** User-provided skill names were used to construct file paths for `shutil.rmtree` without prior validation.
**Learning:** Even internal CLI tools that manage local files must validate user-provided identifiers to prevent accidental or malicious path traversal (e.g., using `../` to delete arbitrary directories).
**Prevention:** Implement strict input validation for all user-provided strings used in file system operations. Restrict allowed characters and check for traversal patterns.
