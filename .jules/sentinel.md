
## 2025-05-23 - Secure File Creation Pattern
**Vulnerability:** Race condition during file creation where a file exists with default (wider) permissions before `os.chmod` is called.
**Learning:** Default `open()` uses system umask, which often allows group or world readability. Hardening permissions after creation leaves a window of exposure.
**Prevention:** Use `os.open(path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)` followed by `os.fdopen()` to ensure the file is never readable by others from the moment of creation.
