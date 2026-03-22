"""Security verification tests for agent-sync."""

import pytest
from agent_sync.validators import validate_skill_name, validate_repo_name, validate_github_url
from agent_sync.skills_delete import SkillsDeleter
from unittest.mock import MagicMock, patch
from pathlib import Path

class TestSecurityValidation:
    """Tests for security-related validation logic."""

    def test_validate_skill_name_basic(self):
        """Test basic valid and invalid skill names."""
        assert validate_skill_name("my-skill") is True
        assert validate_skill_name("skill.v1") is True
        assert validate_skill_name("agent_sync_skill") is True
        assert validate_skill_name("123-skill") is True

        # Invalid cases
        assert validate_skill_name("") is False
        assert validate_skill_name("my skill") is False # No spaces
        assert validate_skill_name("-skill") is False  # Cannot start with hyphen
        assert validate_skill_name("skill$") is False  # No special chars
        assert validate_skill_name("a" * 65) is False  # Too long

    def test_validate_skill_name_path_traversal(self):
        """Test path traversal prevention in skill names."""
        assert validate_skill_name("../passwd") is False
        assert validate_skill_name("..") is False
        assert validate_skill_name("/") is False
        assert validate_skill_name("/etc/passwd") is False
        assert validate_skill_name("skills/../../etc/passwd") is False
        assert validate_skill_name("~/.ssh/id_rsa") is False

    def test_validate_skill_name_newline_injection(self):
        """Test newline injection prevention in skill names."""
        assert validate_skill_name("my-skill\n") is False
        assert validate_skill_name("my-skill\r") is False
        assert validate_skill_name("\nmy-skill") is False

    def test_validate_repo_name_newline_injection(self):
        """Test newline injection prevention in repo names."""
        assert validate_repo_name("my-repo\n") is False
        assert validate_repo_name("owner/repo\n") is False

    def test_validate_github_url_newline_injection(self):
        """Test newline injection prevention in GitHub URLs."""
        assert validate_github_url("https://github.com/owner/repo\n") is False
        assert validate_github_url("https://github.com/owner/repo.git\n") is False

class TestSkillsDeleterSecurity:
    """Tests for SkillsDeleter security measures."""

    @patch("agent_sync.skills_delete.shutil.rmtree")
    @patch("agent_sync.skills_delete.Path.exists")
    @patch("agent_sync.skills_delete.Path.home")
    def test_delete_skills_validation(self, mock_home_delete, mock_exists, mock_rmtree, tmp_path):
        """Test that delete_skills validates names before doing anything."""
        # Setup mock home to avoid permission issues
        mock_home_delete.return_value = tmp_path

        config_file = tmp_path / "config.yaml"
        config_file.write_text("{}")

        # Also need to mock get_agents to avoid more path issues
        with patch("agent_sync.agents.get_agents", return_value=[]):
            with patch("agent_sync.config.Config.load"):
                deleter = SkillsDeleter()
                deleter.config.config_path = config_file

            # Test with an invalid name
        stats = deleter.delete_skills(["../etc/passwd", "valid-skill"])

        # Should have 1 error from the invalid name
        assert stats["errors"] == 1

        # Should NOT have tried to check if ../etc/passwd exists or delete it
        # Note: Depending on implementation, it might check exists for valid-skill
        # but definitely shouldn't for the invalid one.

        for call in mock_exists.call_args_list:
            path = call[0][0] if call[0] else call[1].get('path')
            # The path construction should have been avoided for the invalid skill
            assert "passwd" not in str(path)

    def test_path_joining_safety(self):
        """Verify that Path joining doesn't escape the base directory when using validated names."""
        base_dir = Path("/tmp/base")
        skill_name = "valid-skill"

        # This is how Path works, but we want to ensure we only use it with validated names
        joined = base_dir / skill_name
        assert str(joined) == "/tmp/base/valid-skill"

        # Just a reminder why we validate:
        traversal = " /etc/passwd" # leading space + slash
        # base_dir / "/etc/passwd" would be "/etc/passwd"
        # but our validator catches this
        assert validate_skill_name(traversal) is False
