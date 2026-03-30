"""Security regression tests."""

import pytest
from pathlib import Path
from agent_sync.validators import validate_repo_name, validate_github_url, validate_skill_name
from agent_sync.skills_delete import SkillsDeleter

class TestSecurityHardening:
    """Tests for security hardening measures."""

    def test_newline_injection_repo_name(self):
        """Test that newline injection in repository names is blocked."""
        assert validate_repo_name("my-repo\n") is False
        assert validate_repo_name("my-repo\r") is False
        assert validate_repo_name("my-repo\nls") is False

    def test_newline_injection_github_url(self):
        """Test that newline injection in GitHub URLs is blocked."""
        assert validate_github_url("https://github.com/owner/repo\n") is False
        assert validate_github_url("https://github.com/owner/repo\r") is False
        assert validate_github_url("https://github.com/owner/repo\nls") is False

    def test_validate_skill_name(self):
        """Test skill name validation."""
        # Valid names
        assert validate_skill_name("my-skill") is True
        assert validate_skill_name("skill_123") is True
        assert validate_skill_name("my.skill") is True

        # Invalid names
        assert validate_skill_name("my skill") is False
        assert validate_skill_name("skill/traversal") is False
        assert validate_skill_name("../skill") is False
        assert validate_skill_name("skill\n") is False
        assert validate_skill_name("a" * 65) is False
        assert validate_skill_name("") is False
        assert validate_skill_name("-skill") is False # Must start with alphanumeric

    def test_path_traversal_protection(self, tmp_path, monkeypatch):
        """Test that path traversal attempts in skill deletion are blocked."""
        # Setup mock environment
        hub_dir = tmp_path / "hub"
        hub_dir.mkdir()

        # Mock Path.home() to point to our tmp_path
        monkeypatch.setattr(Path, "home", lambda: tmp_path)

        # SkillsDeleter uses Path.home() / ".agents" / "skills"
        global_hub = tmp_path / ".agents" / "skills"
        global_hub.mkdir(parents=True)

        # Create a "secret" file outside the hub
        secret_file = tmp_path / "secret.txt"
        secret_file.write_text("sensitive data")

        # Create a skill directory
        skill_dir = global_hub / "valid-skill"
        skill_dir.mkdir()
        (skill_dir / "SKILL.md").write_text("Valid skill")

        deleter = SkillsDeleter()

        # Attempt path traversal
        traversal_name = "../../secret.txt"
        stats = deleter.delete_skills([traversal_name])

        # Check that traversal was blocked and secret file still exists
        assert stats["errors"] > 0
        assert secret_file.exists()
        assert secret_file.read_text() == "sensitive data"
