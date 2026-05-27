"""Security utilities for agent-sync."""

import os
from pathlib import Path
from typing import IO, Any


def ensure_secure_dir(path: Path) -> None:
    """
    Ensure a directory exists with secure permissions (0o700).

    If the directory already exists, it updates permissions to 0o700.
    """
    if not path.exists():
        path.mkdir(parents=True, exist_ok=True)

    # Enforce 0o700 (drwx------)
    try:
        os.chmod(path, 0o700)
    except PermissionError:
        # If we can't change permissions, we ignore it (e.g., read-only filesystem)
        pass


def secure_open(path: Path, mode: str = "r", **kwargs: Any) -> IO:
    """
    Open a file with secure permissions (0o600).

    If creating a new file, it will have 0o600 permissions atomically.
    If the file already exists, it attempts to update permissions to 0o600.
    """
    # Ensure parent directory is secure if we might be creating the file
    if "w" in mode or "a" in mode or "x" in mode:
        ensure_secure_dir(path.parent)

    # If the file exists, update permissions before opening for potentially writing
    if path.exists():
        try:
            os.chmod(path, 0o600)
        except PermissionError:
            # Ignore if we don't have permission to chmod (e.g. read-only access to existing config)
            pass

    # Atomic creation with secure permissions if writing
    if "w" in mode or "x" in mode:
        # Map python modes to os flags
        flags = os.O_RDWR | os.O_CREAT
        if "x" in mode:
            flags |= os.O_EXCL
        else:
            flags |= os.O_TRUNC

        if "b" in mode:
            # Binary mode - handled by open()
            pass

        # Use os.open for atomic creation with mode
        fd = os.open(path, flags, mode=0o600)
        return os.fdopen(fd, mode, **kwargs)

    # Fallback to standard open for reading/appending
    f = open(path, mode, **kwargs)

    # Ensure 0o600 for new files (e.g. append mode)
    try:
        os.chmod(path, 0o600)
    except PermissionError:
        pass

    return f
