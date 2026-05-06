"""Security utilities for agent-sync."""

import os
from pathlib import Path
from typing import Any


def secure_open(path: str | Path, mode: str = "r", **kwargs: Any):
    """
    Open a file with restricted permissions (0o600).

    If the file is being created, it will be created with read/write
    permissions for the owner only. If it already exists, its
    permissions will be hardened.
    """
    path = Path(path)

    def opener(path: str, flags: int) -> int:
        return os.open(path, flags, 0o600)

    # If we are writing, we ensure the file has the right permissions
    if "w" in mode or "a" in mode or "+" in mode or "x" in mode:
        # If file exists, harden it before opening if possible
        if path.exists():
            try:
                os.chmod(path, 0o600)
            except OSError:
                pass

        # Use the secure opener for creation
        return open(path, mode, opener=opener, **kwargs)

    return open(path, mode, **kwargs)


def ensure_secure_dir(path: str | Path) -> None:
    """Ensure a directory exists and has restricted permissions (0o700)."""
    path = Path(path)
    path.mkdir(parents=True, exist_ok=True)
    try:
        os.chmod(path, 0o700)
    except OSError:
        pass
