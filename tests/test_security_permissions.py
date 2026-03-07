"""Tests for security permissions of configuration and state files."""

import os
import stat
from pathlib import Path
from unittest.mock import patch, MagicMock
from agent_sync.config import Config
from agent_sync.sync import SyncManager

def test_config_permissions(tmp_path):
    """Test that Config creates directories and files with restricted permissions."""
    config_dir = tmp_path / "config"
    config_file = config_dir / "config.yaml"
    overrides_file = config_dir / "overrides.yaml"

    # Initialize Config
    config = Config(config_path=config_file, overrides_path=overrides_file)

    # Verify directory permissions (0o700)
    assert config_dir.exists()
    mode = os.stat(config_dir).st_mode
    assert stat.S_IMODE(mode) == 0o700

    # Save and verify file permissions (0o600)
    config.save()
    assert config_file.exists()
    mode = os.stat(config_file).st_mode
    assert stat.S_IMODE(mode) == 0o600

    # Save overrides and verify permissions
    config.save_overrides()
    assert overrides_file.exists()
    mode = os.stat(overrides_file).st_mode
    assert stat.S_IMODE(mode) == 0o600

def test_sync_manager_permissions(tmp_path):
    """Test that SyncManager creates directories and files with restricted permissions."""
    data_dir = tmp_path / "data"
    repo_dir = data_dir / "repo"
    state_file = data_dir / "sync-state.json"

    mock_config = MagicMock()
    mock_config.repo_url = "https://github.com/test/repo.git"

    with patch("agent_sync.sync.SyncManager.DATA_DIR", data_dir), \
         patch("agent_sync.sync.SyncManager.DEFAULT_REPO_DIR", repo_dir), \
         patch("agent_sync.sync.SyncManager.STATE_FILE", state_file):

        sync_manager = SyncManager(mock_config)

        # Verify directory permissions (0o700)
        assert data_dir.exists()
        assert stat.S_IMODE(os.stat(data_dir).st_mode) == 0o700

        assert repo_dir.exists()
        assert stat.S_IMODE(os.stat(repo_dir).st_mode) == 0o700

        # Save state and verify file permissions (0o600)
        sync_manager._save_state("test")
        assert state_file.exists()
        assert stat.S_IMODE(os.stat(state_file).st_mode) == 0o600

        # Save manifest and verify file permissions (0o600)
        manifest_file = repo_dir / ".agent-sync-manifest.json"
        sync_manager._save_manifest({"test": "data"})
        assert manifest_file.exists()
        assert stat.S_IMODE(os.stat(manifest_file).st_mode) == 0o600
