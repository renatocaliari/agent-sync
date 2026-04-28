"""Tests for security permission enforcement."""

import os
import stat
from pathlib import Path
from agent_sync.security import secure_open, ensure_secure_dir


def test_secure_open_permissions(tmp_path):
    """Verify that secure_open creates files with 0o600 permissions."""
    test_file = tmp_path / "test_secure.txt"

    with secure_open(test_file, "w") as f:
        f.write("sensitive data")

    # Check permissions
    mode = os.stat(test_file).st_mode
    # stat.S_IMODE extracts the permission bits
    assert stat.S_IMODE(mode) == 0o600


def test_secure_open_harden_existing(tmp_path):
    """Verify that secure_open hardens existing files to 0o600."""
    test_file = tmp_path / "test_harden.txt"

    # Create with loose permissions
    test_file.write_text("loose data")
    os.chmod(test_file, 0o644)
    assert stat.S_IMODE(os.stat(test_file).st_mode) == 0o644

    # Open with secure_open
    with secure_open(test_file, "r") as f:
        pass

    # Check that permissions were hardened
    assert stat.S_IMODE(os.stat(test_file).st_mode) == 0o600


def test_ensure_secure_dir_permissions(tmp_path):
    """Verify that ensure_secure_dir creates directories with 0o700 permissions."""
    test_dir = tmp_path / "secure_subdir"

    ensure_secure_dir(test_dir)

    assert test_dir.exists()
    assert test_dir.is_dir()

    mode = os.stat(test_dir).st_mode
    assert stat.S_IMODE(mode) == 0o700


def test_ensure_secure_dir_harden_existing(tmp_path):
    """Verify that ensure_secure_dir hardens existing directories to 0o700."""
    test_dir = tmp_path / "harden_subdir"
    test_dir.mkdir()
    os.chmod(test_dir, 0o755)
    assert stat.S_IMODE(os.stat(test_dir).st_mode) == 0o755

    ensure_secure_dir(test_dir)

    assert stat.S_IMODE(os.stat(test_dir).st_mode) == 0o700
