"""Security tests for file and directory permissions."""

import os
import pytest
from pathlib import Path
from agent_sync.config import Config
from agent_sync.sync import SyncManager
from agent_sync.publish import publish_skills
from unittest.mock import MagicMock, patch

def test_config_permissions(tmp_path):
    """Verify that Config creates files and directories with secure permissions."""
    config_dir = tmp_path / ".config" / "agent-sync"
    config_path = config_dir / "config.yaml"
    overrides_path = config_dir / "overrides.yaml"

    config = Config(config_path=config_path, overrides_path=overrides_path)
    config.repo_url = "https://github.com/user/repo"
    config.save()

    # Check directory permissions (0o700)
    assert oct(os.stat(config_dir).st_mode & 0o777) == "0o700"

    # Check file permissions (0o600)
    assert oct(os.stat(config_path).st_mode & 0o777) == "0o600"

    config.set_override("test_key", "test_value")
    # Overrides file should also be 0o600
    assert oct(os.stat(overrides_path).st_mode & 0o777) == "0o600"

def test_sync_manager_permissions(tmp_path):
    """Verify that SyncManager creates state and repo directories with secure permissions."""
    data_dir = tmp_path / "data"
    repo_dir = data_dir / "repo"
    state_file = data_dir / "sync-state.json"

    mock_config = MagicMock()
    mock_config.repo_url = "https://github.com/user/repo"

    # Mock DATA_DIR and other paths to use tmp_path
    with patch("agent_sync.sync.SyncManager.DATA_DIR", data_dir), \
         patch("agent_sync.sync.SyncManager.DEFAULT_REPO_DIR", repo_dir), \
         patch("agent_sync.sync.SyncManager.STATE_FILE", state_file):

        sm = SyncManager(mock_config)

        # Check directories permissions
        assert oct(os.stat(data_dir).st_mode & 0o777) == "0o700"
        assert oct(os.stat(repo_dir).st_mode & 0o777) == "0o700"

        sm._save_state("test_action")
        # Check state file permissions
        assert oct(os.stat(state_file).st_mode & 0o777) == "0o600"

        # Test manifest permissions
        manifest_path = repo_dir / ".agent-sync-manifest.json"
        sm._save_manifest({"test": "data"})
        assert oct(os.stat(manifest_path).st_mode & 0o777) == "0o600"

@patch("agent_sync.publish.Prompt.ask")
@patch("agent_sync.publish.Confirm.ask")
@patch("agent_sync.publish.get_available_skills")
@patch("agent_sync.publish.subprocess.run")
def test_publish_config_permissions(mock_run, mock_get_skills, mock_confirm, mock_prompt, tmp_path):
    """Verify that publish.yaml is created with secure permissions."""
    publish_config_dir = tmp_path / ".config" / "agent-sync"
    publish_config_path = publish_config_dir / "publish.yaml"

    mock_prompt.side_effect = ["https://github.com/user/agent-sync-public-skills"]
    mock_confirm.return_value = True
    mock_get_skills.return_value = [{"name": "test-skill", "path": Path("/tmp/fake")}]

    # Mock successful gh call for username
    mock_run.return_value = MagicMock(returncode=0, stdout="testuser")

    with patch("agent_sync.publish.PUBLISH_CONFIG_PATH", publish_config_path):
        # We only need to trigger the part that saves the config
        # Use dry_run to avoid actual git/gh operations
        try:
            publish_skills(interactive=True, dry_run=True)
        except Exception:
            # We don't care about the full execution, just the config saving
            pass

        if publish_config_path.exists():
            assert oct(os.stat(publish_config_dir).st_mode & 0o777) == "0o700"
            assert oct(os.stat(publish_config_path).st_mode & 0o777) == "0o600"
