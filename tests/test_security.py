"""Security tests for path traversal and validation bypasses."""

import pytest
from pathlib import Path
from agent_sync.skills_delete import SkillsDeleter
from agent_sync.validators import validate_skill_name, validate_repo_name, validate_github_url


def test_validate_skill_name_path_traversal():
    """Verify that validate_skill_name rejects path traversal attempts."""
    assert validate_skill_name("../skill") is False
    assert validate_skill_name("..") is False
    assert validate_skill_name("/") is False
    assert validate_skill_name("/etc/passwd") is False
    assert validate_skill_name("skill/../../etc/passwd") is False


def test_validate_skill_name_newline_injection():
    """Verify that validate_skill_name rejects newline injection."""
    assert validate_skill_name("skill\n") is False
    assert validate_skill_name("skill\r") is False
    assert validate_skill_name("skill\n/etc/passwd") is False


def test_validate_repo_name_newline_injection():
    """Verify that validate_repo_name rejects newline injection."""
    assert validate_repo_name("repo\n") is False
    assert validate_repo_name("owner/repo\n") is False


def test_validate_github_url_newline_injection():
    """Verify that validate_github_url rejects newline injection."""
    assert validate_github_url("https://github.com/owner/repo\n") is False
    assert validate_github_url("https://github.com/owner/repo\n/anything") is False


def test_skills_deleter_path_traversal_protection(tmp_path, monkeypatch):
    """Verify that SkillsDeleter prevents path traversal even if validator is bypassed."""
    # Setup mock home and directories
    mock_home = tmp_path / "home"
    mock_home.mkdir()
    monkeypatch.setenv("HOME", str(mock_home))

    # Hub directory
    hub_dir = mock_home / ".agents" / "skills"
    hub_dir.mkdir(parents=True)

    # Sensitive file outside hub
    sensitive_file = tmp_path / "sensitive.txt"
    sensitive_file.write_text("secrets")

    # Initialize deleter
    # We need to mock get_agents to avoid actual config loading
    monkeypatch.setattr("agent_sync.agents.get_agents", lambda: [])

    deleter = SkillsDeleter()
    deleter.global_skills_dir = hub_dir

    # Attempt deletion with path traversal (simulating validator bypass)
    # Since we are testing the internal logic, we might need to bypass the call to validate_skill_name
    # if it's too good. But here we want to test the relative_to check.

    # Skill name that points outside
    traversal_name = "../../sensitive.txt"

    # We'll mock validate_skill_name to return True for this test
    # to see if the second layer of defense works
    monkeypatch.setattr("agent_sync.validators.validate_skill_name", lambda x: True)

    # Run deletion
    stats = deleter.delete_skills([traversal_name])

    # Verify sensitive file still exists
    assert sensitive_file.exists()
    assert stats["errors"] > 0
    assert stats["deleted_from_hub"] == 0
