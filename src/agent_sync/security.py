"""Security utilities for restricted file and directory operations."""

import os
from pathlib import Path
from typing import Any


def ensure_secure_dir(path: Path) -> None:
    """
    Ensure a directory exists with restricted permissions (0o700).

    Specifically avoids recursive modification of parent directories.
    """
    path.mkdir(parents=True, exist_ok=True)
    os.chmod(path, 0o700)


def secure_open(filepath: Path, mode: str, encoding: str = "utf-8", **kwargs: Any):
    """
    Open a file with restricted permissions (0o600).

    Uses the opener parameter of the built-in open() function to ensure
    restricted permissions during file creation.
    """
    def opener(path, flags):
        fd = os.open(path, flags, 0o600)
        try:
            os.fchmod(fd, 0o600)
        except (AttributeError, OSError):
            # fchmod not available on some platforms (e.g. Windows)
            pass
        return fd

    # Binary mode
    if "b" in mode:
        return open(filepath, mode, opener=opener, **kwargs)

    # Text mode
    return open(filepath, mode, encoding=encoding, opener=opener, **kwargs)
