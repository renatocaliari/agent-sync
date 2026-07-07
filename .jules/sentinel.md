## 2025-05-15 - Regex Newline Injection Bypass
**Vulnerability:** Regex patterns using `$` instead of `\Z` allowed trailing newlines to bypass validation.
**Learning:** In Python's `re` module, `$` matches at the end of the string OR just before a newline at the end of the string. This can be exploited to inject arguments if the validated string is passed to a shell command.
**Prevention:** Always use `\Z` for absolute end-of-string matching in security-critical regex validators.

## 2026-07-04 - CalledProcessError Token Leakage
**Vulnerability:** `subprocess.CalledProcessError` includes the raw command arguments in its string representation. If these arguments contain sensitive tokens (e.g., in a git remote URL), the tokens are leaked whenever the exception is logged or printed.
**Learning:** Sanitizing `stderr` and `stdout` is not enough; the `cmd` argument passed to `CalledProcessError` must also be sanitized.
**Prevention:** Use a helper function like `_sanitize_git_args` to redact sensitive information from the command list before raising or handling `CalledProcessError`.
