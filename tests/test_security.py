"""Security regression tests for agent-sync."""

import pytest
from pathlib import Path
from agent_sync.validators import validate_skill_name, validate_repo_name, validate_github_url
from agent_sync.skills_delete import SkillsDeleter


def test_validate_skill_name_security():
    """Verify that validate_skill_name blocks dangerous names."""
    # Safe names
    assert validate_skill_name("my-skill") is True
    assert validate_skill_name("skill.v1") is True
    assert validate_skill_name("skill_2") is True

    # Path traversal attempts
    assert validate_skill_name("../dangerous") is False
    assert validate_skill_name("..") is False
    assert validate_skill_name("/") is False
    assert validate_skill_name("/etc/passwd") is False
    assert validate_skill_name("skills/../base") is False

    # Newline injection
    assert validate_skill_name("skill\n") is False
    assert validate_skill_name("skill\r\n") is False

    # Shell characters
    assert validate_skill_name("skill;ls") is False
    assert validate_skill_name("skill|rm") is False
    assert validate_skill_name("skill&whoami") is False
    assert validate_skill_name("skill`id`") is False
    assert validate_skill_name("skill$(id)") is False


def test_validate_repo_name_newline_injection():
    """Verify that validate_repo_name blocks newline injection."""
    assert validate_repo_name("repo\n") is False
    assert validate_repo_name("repo\r") is False
    assert validate_repo_name("owner/repo\n") is False


def test_validate_github_url_newline_injection():
    """Verify that validate_github_url blocks newline injection."""
    assert validate_github_url("https://github.com/owner/repo\n") is False
    assert validate_github_url("https://github.com/owner/repo\r.git") is False


def test_skills_deleter_path_traversal_blocking(tmp_path, monkeypatch):
    """Verify that SkillsDeleter blocks path traversal attempts."""
    # Setup mock environment
    hub_dir = tmp_path / "hub"
    hub_dir.mkdir()

    # Create a dummy skill
    skill_dir = hub_dir / "my-skill"
    skill_dir.mkdir()
    (skill_dir / "SKILL.md").write_text("dummy")

    # Create a file outside the hub
    outside_file = tmp_path / "secret.txt"
    outside_file.write_text("secret content")

    class MockConfig:
        def __init__(self):
            pass

    class MockAgent:
        def __init__(self, name, path):
            self.name = name
            self.skills_path = path

    monkeypatch.setattr("agent_sync.config.Config", MockConfig)

    deleter = SkillsDeleter()
    deleter.global_skills_dir = hub_dir
    deleter.agents = []

    # Attempt to delete using path traversal
    # Note: validate_skill_name will block this first
    stats = deleter.delete_skills(["../secret.txt"])

    assert stats["errors"] == 1
    assert outside_file.exists()

    # Attempt another traversal that might pass validate_skill_name if it was weak
    # (though our regex is quite strict now)
    stats = deleter.delete_skills([".."])
    assert stats["errors"] == 1
    assert hub_dir.exists()


def test_file_permission_hardening(tmp_path):
    """Verify that secure_open and ensure_secure_dir enforce restricted permissions."""
    import os
    from agent_sync.security import secure_open, ensure_secure_dir

    # Test directory creation
    secure_dir = tmp_path / "secure_dir"
    ensure_secure_dir(secure_dir)
    assert secure_dir.exists()
    # Check permissions (should be 0o700)
    assert (os.stat(secure_dir).st_mode & 0o777) == 0o700

    # Test file creation
    secure_file = secure_dir / "secure.yaml"
    with secure_open(secure_file, "w") as f:
        f.write("test: content")

    assert secure_file.exists()
    # Check permissions (should be 0o600)
    assert (os.stat(secure_file).st_mode & 0o777) == 0o600


def test_config_save_permissions(tmp_path):
    """Verify that Config.save enforces restricted permissions."""
    import os
    from agent_sync.config import Config

    config_file = tmp_path / "config.yaml"
    overrides_file = tmp_path / "overrides.yaml"

    config = Config(config_path=config_file, overrides_path=overrides_file)
    config.save()
    config.save_overrides()

    assert config_file.exists()
    assert overrides_file.exists()

    # Check permissions
    assert (os.stat(config_file).st_mode & 0o777) == 0o600
    assert (os.stat(overrides_file).st_mode & 0o777) == 0o600
    assert (os.stat(config_file.parent).st_mode & 0o777) == 0o700


def test_sync_manager_permissions(tmp_path):
    """Verify that SyncManager enforces restricted permissions for state files."""
    import os
    from agent_sync.sync import SyncManager
    from unittest.mock import MagicMock

    config = MagicMock()
    config.repo_url = "https://github.com/owner/repo"

    # Mock DATA_DIR
    data_dir = tmp_path / "data"

    class TestSyncManager(SyncManager):
        DATA_DIR = data_dir
        DEFAULT_REPO_DIR = data_dir / "repo"
        STATE_FILE = data_dir / "sync-state.json"

    sync_mgr = TestSyncManager(config)
    sync_mgr._save_state("test_action")

    assert sync_mgr.STATE_FILE.exists()
    assert (os.stat(sync_mgr.STATE_FILE).st_mode & 0o777) == 0o600
    assert (os.stat(sync_mgr.STATE_FILE.parent).st_mode & 0o777) == 0o700
