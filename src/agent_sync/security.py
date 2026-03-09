"""Security utilities for agent-sync."""

import os
from pathlib import Path
from typing import Union


def secure_open(path: Union[str, Path], mode: str = "w", permissions: int = 0o600):
    """
    Open a file securely with restricted permissions.

    This ensures that if the file is created, it has the specified permissions
    (default 0o600: read/write for owner only).
    """
    path = Path(path)

    # Mapping of Python open modes to os.open flags
    if "w" in mode:
        flags = os.O_WRONLY | os.O_CREAT | os.O_TRUNC
    elif "a" in mode:
        flags = os.O_WRONLY | os.O_CREAT | os.O_APPEND
    elif "x" in mode:
        flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    else:
        # For read modes, just use standard open
        return open(path, mode)

    # Use os.open to set permissions at creation time
    # This avoids a race condition between creation and chmod
    fd = os.open(path, flags, permissions)
    return os.fdopen(fd, mode)


def ensure_secure_dir(path: Union[str, Path], permissions: int = 0o700):
    """
    Ensure a directory exists with restricted permissions (default 0o700).
    """
    path = Path(path)
    path.mkdir(parents=True, exist_ok=True)
    # Ensure correct permissions even if it already existed
    os.chmod(path, permissions)
