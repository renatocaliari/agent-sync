# Sentinel Security Journal

## 2025-05-22 - Strict Path Traversal Prevention in Skill Names
**Vulnerability:** Path traversal via unvalidated skill names (e.g., `../../`).
**Learning:** Using `$` in Python regex validation for file paths can be bypassed by a trailing newline (`\n`). `re.match` with `$` might still return a match if the newline is at the very end, which could cause issues when the string is used in path construction or shell commands.
**Prevention:** Always use a strict whitelist for names used in file operations and terminate the regex with `\Z` instead of `$` to ensure absolute end-of-string matching without newline bypass.
