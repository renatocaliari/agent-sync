## 2025-05-14 - [MEDIUM] Path Traversal in Skill Deletion
**Vulnerability:** The `agent-sync skills delete` command accepted arbitrary skill names that were used to build file paths without validation, allowing for path traversal and deletion of files outside the intended directories (e.g., `../../../file`).
**Learning:** Even internal-looking CLI tools must validate user input when it's used in file system operations. Using `shutil.rmtree` on unvalidated paths is particularly dangerous.
**Prevention:** Always use a strict whitelist for names that will be used as path components. Use regex with `\Z` to ensure no newline injection can bypass the validation.
