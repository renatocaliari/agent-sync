"""Security utilities for agent-sync."""

import os
from pathlib import Path
from typing import Union


def secure_open(path: Union[str, Path], mode: str = "w", encoding: str = "utf-8", permissions: int = 0o600):
    """
    Open a file with restricted permissions (default 0o600).

    Ensures that if the file is created, it has restricted permissions,
    and if it exists, its permissions are corrected.
    """
    path = Path(path)

    # Map Python open modes to os flags
    flags_map = {
        "w": os.O_WRONLY | os.O_CREAT | os.O_TRUNC,
        "a": os.O_WRONLY | os.O_CREAT | os.O_APPEND,
        "r": os.O_RDONLY,
        "r+": os.O_RDWR,
    }

    if mode not in flags_map:
        raise ValueError(f"Unsupported mode: {mode}")

    flags = flags_map[mode]

    # Create directory if it doesn't exist (with secure permissions)
    ensure_secure_dir(path.parent)

    # os.open returns a file descriptor with the specified permissions
    # if the file is created.
    fd = os.open(path, flags, permissions)

    # Ensure permissions are strictly enforced even if file already existed
    try:
        os.chmod(path, permissions)
    except OSError:
        # Might fail if we don't own the file, but os.open would likely have failed too
        pass

    return os.fdopen(fd, mode, encoding=encoding)


def ensure_secure_dir(path: Union[str, Path], permissions: int = 0o700):
    """
    Ensure a directory exists with restricted permissions (default 0o700).
    """
    path = Path(path)

    # Identify which parents need to be created
    to_create = []
    current = path
    while current and not current.exists() and current != current.parent:
        to_create.append(current)
        current = current.parent

    if to_create:
        # Create them
        os.makedirs(path, mode=permissions, exist_ok=True)
        # Correct permissions for all created directories
        for p in to_create:
            try:
                os.chmod(p, permissions)
            except OSError:
                pass
    elif path.exists():
        # Directory already exists, just ensure permissions
        try:
            os.chmod(path, permissions)
        except OSError:
            pass
