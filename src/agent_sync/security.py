"""Security utilities for agent-sync."""

import os
from pathlib import Path
from typing import Union


def secure_open(path: Union[str, Path], mode: str, permissions: int = 0o600, encoding: str = "utf-8"):
    """
    Open a file with restricted permissions using os.open and os.fdopen.
    Ensures the file is created with the specified permissions (default 0o600).
    """
    path = Path(path)

    # Ensure the directory exists
    path.parent.mkdir(parents=True, exist_ok=True)

    # Map Python open modes to os.open flags
    if "w" in mode:
        flags = os.O_WRONLY | os.O_CREAT | os.O_TRUNC
    elif "a" in mode:
        flags = os.O_WRONLY | os.O_CREAT | os.O_APPEND
    elif "r" in mode:
        if "+" in mode:
            flags = os.O_RDWR
        else:
            flags = os.O_RDONLY
    else:
        # Default to read if not specified
        flags = os.O_RDONLY

    # Open the file descriptor with restricted permissions
    # Note: permissions are only applied if the file is created
    fd = os.open(path, flags, permissions)

    # Ensure permissions are correct even if file already existed
    os.chmod(path, permissions)

    return os.fdopen(fd, mode, encoding=encoding)


def ensure_secure_dir(path: Union[str, Path], permissions: int = 0o700):
    """
    Ensure a directory exists and has restricted permissions (default 0o700).
    """
    path = Path(path)

    if not path.exists():
        os.makedirs(path, mode=permissions, exist_ok=True)

    # Explicitly set permissions to ensure they are correct regardless of umask
    os.chmod(path, permissions)
    return path
