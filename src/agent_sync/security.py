"""Security utilities for agent-sync."""

import os
from pathlib import Path
from typing import IO, Any


def secure_open(path: str | Path, mode: str = "w", permissions: int = 0o600, encoding: str = "utf-8") -> IO[Any]:
    """
    Open a file with restricted permissions.

    If the file is being created, it will be created with the specified permissions
    (default 0o600 - read/write for owner only).

    Args:
        path: Path to the file.
        mode: Open mode ('w', 'a', 'r', 'r+').
        permissions: Octal permissions (default 0o600).
        encoding: Text encoding (default 'utf-8').

    Returns:
        A file object.
    """
    path = Path(path)

    # Map mode to os flags
    flags = 0
    if "w" in mode:
        flags |= os.O_WRONLY | os.O_CREAT | os.O_TRUNC
    elif "a" in mode:
        flags |= os.O_WRONLY | os.O_CREAT | os.O_APPEND
    elif "r+" in mode:
        flags |= os.O_RDWR
    elif "r" in mode:
        flags |= os.O_RDONLY
    else:
        raise ValueError(f"Unsupported mode: {mode}")

    # For opening existing files in read mode, we don't need O_CREAT
    # But for write modes, we want to ensure permissions if it's new

    # Use os.open to ensure atomicity of creation and permissions.
    # Note: os.open's mode is modified by umask, so we chmod explicitly.
    fd = os.open(path, flags, permissions)

    try:
        # Explicitly set permissions in case umask interfered
        if "w" in mode or "a" in mode:
            if hasattr(os, "fchmod"):
                os.fchmod(fd, permissions)
            else:
                os.chmod(path, permissions)

        return os.fdopen(fd, mode, encoding=encoding)
    except Exception:
        os.close(fd)
        raise


def ensure_secure_dir(path: str | Path, permissions: int = 0o700) -> None:
    """
    Ensure a directory exists and has restricted permissions.

    Only the specified directory is hardened, avoiding intrusive modifications
    to standard system or user parent directories.

    Args:
        path: Path to the directory.
        permissions: Octal permissions (default 0o700 - rwx for owner only).
    """
    path = Path(path)

    if not path.exists():
        path.mkdir(parents=True, exist_ok=True)

    # Explicitly set permissions for the target directory only
    os.chmod(path, permissions)
