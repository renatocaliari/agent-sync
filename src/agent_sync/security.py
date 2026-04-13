"""Security utilities for restricted file and directory operations."""

import os
from pathlib import Path


def secure_open(path: str | Path, mode: str = "w", permissions: int = 0o600, encoding: str = "utf-8"):
    """
    Open a file with restricted permissions.
    Ensures the file is created with the specified permissions (default 0o600).
    """
    path_obj = Path(path)

    # Ensure parent directory exists and is secure (0o700)
    ensure_secure_dir(path_obj.parent)

    # Use os.open to create file with specific permissions
    # O_WRONLY: Open for writing only
    # O_CREAT: Create file if it does not exist
    # O_TRUNC: Truncate file to zero length if it exists
    flags = os.O_WRONLY | os.O_CREAT | os.O_TRUNC

    # Handle different modes if necessary, but "w" is primary for config/state
    if "a" in mode:
        flags = os.O_WRONLY | os.O_CREAT | os.O_APPEND
        # Remove O_TRUNC if O_APPEND is used

    fd = os.open(str(path_obj), flags, permissions)

    # Ensure permissions are correct even if file already existed
    os.chmod(str(path_obj), permissions)

    return os.fdopen(fd, mode, encoding=encoding)


def ensure_secure_dir(path: str | Path, permissions: int = 0o700) -> None:
    """
    Ensure a directory exists and has restricted permissions.
    Default permissions are 0o700 (rwx------).
    """
    path_obj = Path(path)
    if not path_obj.exists():
        os.makedirs(path_obj, mode=permissions, exist_ok=True)

    # Always chmod to ensure permissions are correct regardless of umask or existing state
    os.chmod(path_obj, permissions)
