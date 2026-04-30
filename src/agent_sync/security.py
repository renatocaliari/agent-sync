"""Security utilities for agent-sync."""

import os
from pathlib import Path
from typing import Any


def secure_open(path: str | Path, mode: str = "r", **kwargs: Any):
    """
    Open a file with restricted permissions (0o600).

    If the file is being created, it will be created with 0o600 permissions.
    If the file already exists, its permissions will be updated to 0o600 if opened for writing.
    """
    path_obj = Path(path)

    def opener(path_str: str, flags: int) -> int:
        return os.open(path_str, flags, 0o600)

    # Ensure parent directory exists
    path_obj.parent.mkdir(parents=True, exist_ok=True)

    f = open(path_obj, mode, opener=opener, **kwargs)

    # If opened for writing/appending, ensure permissions are 0o600
    if any(m in mode for m in "wax+"):
        try:
            os.fchmod(f.fileno(), 0o600)
        except (AttributeError, OSError):
            # Fallback for systems that don't support fchmod (e.g. Windows)
            try:
                os.chmod(path_obj, 0o600)
            except OSError:
                pass

    return f


def ensure_secure_dir(path: str | Path) -> Path:
    """
    Ensure a directory exists with restricted permissions (0o700).
    """
    path_obj = Path(path)
    path_obj.mkdir(parents=True, exist_ok=True)

    try:
        os.chmod(path_obj, 0o700)
    except OSError:
        pass

    return path_obj
