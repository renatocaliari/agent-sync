"""Tests for security permission enforcement."""

import os
import stat
import pytest
from pathlib import Path
from agent_sync.security import secure_open, ensure_secure_dir


def test_ensure_secure_dir_permissions(tmp_path):
    """Verify that ensure_secure_dir sets 0o700 permissions."""
    secure_dir = tmp_path / "secure_dir"
    ensure_secure_dir(secure_dir)

    assert secure_dir.exists()
    mode = secure_dir.stat().st_mode
    # Check for 0o700 (drwx------)
    assert stat.S_IMODE(mode) == 0o700


def test_secure_open_new_file_permissions(tmp_path):
    """Verify that secure_open creates new files with 0o600 permissions."""
    secure_file = tmp_path / "secure_file.txt"

    with secure_open(secure_file, "w") as f:
        f.write("sensitive data")

    assert secure_file.exists()
    mode = secure_file.stat().st_mode
    # Check for 0o600 (-rw-------)
    assert stat.S_IMODE(mode) == 0o600


def test_secure_open_existing_file_hardening(tmp_path):
    """Verify that secure_open hardens existing files to 0o600."""
    insecure_file = tmp_path / "insecure.txt"
    insecure_file.write_text("initial data")
    # Set broad permissions (e.g., 0o666)
    os.chmod(insecure_file, 0o666)

    # Open with secure_open in append mode
    with secure_open(insecure_file, "a") as f:
        f.write(" more data")

    mode = insecure_file.stat().st_mode
    # Should now be 0o600
    assert stat.S_IMODE(mode) == 0o600


def test_secure_open_creates_parent_dirs(tmp_path):
    """Verify that secure_open creates missing parent directories securely."""
    nested_file = tmp_path / "subdir" / "nested.txt"

    with secure_open(nested_file, "w") as f:
        f.write("nested data")

    assert nested_file.exists()
    assert nested_file.parent.exists()

    # Parent dir should be 0o700
    dir_mode = nested_file.parent.stat().st_mode
    assert stat.S_IMODE(dir_mode) == 0o700

    # File should be 0o600
    file_mode = nested_file.stat().st_mode
    assert stat.S_IMODE(file_mode) == 0o600
