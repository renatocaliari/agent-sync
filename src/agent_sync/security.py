"""Security utilities for agent-sync."""

import os
from pathlib import Path


def secure_open(path, mode="r", encoding=None, errors=None, newline=None):
    """
    Open a file with secure permissions (0o600).

    If the file is being created, it will be created with 0o600.
    If it already exists, its permissions will be hardened to 0o600.
    """
    path = Path(path)

    def opener(path_str, flags):
        # Ensure we create with 0o600
        return os.open(path_str, flags, mode=0o600)

    f = open(path, mode, opener=opener, encoding=encoding, errors=errors, newline=newline)

    # Harden permissions of the existing file or just-created file
    # os.fchmod is only available on Unix-like systems
    if hasattr(os, 'fchmod'):
        try:
            os.fchmod(f.fileno(), 0o600)
        except OSError:
            # Some systems might not support fchmod on all file types
            pass
    elif hasattr(os, 'chmod'):
        # Fallback for Windows or systems without fchmod
        try:
            os.chmod(path, 0o600)
        except OSError:
            pass

    return f


def ensure_secure_dir(path) -> Path:
    """
    Ensure a directory exists and has secure permissions (0o700).
    """
    path = Path(path)
    path.mkdir(parents=True, exist_ok=True)
    os.chmod(path, 0o700)
    return path
