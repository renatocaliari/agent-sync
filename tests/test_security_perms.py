"""Tests for security permission enforcement."""

import os
import stat
import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch
from agent_sync.security import secure_open, ensure_secure_dir
from agent_sync.config import Config
from agent_sync.sync import SyncManager


def test_ensure_secure_dir_permissions(tmp_path):
    """Verify ensure_secure_dir sets 0o700 permissions."""
    test_dir = tmp_path / "secure_dir"
    ensure_secure_dir(test_dir)

    assert test_dir.exists()
    mode = stat.S_IMODE(os.stat(test_dir).st_mode)
    assert mode == 0o700


def test_secure_open_creation_permissions(tmp_path):
    """Verify secure_open creates files with 0o600 permissions."""
    test_file = tmp_path / "secure_file.txt"
    with secure_open(test_file, "w") as f:
        f.write("sensitive data")

    assert test_file.exists()
    mode = stat.S_IMODE(os.stat(test_file).st_mode)
    assert mode == 0o600


def test_secure_open_existing_hardening(tmp_path):
    """Verify secure_open hardens existing files to 0o600."""
    test_file = tmp_path / "loose_file.txt"
    test_file.write_text("initial data")
    os.chmod(test_file, 0o644)

    # Verify it's loose
    assert stat.S_IMODE(os.stat(test_file).st_mode) == 0o644

    # Harden it
    with secure_open(test_file, "r") as f:
        pass

    # Verify it's hardened
    assert stat.S_IMODE(os.stat(test_file).st_mode) == 0o600


def test_config_saves_with_restricted_permissions(tmp_path):
    """Verify Config.save() creates files with 0o600 permissions."""
    config_file = tmp_path / "config.yaml"
    overrides_file = tmp_path / "overrides.yaml"

    # Mock platformdirs to use tmp_path
    with patch("agent_sync.config.DEFAULT_CONFIG_FILE", config_file), \
         patch("agent_sync.config.DEFAULT_OVERRIDES_FILE", overrides_file):

        config = Config()
        config.save()
        config.save_overrides()

        assert stat.S_IMODE(os.stat(config_file).st_mode) == 0o600
        assert stat.S_IMODE(os.stat(overrides_file).st_mode) == 0o600
        assert stat.S_IMODE(os.stat(config_file.parent).st_mode) == 0o700


def test_sync_manager_saves_with_restricted_permissions(tmp_path):
    """Verify SyncManager state and manifest have 0o600 permissions."""
    data_dir = tmp_path / "data"
    repo_dir = data_dir / "repo"
    state_file = data_dir / "sync-state.json"
    manifest_file = repo_dir / ".agent-sync-manifest.json"

    # Mock Config
    mock_config = MagicMock()
    mock_config.repo_url = "https://github.com/user/repo.git"

    with patch("agent_sync.sync.user_data_dir", return_value=str(data_dir)):
        # Re-initialize paths because they are class attributes
        with patch.object(SyncManager, 'DATA_DIR', data_dir), \
             patch.object(SyncManager, 'DEFAULT_REPO_DIR', repo_dir), \
             patch.object(SyncManager, 'STATE_FILE', state_file), \
             patch.object(SyncManager, 'MANIFEST_FILE', manifest_file):

            manager = SyncManager(mock_config)
            manager._save_state("test")

            # Create manifest
            repo_dir.mkdir(parents=True, exist_ok=True)
            manager._save_manifest({"test": "data"})

            assert stat.S_IMODE(os.stat(state_file).st_mode) == 0o600
            assert stat.S_IMODE(os.stat(manifest_file).st_mode) == 0o600
            assert stat.S_IMODE(os.stat(data_dir).st_mode) == 0o700
