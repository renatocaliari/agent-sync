import pytest
from pathlib import Path
from agent_sync.skills_delete import SkillsDeleter
from agent_sync.validators import validate_skill_name

def test_validate_skill_name():
    """Test skill name validation."""
    # Valid names
    assert validate_skill_name("valid-skill") is True
    assert validate_skill_name("valid.skill_123") is True
    assert validate_skill_name("a") is True

    # Invalid names (path traversal, etc.)
    assert validate_skill_name("../traversal") is False
    assert validate_skill_name("/absolute") is False
    assert validate_skill_name("invalid/name") is False
    assert validate_skill_name("cmd; ls") is False
    assert validate_skill_name("multi\nline") is False
    assert validate_skill_name("") is False
    assert validate_skill_name("a" * 65) is False
    assert validate_skill_name("-start-with-hyphen") is False
    assert validate_skill_name(".start-with-period") is False

def test_skills_deleter_path_traversal_protection(tmp_path, monkeypatch):
    """Test that SkillsDeleter blocks path traversal even if validation is bypassed."""
    # Setup mock home and global skills dir
    fake_home = tmp_path / "home"
    global_skills = fake_home / ".agents" / "skills"
    global_skills.mkdir(parents=True)

    # Create a "sensitive" file outside the skills dir
    sensitive_file = tmp_path / "sensitive.txt"
    sensitive_file.write_text("secret data")

    # Mock Path.home() and get_agents
    monkeypatch.setattr(Path, "home", lambda: fake_home)

    # Initialize deleter
    deleter = SkillsDeleter()

    # Attempt a path traversal deletion
    # Pathlib might normalize ../sensitive.txt to be relative to global_skills
    # We want to see if it escapes.
    # traversal_name = "../../sensitive.txt" which would point to tmp_path/sensitive.txt
    # We'll use an absolute path simulation as well to be sure.
    traversal_name = "../../sensitive.txt"

    # Mock validate_skill_name to return True to test the second layer of defense
    monkeypatch.setattr("agent_sync.validators.validate_skill_name", lambda x: True)

    # Run deletion
    stats = deleter.delete_skills([traversal_name], dry_run=False)

    # Verify it was blocked
    assert stats["errors"] > 0
    assert sensitive_file.exists()
    assert sensitive_file.read_text() == "secret data"

def test_validate_repo_name_newline_injection():
    """Test that repo name validation blocks newline injection."""
    assert validate_repo_name("valid-repo") is True
    assert validate_repo_name("valid-repo\ninjection") is False

def test_validate_github_url_newline_injection():
    """Test that GitHub URL validation blocks newline injection."""
    assert validate_github_url("https://github.com/owner/repo") is True
    assert validate_github_url("https://github.com/owner/repo\ninjection") is False
    assert validate_github_url("https://github.com/owner\ninjection/repo") is False

from agent_sync.validators import validate_repo_name, validate_github_url
