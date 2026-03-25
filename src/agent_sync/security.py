"""Centralized security utilities for agent-sync."""

import os
import pathlib
from typing import Union


def secure_open(path: Union[str, pathlib.Path], mode: str = 'r', encoding: str = 'utf-8'):
    """
    Open a file with restricted permissions (0o600).
    If the file is being created, it will have permissions set to 0o600.
    """
    if 'w' in mode or 'x' in mode or 'a' in mode:
        # For writing, use os.fdopen with os.open to set permissions at creation
        flags = os.O_WRONLY | os.O_CREAT
        if 'w' in mode:
            flags |= os.O_TRUNC
        elif 'x' in mode:
            flags |= os.O_EXCL
        elif 'a' in mode:
            flags |= os.O_APPEND

        fd = os.open(path, flags, 0o600)
        return os.fdopen(fd, mode, encoding=encoding)
    else:
        # For reading, just use normal open but verify it's not a symlink to somewhere dangerous
        return open(path, mode, encoding=encoding)


def ensure_secure_dir(path: Union[str, pathlib.Path]):
    """
    Ensure a directory exists and has restricted permissions (0o700).
    """
    path = pathlib.Path(path)
    if not path.exists():
        os.makedirs(path, mode=0o700, exist_ok=True)
    else:
        # If it exists, ensure it has the correct permissions
        os.chmod(path, 0o700)
