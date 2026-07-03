## 2025-05-15 - Regex Newline Injection Bypass
**Vulnerability:** Regex patterns using `$` instead of `\Z` allowed trailing newlines to bypass validation.
**Learning:** In Python's `re` module, `$` matches at the end of the string OR just before a newline at the end of the string. This can be exploited to inject arguments if the validated string is passed to a shell command.
**Prevention:** Always use `\Z` for absolute end-of-string matching in security-critical regex validators.

## 2025-05-15 - Token Leakage in CalledProcessError
**Vulnerability:** `subprocess.CalledProcessError` exceptions included unsanitized command arguments in the `cmd` attribute.
**Learning:** Even if `stdout` and `stderr` are sanitized, the `cmd` list (which often contains URLs with tokens) is stored in the exception object and can be leaked if the exception is printed or logged.
**Prevention:** Explicitly sanitize the `cmd` or `args` list before passing it to `CalledProcessError` or use a wrapper that redacts sensitive patterns from all exception attributes.
