"""Security utilities for agent-sync."""

import os
from pathlib import Path
from typing import Any


def _secure_opener(path: str, flags: int) -> int:
    """Opener for open() that ensures 0o600 permissions on creation."""
    return os.open(path, flags, 0o600)


def ensure_secure_dir(path: Path) -> None:
    """
    Ensure directory exists and has 0o700 permissions (owner-only).
    Does not modify parent directories recursively for safety.
    Refuses to modify current directory (.) for safety.
    """
    path = path.resolve()
    # Refuse to modify home directory or current directory for safety
    if path == Path.cwd() or path == Path.home():
        return

    path.mkdir(parents=True, exist_ok=True)
    try:
        os.chmod(path, 0o700)
    except OSError:
        # Might fail on some filesystems or OSs
        pass


def secure_open(path: Path, mode: str = "r", **kwargs: Any):
    """
    Open a file ensuring 0o600 permissions (owner-only).
    Uses the 'opener' parameter to set permissions atomically on creation.
    Also attempts to harden existing files using fchmod or chmod.
    """
    path = path.resolve()
    # Ensure parent directory is secure if we might create the file
    if any(m in mode for m in "wax"):
        ensure_secure_dir(path.parent)

    # Use secure opener for atomic 0o600 on creation
    kwargs["opener"] = _secure_opener

    f = open(path, mode, **kwargs)

    # Harden existing file or ensure permissions are correct
    try:
        if hasattr(os, "fchmod"):
            os.fchmod(f.fileno(), 0o600)
        else:
            os.chmod(path, 0o600)
    except (OSError, AttributeError):
        # Fallback for systems that don't support these operations
        pass

    return f
