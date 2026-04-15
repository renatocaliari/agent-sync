"""Security permission tests for agent-sync."""

import os
import pytest
from pathlib import Path
from agent_sync.security import secure_open, ensure_secure_dir


def test_ensure_secure_dir(tmp_path):
    """Verify that ensure_secure_dir creates directories with 0o700 permissions."""
    test_dir = tmp_path / "secure_dir"
    ensure_secure_dir(test_dir)

    assert test_dir.exists()
    assert test_dir.is_dir()

    # Check permissions (0o700)
    mode = os.stat(test_dir).st_mode
    assert (mode & 0o777) == 0o700


def test_ensure_secure_dir_existing(tmp_path):
    """Verify that ensure_secure_dir corrects permissions of existing directories."""
    test_dir = tmp_path / "existing_dir"
    test_dir.mkdir(mode=0o755)
    os.chmod(test_dir, 0o755) # Ensure it's 0o755

    ensure_secure_dir(test_dir)

    mode = os.stat(test_dir).st_mode
    assert (mode & 0o777) == 0o700


def test_secure_open_write(tmp_path):
    """Verify that secure_open creates files with 0o600 permissions."""
    test_file = tmp_path / "secure_file.txt"

    with secure_open(test_file, "w") as f:
        f.write("sensitive data")

    assert test_file.exists()

    # Check permissions (0o600)
    mode = os.stat(test_file).st_mode
    assert (mode & 0o777) == 0o600


def test_secure_open_existing(tmp_path):
    """Verify that secure_open corrects permissions of existing files."""
    test_file = tmp_path / "existing_file.txt"
    test_file.write_text("initial data")
    os.chmod(test_file, 0o644)

    with secure_open(test_file, "w") as f:
        f.write("new sensitive data")

    mode = os.stat(test_file).st_mode
    assert (mode & 0o777) == 0o600


def test_secure_open_append(tmp_path):
    """Verify that secure_open works with append mode."""
    test_file = tmp_path / "append_file.txt"

    with secure_open(test_file, "a") as f:
        f.write("part 1")

    with secure_open(test_file, "a") as f:
        f.write("part 2")

    assert test_file.read_text() == "part 1part 2"
    mode = os.stat(test_file).st_mode
    assert (mode & 0o777) == 0o600
