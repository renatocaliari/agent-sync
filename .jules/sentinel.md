# Sentinel Security Journal

## 2025-05-15 - Regex Anchor Bypass for Path Validation
**Vulnerability:** Use of `$` anchor in Python `re` module for input validation.
**Learning:** In Python, the `$` anchor matches the end of the string OR the position just before a trailing newline (`\n`). This allows an attacker to append a newline and potentially bypass validation if the trailing newline is then used in file path construction or shell commands.
**Prevention:** Always use `\Z` instead of `$` in Python regex patterns for strict end-of-string matching.
