"""Security utilities for restricted file and directory operations."""

import os
from pathlib import Path
from typing import Union


def secure_open(
    path: Union[str, Path],
    mode: str = "w",
    permissions: int = 0o600,
    encoding: str = "utf-8",
):
    """
    Open a file with restricted permissions (default 0o600).

    Ensures that if the file is created, it has the specified permissions.
    If the file exists, it corrects the permissions.
    """
    path = Path(path)

    # Map Python open modes to os flags
    mode_map = {
        "w": os.O_WRONLY | os.O_CREAT | os.O_TRUNC,
        "wt": os.O_WRONLY | os.O_CREAT | os.O_TRUNC,
        "a": os.O_WRONLY | os.O_CREAT | os.O_APPEND,
        "at": os.O_WRONLY | os.O_CREAT | os.O_APPEND,
        "r": os.O_RDONLY,
        "rt": os.O_RDONLY,
        "r+": os.O_RDWR,
        "w+": os.O_RDWR | os.O_CREAT | os.O_TRUNC,
        "a+": os.O_RDWR | os.O_CREAT | os.O_APPEND,
    }

    flags = mode_map.get(mode)
    if flags is None:
        # Fallback for binary modes or others not explicitly mapped
        return open(path, mode, encoding=encoding if "b" not in mode else None)

    fd = os.open(path, flags, permissions)
    # Ensure permissions even if file already existed
    os.chmod(path, permissions)

    return os.fdopen(fd, mode, encoding=encoding if "b" not in mode else None)


def ensure_secure_dir(path: Union[str, Path], permissions: int = 0o700):
    """
    Ensure a directory exists and has restricted permissions (default 0o700).
    """
    path = Path(path)
    if not path.exists():
        os.makedirs(path, mode=permissions, exist_ok=True)

    # os.makedirs 'mode' argument is not always honored depending on umask
    # So we explicitly chmod the leaf directory
    os.chmod(path, permissions)
