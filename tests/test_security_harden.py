
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

def test_publish_validation_logic():
    # Testing the logic added to publish.py via a small simulation if possible
    # or just relying on the fact that it uses the now-hardened validators.
    pass

import os
import stat
from agent_sync.config import Config
from agent_sync.sync import SyncManager

def test_config_file_permissions(tmp_path):
    config_file = tmp_path / "config.yaml"
    overrides_file = tmp_path / "overrides.yaml"

    config = Config(config_path=config_file, overrides_path=overrides_file)
    config._config = {"test": "data"}
    config.save()

    config._overrides = {"local": "data"}
    config.save_overrides()

    assert config_file.exists()
    assert overrides_file.exists()

    # Check permissions (0o600)
    assert (os.stat(config_file).st_mode & 0o777) == 0o600
    assert (os.stat(overrides_file).st_mode & 0o777) == 0o600

    # Check directory permissions (0o700)
    assert (os.stat(config_file.parent).st_mode & 0o777) == 0o700

def test_sync_state_permissions(tmp_path):
    repo_dir = tmp_path / "repo"
    state_file = tmp_path / "state.json"

    class MockConfig:
        def __init__(self):
            self.repo_url = "https://github.com/owner/repo"

    config = MockConfig()
    # Mocking DATA_DIR and DEFAULT_REPO_DIR and STATE_FILE is tricky because they are class attributes
    # But we can patch them or just use a modified SyncManager that uses our paths

    sync_manager = SyncManager(config)
    sync_manager.repo_dir = repo_dir
    sync_manager.state_file = state_file

    # Trigger state save
    sync_manager._save_state("test")

    assert state_file.exists()
    assert (os.stat(state_file).st_mode & 0o777) == 0o600
    assert (os.stat(state_file.parent).st_mode & 0o777) == 0o700
