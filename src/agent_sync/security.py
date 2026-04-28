"""Security utilities for agent-sync."""

import os
from pathlib import Path
from typing import Any, Callable, Optional


def secure_open(path: str | Path, mode: str = "r", **kwargs: Any) -> Any:
    """
    Open a file with secure permissions (0o600).

    If the file is being created, it will be created with 0o600 permissions.
    If it already exists, its permissions will be hardened to 0o600.
    """
    path = Path(path)

    def opener(path: str, flags: int) -> int:
        return os.open(path, flags, 0o600)

    # Use the opener to ensure 0o600 on creation
    f = open(path, mode, opener=opener, **kwargs)

    # Also harden existing files using fchmod if available (Unix)
    try:
        os.fchmod(f.fileno(), 0o600)
    except AttributeError:
        # Fallback for Windows
        os.chmod(path, 0o600)

    return f


def ensure_secure_dir(path: str | Path) -> Path:
    """
    Ensure a directory exists and has secure permissions (0o700).
    """
    path = Path(path)

    if not path.exists():
        path.mkdir(parents=True, exist_ok=True)

    # Harden permissions to 0o700
    os.chmod(path, 0o700)

    return path
