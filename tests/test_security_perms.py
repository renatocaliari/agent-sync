import os
import pytest
from pathlib import Path
from src.agent_sync.security import ensure_secure_dir, secure_open

def test_ensure_secure_dir_permissions(tmp_path):
    """Verify that ensure_secure_dir creates directories with 0o700 permissions."""
    test_dir = tmp_path / "secure_dir"
    ensure_secure_dir(test_dir)

    assert test_dir.exists()
    assert test_dir.is_dir()

    # Check permissions
    mode = os.stat(test_dir).st_mode
    assert (mode & 0o777) == 0o700

def test_secure_open_permissions(tmp_path):
    """Verify that secure_open creates files with 0o600 permissions."""
    test_file = tmp_path / "secure_file.txt"

    with secure_open(test_file, "w") as f:
        f.write("sensitive data")

    assert test_file.exists()

    # Check permissions
    mode = os.stat(test_file).st_mode
    assert (mode & 0o777) == 0o600

def test_secure_open_existing_file_permissions(tmp_path):
    """Verify that secure_open updates permissions of existing files to 0o600."""
    test_file = tmp_path / "existing_file.txt"

    # Create file with loose permissions
    test_file.write_text("initial data")
    os.chmod(test_file, 0o666)

    # Check initial permissions
    assert (os.stat(test_file).st_mode & 0o777) == 0o666

    # Re-open with secure_open
    with secure_open(test_file, "a") as f:
        f.write("\nmore data")

    # Check updated permissions
    assert (os.stat(test_file).st_mode & 0o777) == 0o600

def test_secure_open_modes(tmp_path):
    """Verify that secure_open handles different modes correctly."""
    test_file = tmp_path / "modes_file.txt"

    # Write mode
    with secure_open(test_file, "w") as f:
        f.write("line 1")
    assert test_file.read_text() == "line 1"

    # Append mode
    with secure_open(test_file, "a") as f:
        f.write("\nline 2")
    assert test_file.read_text() == "line 1\nline 2"

    # Read mode
    with secure_open(test_file, "r") as f:
        content = f.read()
    assert content == "line 1\nline 2"

def test_secure_open_binary_mode(tmp_path):
    """Verify that secure_open handles binary mode correctly."""
    test_file = tmp_path / "binary_file.bin"
    data = b"\x00\x01\x02\x03"

    with secure_open(test_file, "wb") as f:
        f.write(data)

    assert test_file.read_bytes() == data
    assert (os.stat(test_file).st_mode & 0o777) == 0o600
