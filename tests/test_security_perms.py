"""Security tests for file and directory permissions."""

import os
import stat

from agent_sync.security import ensure_secure_dir, secure_open


def test_secure_open_permissions(tmp_path):
    """Verify that secure_open creates files with 0o600 permissions."""
    test_file = tmp_path / "secret.txt"

    with secure_open(test_file, "w") as f:
        f.write("sensitive data")

    # Check permissions
    mode = os.stat(test_file).st_mode
    # Get only the permission bits
    perms = stat.S_IMODE(mode)

    # 0o600 = 384 in decimal
    assert perms == 0o600


def test_secure_open_existing_file_hardening(tmp_path):
    """Verify that secure_open hardens existing files to 0o600."""
    test_file = tmp_path / "existing.txt"
    test_file.write_text("initial content")

    # Set loose permissions
    os.chmod(test_file, 0o666)
    assert stat.S_IMODE(os.stat(test_file).st_mode) == 0o666

    # Open with secure_open
    with secure_open(test_file, "a") as f:
        f.write(" more content")

    # Should now be 0o600
    perms = stat.S_IMODE(os.stat(test_file).st_mode)
    assert perms == 0o600


def test_ensure_secure_dir_permissions(tmp_path):
    """Verify that ensure_secure_dir creates directories with 0o700 permissions."""
    test_dir = tmp_path / "secure_subdir"

    returned_path = ensure_secure_dir(test_dir)

    assert returned_path == test_dir
    assert test_dir.exists()
    assert test_dir.is_dir()

    # Check permissions
    mode = os.stat(test_dir).st_mode
    perms = stat.S_IMODE(mode)

    # 0o700 = 448 in decimal
    assert perms == 0o700


def test_ensure_secure_dir_existing_hardening(tmp_path):
    """Verify that ensure_secure_dir hardens existing directories to 0o700."""
    test_dir = tmp_path / "existing_dir"
    test_dir.mkdir()

    # Set loose permissions
    os.chmod(test_dir, 0o777)
    assert stat.S_IMODE(os.stat(test_dir).st_mode) == 0o777

    # Harden it
    ensure_secure_dir(test_dir)

    # Should now be 0o700
    perms = stat.S_IMODE(os.stat(test_dir).st_mode)
    assert perms == 0o700
