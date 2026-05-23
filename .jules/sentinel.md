## 2025-05-15 - Regex Newline Injection Bypass
**Vulnerability:** Regex patterns using `$` instead of `\Z` allowed trailing newlines to bypass validation.
**Learning:** In Python's `re` module, `$` matches at the end of the string OR just before a newline at the end of the string. This can be exploited to inject arguments if the validated string is passed to a shell command.
**Prevention:** Always use `\Z` for absolute end-of-string matching in security-critical regex validators.

## 2025-05-22 - Extension Path Traversal & Unsanitized Editor Execution
**Vulnerability:** Restoring extension skills was vulnerable to path traversal if the manifest contained '..' in extension directories. Also, CLI edit commands used unsanitized editor environment variables with `subprocess.run(shell=False)` but without `shlex.split()`, which could lead to execution failure or limited command injection if the editor string contained malicious arguments.
**Learning:** External manifests and environment variables are untrusted inputs. `shlex.split()` is essential for safe handling of command strings from environment variables, and `Path.resolve()` with parentage checks is necessary for directory containment.
**Prevention:** Use `is_safe_path` for all directory-restoration logic and `validate_editor` with `shlex.split()` for any user-provided command strings.
