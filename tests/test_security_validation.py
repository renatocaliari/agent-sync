
import pytest
from agent_sync.validators import validate_repo_name, validate_github_url, validate_skill_name

def test_validate_repo_name_newline_injection():
    # Should fail with trailing newline
    assert validate_repo_name("my-repo\n") is False
    assert validate_repo_name("my-repo") is True

def test_validate_github_url_newline_injection():
    # Should fail with newline in URL
    assert validate_github_url("https://github.com/owner/repo\n") is False
    assert validate_github_url("https://github.com/owner/repo") is True

def test_validate_skill_name_basic():
    assert validate_skill_name("valid-skill") is True
    assert validate_skill_name("valid.skill_123") is True
    assert validate_skill_name("invalid/skill") is False
    assert validate_skill_name("../traversal") is False
    assert validate_skill_name("skill\n") is False
    assert validate_skill_name("-start-with-hyphen") is False
    assert validate_skill_name("") is False
    assert validate_skill_name("a" * 65) is False

def test_delete_skills_with_invalid_name():
    from agent_sync.skills_delete import SkillsDeleter
    from unittest.mock import MagicMock

    deleter = SkillsDeleter()
    # Mock global_skills_dir to avoid real file system impact
    deleter.global_skills_dir = MagicMock()

    stats = deleter.delete_skills(["../etc/passwd", "valid-skill"])
    assert stats["errors"] >= 1  # Should error on the malicious one
