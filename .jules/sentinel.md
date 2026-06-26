## 2025-05-15 - Regex Newline Injection Bypass
**Vulnerability:** Regex patterns using `$` instead of `\Z` allowed trailing newlines to bypass validation.
**Learning:** In Python's `re` module, `$` matches at the end of the string OR just before a newline at the end of the string. This can be exploited to inject arguments if the validated string is passed to a shell command.
**Prevention:** Always use `\Z` for absolute end-of-string matching in security-critical regex validators.

## 2026-06-26 - Regression of Regex Newline Injection in Internal Validators
**Vulnerability:** Duplicate internal `_is_valid_skill_name` functions in the `publish` flow regressed to using the vulnerable `$` anchor.
**Learning:** Security fixes applied to central validators (like `src/agent_sync/validators.py`) do not automatically propagate to duplicated internal validation logic in subpackages. Duplicated security logic is a major source of regressions.
**Prevention:** Consolidate validation logic into a single source of truth. Add specific regression tests for newline injection in all entry points that perform validation.
