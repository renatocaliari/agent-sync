## 2025-05-15 - [CRITICAL] Path Traversal in Skill Deletion
**Vulnerability:** The `agent-sync skills delete` command was vulnerable to path traversal because it joined user-provided skill names with the global skills directory without validation. An attacker could provide a name like `../../../../tmp/important_file` to delete arbitrary files.
**Learning:** Python's `pathlib.Path` joining operator `/` resets the path if the second argument is an absolute path, and `shutil.rmtree` happily follows `..` sequences. Relying on simple path joining for user-provided identifiers is extremely dangerous.
**Prevention:** Implement strict alphanumeric validation for identifiers (`validate_skill_name`) and use defense-in-depth by resolving the final path and verifying it remains within the intended parent directory.

## 2025-05-15 - [HIGH] Regex Bypass via Trailing Newlines
**Vulnerability:** Regex patterns for repository names and GitHub URLs used `$` to match the end of the string. In many regex engines, including Python's `re.match`, `$` can match before a trailing newline, allowing an attacker to append malicious characters after a valid-looking name.
**Learning:** `$` is not a reliable end-of-string anchor when security is at stake.
**Prevention:** Always use `\Z` instead of `$` to ensure the pattern matches the absolute end of the string.
