
import pytest
from src.agent_sync.validators import validate_repo_name, validate_github_url

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

import os
from src.agent_sync.security import secure_open, ensure_secure_dir

def test_secure_open_permissions(tmp_path):
    test_file = tmp_path / "subdir" / "test.txt"

    with secure_open(test_file, "w") as f:
        f.write("test")

    # Check file permissions
    mode = os.stat(test_file).st_mode
    assert (mode & 0o777) == 0o600

    # Check parent directory permissions
    dir_mode = os.stat(test_file.parent).st_mode
    assert (dir_mode & 0o777) == 0o700

def test_ensure_secure_dir_permissions(tmp_path):
    test_dir = tmp_path / "secure_dir"
    ensure_secure_dir(test_dir)

    mode = os.stat(test_dir).st_mode
    assert (mode & 0o777) == 0o700

def test_secure_open_existing_file(tmp_path):
    test_file = tmp_path / "existing.txt"
    test_file.write_text("initial")
    os.chmod(test_file, 0o644)

    with secure_open(test_file, "w") as f:
        f.write("updated")

    mode = os.stat(test_file).st_mode
    assert (mode & 0o777) == 0o600
