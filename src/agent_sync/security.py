"""Security utilities for agent-sync."""

import os
from pathlib import Path
from typing import Optional


def ensure_secure_dir(path: Path) -> None:
    """
    Ensure a directory exists and has restricted permissions (0o700).
    """
    if not path.exists():
        path.mkdir(parents=True, mode=0o700, exist_ok=True)

    # Even if it exists, ensure permissions are correct
    # Note: os.chmod behavior on Windows is limited, but it doesn't hurt.
    try:
        os.chmod(path, 0o700)
    except PermissionError:
        pass


def secure_open(path: Path, mode: str = "r", encoding: Optional[str] = "utf-8", **kwargs):
    """
    Open a file with restricted permissions (0o600).
    Uses the opener parameter to ensure the file is created with correct permissions.
    """
    def opener(path_str, flags):
        # Create with 0o600 permissions
        return os.open(path_str, flags, 0o600)

    # Ensure parent directory is secure
    ensure_secure_dir(path.parent)

    file_obj = open(path, mode, opener=opener, encoding=encoding, **kwargs)

    # If the file already existed, opener might not have changed its permissions
    # on some systems/filesystems. For existing files, we use fchmod to harden them.
    # fchmod is generally more secure as it works on the file descriptor.
    if "w" in mode or "a" in mode or "+" in mode:
        try:
            os.fchmod(file_obj.fileno(), 0o600)
        except (AttributeError, OSError):
            # Fallback for Windows or systems where fchmod is not available
            try:
                os.chmod(path, 0o600)
            except (OSError, PermissionError):
                pass

    return file_obj
