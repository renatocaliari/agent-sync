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


def test_shutil_copy_preserves_symlinks(tmp_path, monkeypatch):
    """Verify that SyncManager doesn't follow symlinks during staging to prevent data leakage."""
    from agent_sync.sync import SyncManager
    from unittest.mock import MagicMock

    # Setup directories
    repo_dir = tmp_path / "repo"
    repo_dir.mkdir()
    agent_dir = tmp_path / "agent"
    agent_dir.mkdir()
    secret_file = tmp_path / "secret.txt"
    secret_file.write_text("SENSITIVE DATA")

    # Create symlink that could be leaked
    leak_link = agent_dir / "leak.txt"
    leak_link.symlink_to(secret_file)

    # Mock Config
    mock_config = MagicMock()
    mock_config.repo_url = "https://github.com/user/repo.git"
    mock_config.is_agent_enabled.return_value = True
    mock_config.get_sync_options.return_value = {
        "configs": True,
        "all_files": False,
        "paths": ["leak.txt"]
    }

    # Mock Agent
    mock_agent = MagicMock()
    mock_agent.name = "test-agent"
    mock_agent.config_dir = str(agent_dir)
    mock_agent.is_available.return_value = True

    # Use monkeypatch for get_all_agents
    # Note: get_all_agents is NOT imported directly in sync.py, it's imported inside methods.
    # We should patch where it's used if possible, or patch agent_sync.agents.get_all_agents
    monkeypatch.setattr("agent_sync.sync.BaseAgent", MagicMock()) # Just to be safe
    # It seems get_all_agents is imported inside _stage_all_agent_files and _stage_agents
    # but NOT in _stage_agent_files which we are calling.
    # Wait, _stage_agent_files doesn't call get_all_agents.

    # Mock DATA_DIR and other paths to use tmp_path
    monkeypatch.setattr("agent_sync.sync.SyncManager.DATA_DIR", tmp_path / "data")
    monkeypatch.setattr("agent_sync.sync.SyncManager.DEFAULT_REPO_DIR", repo_dir)

    sync_mgr = SyncManager(mock_config)
    sync_mgr.repo_dir = repo_dir

    # Perform staging
    sync_mgr._stage_agent_files(mock_agent)

    # Check the result
    staged_file = repo_dir / "configs" / "test-agent" / "leak.txt"
    assert staged_file.exists(), "Staged file should exist"
    assert staged_file.is_symlink(), "Symlink should be preserved, not followed"
