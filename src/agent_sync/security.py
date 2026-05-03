"""Security utilities for agent-sync."""

import os
import sys
from pathlib import Path
from typing import Optional, Union


def ensure_secure_dir(path: Union[str, Path]) -> None:
    """
    Ensure a directory exists and has restricted permissions (0o700).
    Only sets permissions on the leaf directory.
    """
    path = Path(path)
    if not path.exists():
        path.mkdir(parents=True, exist_ok=True)

    # Set 0o700 permissions (rwx------)
    os.chmod(path, 0o700)


def secure_open(path: Union[str, Path], mode: str = "r", encoding: Optional[str] = "utf-8"):
    """
    Open a file with restricted permissions (0o600).
    Uses the 'opener' parameter to ensure atomic 0o600 on creation.
    Also applies fchmod for existing files on Unix-like systems.
    """
    path = Path(path)

    def opener(path, flags):
        return os.open(path, flags, 0o600)

    # Open the file
    f = open(path, mode, encoding=encoding, opener=opener)

    # On Unix-like systems, also use fchmod to harden existing files
    if sys.platform != "win32":
        try:
            os.fchmod(f.fileno(), 0o600)
        except (AttributeError, OSError):
            pass

    return f
