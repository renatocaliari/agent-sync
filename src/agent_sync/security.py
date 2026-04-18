"""Security utilities for agent-sync."""

import os
import io
from pathlib import Path
from typing import Union


def secure_open(
    filepath: Union[str, Path], mode: str, permissions: int = 0o600, encoding: str = "utf-8"
) -> io.TextIOWrapper:
    """
    Open a file with restricted permissions (default 0o600).
    Uses os.open with atomic flags to prevent TOCTOU vulnerabilities.

    Args:
        filepath: Path to the file
        mode: Standard Python open mode ('w', 'a', 'r', 'r+')
        permissions: File permissions (default 0o600)
        encoding: File encoding (default 'utf-8')

    Returns:
        io.TextIOWrapper: File object
    """
    path = Path(filepath)

    # Map Python modes to os flags
    if 'r+' in mode:
        flags = os.O_RDWR
    elif 'w' in mode:
        flags = os.O_WRONLY | os.O_CREAT | os.O_TRUNC
    elif 'a' in mode:
        flags = os.O_WRONLY | os.O_CREAT | os.O_APPEND
    else:  # default to read
        flags = os.O_RDONLY

    # On Unix, we can set the mode during creation
    # If file exists, os.open won't change its permissions
    fd = os.open(path, flags, permissions)

    # Ensure permissions are correct if the file already existed
    try:
        if hasattr(os, "fchmod"):
            os.fchmod(fd, permissions)
    except OSError:
        pass  # May fail on some filesystems or OSes

    return os.fdopen(fd, mode, encoding=encoding)


def ensure_secure_dir(path: Union[str, Path], permissions: int = 0o700) -> Path:
    """
    Ensure a directory exists with restricted permissions (default 0o700).

    Args:
        path: Path to the directory
        permissions: Directory permissions (default 0o700)

    Returns:
        Path: The directory path
    """
    dir_path = Path(path)
    if not dir_path.exists():
        dir_path.mkdir(parents=True, mode=permissions)
        # mode in mkdir is masked by umask, so we chmod it
        os.chmod(dir_path, permissions)
    else:
        # Enforce permissions on existing directory
        os.chmod(dir_path, permissions)
    return dir_path
