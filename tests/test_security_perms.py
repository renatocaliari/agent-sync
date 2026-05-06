"""Tests for security permission enforcement."""

import os
import pytest
from pathlib import Path
from agent_sync.security import secure_open, ensure_secure_dir


@pytest.mark.skipif(os.name == 'nt', reason="Permissions work differently on Windows")
def test_ensure_secure_dir_permissions(tmp_path):
    """Verify that ensure_secure_dir sets 0o700 permissions."""
    test_dir = tmp_path / "secure_dir"
    ensure_secure_dir(test_dir)

    assert test_dir.exists()
    assert test_dir.is_dir()

    # Check permissions (only looking at the last 3 octets)
    mode = os.stat(test_dir).st_mode
    assert (mode & 0o777) == 0o700


@pytest.mark.skipif(os.name == 'nt', reason="Permissions work differently on Windows")
def test_secure_open_creation_permissions(tmp_path):
    """Verify that secure_open creates files with 0o600 permissions."""
    test_file = tmp_path / "secure_file.txt"

    with secure_open(test_file, "w") as f:
        f.write("sensitive data")

    assert test_file.exists()

    # Check permissions
    mode = os.stat(test_file).st_mode
    assert (mode & 0o777) == 0o600


@pytest.mark.skipif(os.name == 'nt', reason="Permissions work differently on Windows")
def test_secure_open_hardening_existing_file(tmp_path):
    """Verify that secure_open hardens existing files to 0o600."""
    test_file = tmp_path / "existing_file.txt"

    # Create file with loose permissions
    test_file.write_text("initial data")
    os.chmod(test_file, 0o644)

    assert (os.stat(test_file).st_mode & 0o777) == 0o644

    # Open with secure_open in write mode
    with secure_open(test_file, "w") as f:
        f.write("new sensitive data")

    # Check permissions are now hardened
    mode = os.stat(test_file).st_mode
    assert (mode & 0o777) == 0o600


@pytest.mark.skipif(os.name == 'nt', reason="Permissions work differently on Windows")
def test_secure_open_read_mode_no_hardening(tmp_path):
    """Verify that secure_open in read mode doesn't change permissions."""
    test_file = tmp_path / "read_only_file.txt"

    # Create file with specific permissions
    test_file.write_text("data")
    os.chmod(test_file, 0o644)

    # Open with secure_open in read mode
    with secure_open(test_file, "r") as f:
        assert f.read() == "data"

    # Check permissions remain unchanged
    mode = os.stat(test_file).st_mode
    assert (mode & 0o777) == 0o644
