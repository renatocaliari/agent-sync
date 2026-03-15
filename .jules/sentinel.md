# Sentinel's Journal

## 2026-03-15 - Path Traversal in Skills Deletion
**Vulnerability:** Path traversal vulnerability in `agent-sync skills delete`. User-provided skill names were used directly to construct file system paths for deletion without validation, allowing an attacker to delete arbitrary files by using names like `../../file.txt`.
**Learning:** Even internal CLI tools that manage local files must strictly validate user input when that input is used to form file paths, especially for destructive operations like deletion.
**Prevention:** Implement a central `validate_skill_name` validator that restricts input to a safe character set (alphanumeric, hyphens, underscores) and use it consistently across all commands that accept skill names as arguments.
