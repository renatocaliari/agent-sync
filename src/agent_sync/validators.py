"""Validation utilities for agent-sync."""

import re
from pathlib import Path
from urllib.parse import urlparse


def is_safe_path(path: Path, base_dir: Path) -> bool:
    """Check if a path is safely contained within a base directory."""
    try:
        # resolve() handles '..' and symlinks.
        # We want to ensure the final path is still under base_dir.
        resolved_path = path.resolve()
        resolved_base = base_dir.resolve()
        return resolved_base in resolved_path.parents or resolved_path == resolved_base
    except Exception:
        return False


def validate_editor(editor: str) -> bool:
    """
    Validate an editor command string to prevent shell injection.

    Rules:
    - Max length 255 characters.
    - No dangerous shell metacharacters.
    """
    if not editor:
        return False

    if len(editor) > 255:
        return False

    # Strictly forbid common shell injection characters
    if any(c in editor for c in ";|&<>($)`'\"{}"):
        return False

    return True


def validate_repo_name(name: str) -> bool:
    """
    Validate a GitHub repository name or slug (owner/repo).

    Rules:
    - Only alphanumeric characters, hyphens, underscores, periods, and a single forward slash.
    - Cannot start with a hyphen, period, or slash.
    - Max length 100 characters.
    """
    if not name:
        return False

    # GitHub repo name/slug regex: [a-zA-Z0-9._/-]
    # Cannot start with a hyphen, period, or slash.
    # Optionally can have one slash in the middle.
    # First char must be alphanumeric (not . or -)
    pattern = r'^[a-zA-Z0-9][a-zA-Z0-9._-]*(?:/[a-zA-Z0-9][a-zA-Z0-9._-]*)?\Z'

    if not re.match(pattern, name):
        return False

    if len(name) > 100:
        return False

    return True


def validate_skill_name(name: str) -> bool:
    """
    Validate a skill name to prevent path traversal and shell injection.

    Rules:
    - Only alphanumeric characters, hyphens, underscores, and periods.
    - Must start with an alphanumeric character.
    - No slashes allowed.
    - Max length 64 characters.
    """
    if not name:
        return False

    pattern = r'^[a-zA-Z0-9][a-zA-Z0-9._-]*\Z'
    if not re.match(pattern, name):
        return False

    if len(name) > 64:
        return False

    return True


def validate_github_url(url: str) -> bool:
    """
    Validate a GitHub HTTPS URL to prevent argument injection and ensure correct format.

    Format: https://github.com/owner/repo[.git]
    """
    if not url:
        return False

    # Strictly forbid whitespace and other dangerous characters upfront
    if any(c in url for c in " \n\r\t;'\"`<>|"):
        return False

    try:
        parsed = urlparse(url)

        # Scheme must be https
        if parsed.scheme != 'https':
            return False

        # Netloc must be github.com
        if parsed.netloc != 'github.com':
            return False

        # Path should be /owner/repo or /owner/repo.git
        path = parsed.path.strip('/')
        parts = path.split('/')

        if len(parts) != 2:
            return False

        owner, repo = parts

        # Validate owner (alphanumeric and hyphens, no leading hyphen)
        owner_pattern = r'^[a-zA-Z0-9][a-zA-Z0-9-]*\Z'
        if not re.match(owner_pattern, owner):
            return False

        # Validate repo
        if repo.endswith('.git'):
            repo = repo[:-4]

        # Explicitly validate repo name without slash
        repo_pattern = r'^[a-zA-Z0-9][a-zA-Z0-9._-]*\Z'
        if not re.match(repo_pattern, repo):
            return False

        # Also validate against general repo name rules
        if not validate_repo_name(repo):
            return False

        # No params, query, or fragment allowed
        if parsed.params or parsed.query or parsed.fragment:
            return False

        return True
    except Exception:
        return False
