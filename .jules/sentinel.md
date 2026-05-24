## 2025-05-15 - Regex Newline Injection Bypass
**Vulnerability:** Regex patterns using `$` instead of `\Z` allowed trailing newlines to bypass validation.
**Learning:** In Python's `re` module, `$` matches at the end of the string OR just before a newline at the end of the string. This can be exploited to inject arguments if the validated string is passed to a shell command.
**Prevention:** Always use `\Z` for absolute end-of-string matching in security-critical regex validators.

## 2025-05-16 - Symlink Content Leakage in Publishing
**Vulnerability:** The publishing process followed symbolic links, potentially leaking the content of sensitive files (e.g., SSH keys, credentials) located outside the skills directory into a public repository.
**Learning:** `shutil.copytree` and `shutil.copy2` follow symlinks by default. When copying user-controlled content for public distribution, symlinks must be handled explicitly to prevent Arbitrary File Read/Information Disclosure.
**Prevention:** Explicitly use `symlinks=True` in `shutil.copytree` and `follow_symlinks=False` in `shutil.copy2` to preserve links as links. Additionally, skip symlinks during initial discovery if they are not intended to be shared.
