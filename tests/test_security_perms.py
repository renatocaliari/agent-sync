"""Permission enforcement tests for agent-sync."""

import os
import pytest
from pathlib import Path
from agent_sync.security import secure_open, ensure_secure_dir


def test_ensure_secure_dir_permissions(tmp_path):
    """Verify that ensure_secure_dir creates a directory with 0o700 permissions."""
    secure_dir = tmp_path / "secure_dir"
    ensure_secure_dir(secure_dir)

    assert secure_dir.exists()
    assert secure_dir.is_dir()

    # On Unix, check permissions
    if os.name != 'nt':
        mode = os.stat(secure_dir).st_mode
        assert oct(mode & 0o777) == '0o700'


def test_secure_open_permissions_creation(tmp_path):
    """Verify that secure_open creates a file with 0o600 permissions."""
    secure_file = tmp_path / "secure_file.txt"
    with secure_open(secure_file, "w") as f:
        f.write("sensitive data")

    assert secure_file.exists()

    # On Unix, check permissions
    if os.name != 'nt':
        mode = os.stat(secure_file).st_mode
        assert oct(mode & 0o777) == '0o600'


def test_secure_open_permissions_existing(tmp_path):
    """Verify that secure_open updates an existing file to 0o600 permissions."""
    secure_file = tmp_path / "existing_file.txt"

    # Create file with loose permissions
    secure_file.write_text("initial data")
    os.chmod(secure_file, 0o644)

    if os.name != 'nt':
        mode = os.stat(secure_file).st_mode
        assert oct(mode & 0o777) == '0o644'

    # Open with secure_open for writing
    with secure_open(secure_file, "w") as f:
        f.write("new sensitive data")

    # On Unix, check permissions updated
    if os.name != 'nt':
        mode = os.stat(secure_file).st_mode
        assert oct(mode & 0o777) == '0o600'


def test_secure_open_creates_parent_dir(tmp_path):
    """Verify that secure_open creates parent directories if they don't exist."""
    nested_file = tmp_path / "subdir" / "nested" / "file.txt"
    with secure_open(nested_file, "w") as f:
        f.write("data")

    assert nested_file.exists()
    assert nested_file.parent.exists()
    assert nested_file.parent.parent.exists()
