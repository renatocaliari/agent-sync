"""Security utilities for agent-sync."""

import os
from pathlib import Path
from typing import Optional, Any


def secure_open(path: Path | str, mode: str = "r", encoding: Optional[str] = None) -> Any:
    """
    Open a file with restricted permissions (0o600).

    Ensures that if the file is created, it has 0o600 permissions.
    Also attempts to harden existing files to 0o600.
    """
    path_obj = Path(path)

    def opener(path_str, flags):
        # Open with 0o600 permissions if created
        return os.open(path_str, flags, 0o600)

    # Use the opener to ensure 0o600 on creation
    f = open(path_obj, mode, encoding=encoding, opener=opener)

    # Secondary measure: harden existing file permissions
    try:
        # Use fchmod on the file descriptor if available (Unix-like)
        if hasattr(os, "fchmod"):
            os.fchmod(f.fileno(), 0o600)
        else:
            # Fallback for Windows
            os.chmod(path_obj, 0o600)
    except OSError:
        # Best effort for hardening
        pass

    return f


def ensure_secure_dir(path: Path | str) -> None:
    """
    Ensure a directory exists and has restricted permissions (0o700).
    """
    path_obj = Path(path)

    # Create directory if it doesn't exist
    path_obj.mkdir(parents=True, exist_ok=True)

    # Harden permissions to 0o700
    try:
        os.chmod(path_obj, 0o700)
    except OSError:
        # Best effort
        pass
