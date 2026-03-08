## 2025-03-08 - Path Traversal in Skills Management
**Vulnerability:** User-provided skill names were used to construct file paths for deletion and reconciliation without validation, allowing directory traversal (e.g., '../../') to access or delete files outside the intended scope.
**Learning:** Even internal tool-to-tool integrations (like agent skills) can be vulnerable if they accept and process identifiers that are ultimately mapped to the file system.
**Prevention:** Always use a strict allow-list validator (regex) for any user-provided identifier used in file path construction. Forbid characters like '.' and '/' entirely if they are not part of the expected identifier format.
