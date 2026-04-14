import os
import stat
from pathlib import Path
import pytest
from agent_sync.security import secure_open, ensure_secure_dir

def test_secure_open_permissions(tmp_path):
    """Test that secure_open creates files with 0o600 permissions."""
    test_file = tmp_path / "test_secure.txt"

    with secure_open(test_file, "w") as f:
        f.write("test content")

    assert test_file.exists()

    # Get file permissions
    file_stat = os.stat(test_file)
    actual_mode = stat.S_IMODE(file_stat.st_mode)

    # Expected mode is 0o600
    assert actual_mode == 0o600

def test_secure_open_existing_file_permissions(tmp_path):
    """Test that secure_open corrects permissions on existing files."""
    test_file = tmp_path / "test_existing.txt"

    # Create with loose permissions
    test_file.write_text("initial content")
    os.chmod(test_file, 0o666)

    # Open with secure_open
    with secure_open(test_file, "a") as f:
        f.write("additional content")

    # Get file permissions
    file_stat = os.stat(test_file)
    actual_mode = stat.S_IMODE(file_stat.st_mode)

    # Expected mode is 0o600
    assert actual_mode == 0o600

def test_ensure_secure_dir_permissions(tmp_path):
    """Test that ensure_secure_dir creates directories with 0o700 permissions."""
    test_dir = tmp_path / "secure_dir"

    ensure_secure_dir(test_dir)

    assert test_dir.exists()
    assert test_dir.is_dir()

    # Get directory permissions
    dir_stat = os.stat(test_dir)
    actual_mode = stat.S_IMODE(dir_stat.st_mode)

    # Expected mode is 0o700
    assert actual_mode == 0o700

def test_ensure_secure_dir_existing_permissions(tmp_path):
    """Test that ensure_secure_dir corrects permissions on existing directories."""
    test_dir = tmp_path / "existing_loose_dir"

    # Create with loose permissions
    os.makedirs(test_dir, mode=0o777, exist_ok=True)
    os.chmod(test_dir, 0o777)

    # Apply ensure_secure_dir
    ensure_secure_dir(test_dir)

    # Get directory permissions
    dir_stat = os.stat(test_dir)
    actual_mode = stat.S_IMODE(dir_stat.st_mode)

    # Expected mode is 0o700
    assert actual_mode == 0o700
