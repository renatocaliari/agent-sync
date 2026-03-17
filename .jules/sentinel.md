## 2026-03-17 - Strict Regex Anchors for Path Safety
**Vulnerability:** Newline injection bypass in path/name validation.
**Learning:** In Python, the '$' regex anchor can match before a trailing newline (e.g., 'payload\n'), which could potentially bypass validation if the input is used in file system operations that strip or ignore the newline.
**Prevention:** Always use '\Z' instead of '$' in regular expressions intended for security validation to ensure the pattern matches the absolute end of the string.
