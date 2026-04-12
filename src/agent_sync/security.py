"""Security utilities for agent-sync."""

import os
from pathlib import Path


def secure_open(path, mode="w", permissions=0o600):
    """
    Open a file with restricted permissions (default 0o600).
    Ensures that the file is created with the specified permissions at the moment of creation.
    """
    path = Path(path).expanduser().resolve()

    # Ensure parent directory exists and is secure
    ensure_secure_dir(path.parent)

    # Use os.open to ensure permissions are set at creation time (ignoring umask)
    # We use O_WRONLY | os.O_CREAT | os.O_TRUNC for write mode "w"
    flags = os.O_WRONLY | os.O_CREAT
    if "a" in mode:
        flags |= os.O_APPEND
    else:
        flags |= os.O_TRUNC

    fd = os.open(path, flags, permissions)

    # Also ensure permissions on existing files are corrected
    os.chmod(path, permissions)

    return os.fdopen(fd, mode, encoding="utf-8")


def ensure_secure_dir(path, permissions=0o700):
    """
    Ensure a directory exists with restricted permissions (default 0o700).
    Applies permissions to the directory and ensures it is created securely.
    """
    path = Path(path).expanduser().resolve()

    if not path.exists():
        # Create parents if they don't exist
        # We don't use mkdir(parents=True) directly to ensure we can control permissions
        # of the created directories if needed, but for simplicity we rely on chmod
        path.mkdir(parents=True, mode=permissions, exist_ok=True)

    # Set permissions explicitly to override umask
    os.chmod(path, permissions)
