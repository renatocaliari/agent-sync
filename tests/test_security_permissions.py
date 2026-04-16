"""Tests for security permission enforcement."""

import os
import stat
from pathlib import Path
from agent_sync.security import secure_open, ensure_secure_dir


def get_permissions(path: Path) -> int:
    """Return the octal permission bits of a path."""
    return stat.S_IMODE(os.stat(path).st_mode)


def test_secure_open_creates_file_with_restricted_permissions(tmp_path):
    """Verify that secure_open creates a file with 0o600 permissions."""
    test_file = tmp_path / "secure_file.txt"

    with secure_open(test_file, "w") as f:
        f.write("sensitive data")

    assert test_file.exists()
    assert get_permissions(test_file) == 0o600


def test_secure_open_corrects_existing_file_permissions(tmp_path):
    """Verify that secure_open corrects permissions of an existing file to 0o600."""
    test_file = tmp_path / "permissive_file.txt"
    test_file.write_text("sensitive data")
    os.chmod(test_file, 0o666)

    assert get_permissions(test_file) == 0o666

    with secure_open(test_file, "w") as f:
        f.write("new sensitive data")

    assert get_permissions(test_file) == 0o600


def test_ensure_secure_dir_creates_dir_with_restricted_permissions(tmp_path):
    """Verify that ensure_secure_dir creates a directory with 0o700 permissions."""
    test_dir = tmp_path / "secure_dir"

    ensure_secure_dir(test_dir)

    assert test_dir.exists()
    assert test_dir.is_dir()
    assert get_permissions(test_dir) == 0o700


def test_ensure_secure_dir_corrects_existing_dir_permissions(tmp_path):
    """Verify that ensure_secure_dir corrects permissions of an existing directory to 0o700."""
    test_dir = tmp_path / "permissive_dir"
    test_dir.mkdir(mode=0o777)
    os.chmod(test_dir, 0o777)

    assert get_permissions(test_dir) == 0o777

    ensure_secure_dir(test_dir)

    assert get_permissions(test_dir) == 0o700


def test_secure_open_creates_parent_dirs_with_restricted_permissions(tmp_path):
    """Verify that secure_open creates missing parent directories with 0o700 permissions."""
    test_file = tmp_path / "nested" / "deep" / "secure_file.txt"

    with secure_open(test_file, "w") as f:
        f.write("sensitive data")

    assert test_file.exists()
    assert get_permissions(test_file) == 0o600
    assert get_permissions(test_file.parent) == 0o700
    assert get_permissions(test_file.parent.parent) == 0o700
