"""Security utilities for agent-sync."""

import os
from pathlib import Path
from typing import Any


def secure_open(path: str | Path, mode: str = "r", **kwargs: Any):
    """
    Open a file with restricted permissions (0o600).

    Uses the 'opener' parameter to ensure the file is created with
    the correct permissions atomically on supported systems.
    """
    path = Path(path)

    def opener(path: str, flags: int) -> int:
        # 0o600: read/write by owner only
        return os.open(path, flags, 0o600)

    # Use the custom opener for file creation
    handle = open(path, mode, opener=opener, **kwargs)

    # Hardening: ensure permissions even if file already existed
    try:
        if hasattr(os, "fchmod"):
            os.fchmod(handle.fileno(), 0o600)
        else:
            # Fallback for Windows or systems without fchmod
            os.chmod(path, 0o600)
    except OSError:
        # Ignore errors if we can't change permissions (e.g. read-only FS)
        pass

    return handle


def ensure_secure_dir(path: str | Path) -> Path:
    """
    Ensure a directory exists and has restricted permissions (0o700).
    """
    path = Path(path)
    if not path.exists():
        path.mkdir(parents=True, exist_ok=True)

    try:
        # 0o700: read/write/execute by owner only
        os.chmod(path, 0o700)
    except OSError:
        pass

    return path
