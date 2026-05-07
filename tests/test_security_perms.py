"""Tests for security permission enforcement."""

import os
import stat
from pathlib import Path
from agent_sync.security import secure_open, ensure_secure_dir


def test_ensure_secure_dir(tmp_path):
    """Verify that ensure_secure_dir sets 0o700 permissions."""
    test_dir = tmp_path / "secure_dir"
    ensure_secure_dir(test_dir)

    assert test_dir.exists()
    assert test_dir.is_dir()

    mode = test_dir.stat().st_mode
    # 0o700 is S_IRWXU
    assert stat.S_IMODE(mode) == 0o700


def test_secure_open_new_file(tmp_path):
    """Verify that secure_open sets 0o600 permissions on new file creation."""
    test_file = tmp_path / "secure_file.txt"

    with secure_open(test_file, "w") as f:
        f.write("sensitive data")

    assert test_file.exists()

    mode = test_file.stat().st_mode
    # 0o600 is S_IRUSR | S_IWUSR
    assert stat.S_IMODE(mode) == 0o600


def test_secure_open_existing_file(tmp_path):
    """Verify that secure_open hardens existing files to 0o600."""
    test_file = tmp_path / "existing_file.txt"

    # Create file with loose permissions
    test_file.write_text("initial data")
    os.chmod(test_file, 0o644)
    assert stat.S_IMODE(test_file.stat().st_mode) == 0o644

    # Open with secure_open
    with secure_open(test_file, "r") as f:
        content = f.read()
        assert content == "initial data"

    # Should now be 0o600
    assert stat.S_IMODE(test_file.stat().st_mode) == 0o600


def test_secure_open_creates_parent_dir(tmp_path):
    """Verify that secure_open creates parent directory with 0o700."""
    parent_dir = tmp_path / "new_parent"
    test_file = parent_dir / "file.txt"

    assert not parent_dir.exists()

    with secure_open(test_file, "w") as f:
        f.write("data")

    assert parent_dir.exists()
    assert stat.S_IMODE(parent_dir.stat().st_mode) == 0o700
    assert stat.S_IMODE(test_file.stat().st_mode) == 0o600
