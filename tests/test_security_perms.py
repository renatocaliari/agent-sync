"""Security tests for file and directory permissions."""

import os
import sys
import pytest
from pathlib import Path
from agent_sync.security import secure_open, ensure_secure_dir
from agent_sync.config import Config
from agent_sync.sync import SyncManager


def test_ensure_secure_dir(tmp_path):
    """Verify that ensure_secure_dir sets 0o700 permissions."""
    test_dir = tmp_path / "secure_dir"
    ensure_secure_dir(test_dir)

    assert test_dir.exists()
    assert test_dir.is_dir()

    # On Windows, os.chmod doesn't support 0o700 fully for directories in the same way as Unix
    if sys.platform != "win32":
        mode = os.stat(test_dir).st_mode
        assert oct(mode & 0o777) == "0o700"


def test_secure_open_creation(tmp_path):
    """Verify that secure_open creates files with 0o600 permissions."""
    test_file = tmp_path / "secure_file.txt"

    with secure_open(test_file, "w") as f:
        f.write("sensitive data")

    assert test_file.exists()

    if sys.platform != "win32":
        mode = os.stat(test_file).st_mode
        assert oct(mode & 0o777) == "0o600"


def test_secure_open_hardening(tmp_path):
    """Verify that secure_open hardens existing files to 0o600."""
    test_file = tmp_path / "existing_file.txt"
    test_file.write_text("initial data")

    # Set permissive permissions
    os.chmod(test_file, 0o666)

    with secure_open(test_file, "a") as f:
        f.write("\nmore data")

    if sys.platform != "win32":
        mode = os.stat(test_file).st_mode
        assert oct(mode & 0o777) == "0o600"


def test_config_save_permissions(tmp_path, monkeypatch):
    """Verify that Config.save() uses restricted permissions."""
    config_dir = tmp_path / "config"
    config_file = config_dir / "config.yaml"
    overrides_file = config_dir / "overrides.yaml"

    # Mock default paths
    monkeypatch.setattr("agent_sync.config.DEFAULT_CONFIG_DIR", config_dir)
    monkeypatch.setattr("agent_sync.config.DEFAULT_CONFIG_FILE", config_file)
    monkeypatch.setattr("agent_sync.config.DEFAULT_OVERRIDES_FILE", overrides_file)

    config = Config(config_path=config_file, overrides_path=overrides_file)
    config.save()
    config.save_overrides()

    if sys.platform != "win32":
        assert oct(os.stat(config_dir).st_mode & 0o777) == "0o700"
        assert oct(os.stat(config_file).st_mode & 0o777) == "0o600"
        assert oct(os.stat(overrides_file).st_mode & 0o777) == "0o600"


def test_sync_manager_permissions(tmp_path, monkeypatch):
    """Verify that SyncManager uses restricted permissions for state and repo."""
    data_dir = tmp_path / "data"
    repo_dir = data_dir / "repo"
    state_file = data_dir / "sync-state.json"

    # Mock data directory paths
    monkeypatch.setattr("agent_sync.sync.SyncManager.DATA_DIR", data_dir)
    monkeypatch.setattr("agent_sync.sync.SyncManager.DEFAULT_REPO_DIR", repo_dir)
    monkeypatch.setattr("agent_sync.sync.SyncManager.STATE_FILE", state_file)

    class MockConfig:
        repo_url = "https://github.com/owner/repo.git"

    sync_mgr = SyncManager(MockConfig())
    sync_mgr._save_state("test_action")

    if sys.platform != "win32":
        assert oct(os.stat(data_dir).st_mode & 0o777) == "0o700"
        assert oct(os.stat(repo_dir).st_mode & 0o777) == "0o700"
        assert oct(os.stat(state_file).st_mode & 0o777) == "0o600"
