# Sentinel Security Journal 🛡️

## 2025-05-15 - [Path Traversal in Skills Deletion]
**Vulnerability:** User-provided skill names were used to construct file paths without validation or path boundary checks in `src/agent_sync/skills_delete.py`.
**Learning:** Python's `pathlib.Path` joining operator `/` resets the path if the second argument is an absolute path (starts with `/`), and it doesn't prevent `..` segments.
**Prevention:** Always validate user-provided strings against a whitelist of characters, and use `.resolve()` and `.relative_to()` to ensure paths stay within the intended directory.
