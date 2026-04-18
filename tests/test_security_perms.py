"""Tests for secure file and directory permissions."""

import os
import stat
from pathlib import Path
from agent_sync.security import secure_open, ensure_secure_dir


def test_secure_open_permissions(tmp_path):
    """Verify that secure_open creates files with 0o600 permissions."""
    test_file = tmp_path / "secret.txt"

    with secure_open(test_file, "w") as f:
        f.write("sensitive data")

    assert test_file.exists()
    mode = test_file.stat().st_mode
    # mode includes file type bits, so we mask them
    assert stat.S_IMODE(mode) == 0o600


def test_secure_open_existing_file(tmp_path):
    """Verify that secure_open enforces 0o600 on existing files."""
    test_file = tmp_path / "existing.txt"
    test_file.write_text("initial data")
    # Set permissive mode
    os.chmod(test_file, 0o644)
    assert stat.S_IMODE(test_file.stat().st_mode) == 0o644

    with secure_open(test_file, "a") as f:
        f.write(" more data")

    assert stat.S_IMODE(test_file.stat().st_mode) == 0o600


def test_ensure_secure_dir_permissions(tmp_path):
    """Verify that ensure_secure_dir creates directories with 0o700 permissions."""
    test_dir = tmp_path / "secure_config"

    ensure_secure_dir(test_dir)

    assert test_dir.exists()
    assert test_dir.is_dir()
    mode = test_dir.stat().st_mode
    assert stat.S_IMODE(mode) == 0o700


def test_ensure_secure_dir_existing(tmp_path):
    """Verify that ensure_secure_dir enforces 0o700 on existing directories."""
    test_dir = tmp_path / "existing_dir"
    test_dir.mkdir(mode=0o755)
    os.chmod(test_dir, 0o755)
    assert stat.S_IMODE(test_dir.stat().st_mode) == 0o755

    ensure_secure_dir(test_dir)

    assert stat.S_IMODE(test_dir.stat().st_mode) == 0o700
