"""Security utilities for agent-sync."""

import os
from pathlib import Path
from typing import Union


def secure_open(path: Union[str, Path], mode: str = 'w', permissions: int = 0o600):
    """
    Atomically open a file with restricted permissions.

    Ensures that the file is created with the specified permissions
    at the moment of creation, avoiding race conditions.

    Args:
        path: Path to the file.
        mode: File opening mode (must be a write mode).
        permissions: File permissions (default: 0o600 - owner read/write).

    Returns:
        A file object.
    """
    path = Path(path)
    # Ensure parent directory exists (with secure permissions if created)
    ensure_secure_dir(path.parent)

    # Use os.open with O_CREAT and O_TRUNC to ensure permissions at creation
    flags = os.O_WRONLY | os.O_CREAT | os.O_TRUNC
    fd = os.open(path, flags, permissions)
    return os.fdopen(fd, mode)


def ensure_secure_dir(path: Union[str, Path], permissions: int = 0o700) -> Path:
    """
    Ensure a directory exists with restricted permissions.

    Args:
        path: Path to the directory.
        permissions: Directory permissions (default: 0o700 - owner read/write/execute).

    Returns:
        The Path object.
    """
    path = Path(path)
    if not path.exists():
        # Ensure parent exists securely
        if not path.parent.exists():
            ensure_secure_dir(path.parent, permissions)

        path.mkdir(mode=permissions, exist_ok=True)
        # Ensure mode is correct even if umask interfered
        os.chmod(path, permissions)
    return path
