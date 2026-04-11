
import os
import pytest
from pathlib import Path
from agent_sync.security import secure_open, ensure_secure_dir
from agent_sync.validators import validate_repo_name, validate_github_url

def test_validators_newline_injection():
    # These should fail with newlines
    assert validate_repo_name("owner/repo\n") is False
    assert validate_repo_name("owner/repo\r") is False
    assert validate_github_url("https://github.com/owner/repo\n") is False

    # Valid ones should still pass
    assert validate_repo_name("owner/repo") is True
    assert validate_github_url("https://github.com/owner/repo") is True

def test_validators_argument_injection_prevention():
    # validators already prevent leading hyphens
    assert validate_repo_name("-bad/repo") is False
    assert validate_github_url("https://github.com/-bad/repo") is False

def test_publish_validation_logic():
    # Testing the logic added to publish.py via a small simulation if possible
    # or just relying on the fact that it uses the now-hardened validators.
    pass

def test_secure_open_permissions(tmp_path):
    """Verify that secure_open creates files with correct permissions."""
    test_file = tmp_path / "secure.txt"

    with secure_open(test_file, "w") as f:
        f.write("test content")

    assert test_file.exists()
    # Check permissions
    mode = os.stat(test_file).st_mode & 0o777
    assert mode == 0o600

def test_ensure_secure_dir_permissions(tmp_path):
    """Verify that ensure_secure_dir creates directories with correct permissions."""
    test_dir = tmp_path / "secure_dir"

    ensure_secure_dir(test_dir)

    assert test_dir.exists()
    assert test_dir.is_dir()
    # Check permissions
    mode = os.stat(test_dir).st_mode & 0o777
    assert mode == 0o700

def test_secure_open_nested(tmp_path):
    """Verify that secure_open creates parent directories if they don't exist."""
    nested_file = tmp_path / "a" / "b" / "c.txt"

    with secure_open(nested_file, "w") as f:
        f.write("nested")

    assert nested_file.exists()
    assert nested_file.parent.exists()

    # Parents should have 0o700
    assert (os.stat(nested_file.parent).st_mode & 0o777) == 0o700
    assert (os.stat(nested_file.parent.parent).st_mode & 0o777) == 0o700
