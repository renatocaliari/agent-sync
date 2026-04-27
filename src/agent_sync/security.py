"""Security utilities for agent-sync."""

import os
import sys
from pathlib import Path
from typing import Any


def secure_open(path: str | Path, mode: str = "r", *args: Any, **kwargs: Any):
    """
    Open a file and ensure it has restricted permissions (0o600).
    On creation, the file is created with 0o600.
    For existing files, it attempts to harden permissions to 0o600.
    """
    path = Path(path)

    # Custom opener to ensure 0o600 on creation
    def opener(file_path: str, flags: int) -> int:
        return os.open(file_path, flags, 0o600)

    # Open the file
    f = open(path, mode, *args, opener=opener, **kwargs)

    # Attempt to harden permissions for existing files or just as a second layer
    try:
        # Use fchmod if available (Unix-like systems)
        if hasattr(os, "fchmod"):
            os.fchmod(f.fileno(), 0o600)
        else:
            # Fallback for Windows
            os.chmod(path, 0o600)
    except OSError:
        # Silently fail if we can't change permissions (e.g. read-only filesystem)
        pass

    return f


def ensure_secure_dir(path: str | Path) -> Path:
    """
    Ensure a directory exists and has restricted permissions (0o700).
    """
    path = Path(path)
    if not path.exists():
        path.mkdir(parents=True, exist_ok=True)

    try:
        os.chmod(path, 0o700)
    except OSError:
        pass

    return path
