"""Security tests for agent-sync."""

import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock
from agent_sync.validators import validate_repo_name, validate_github_url, validate_skill_name
from agent_sync.skills_delete import SkillsDeleter


class TestSecurityValidators:
    """Tests for security in validators."""

    def test_validate_repo_name_newline_injection(self):
        """Test that newline injection is blocked in repo names."""
        assert validate_repo_name("my-repo\n") is False
        assert validate_repo_name("my-repo\r") is False
        assert validate_repo_name("my-repo\nother") is False

    def test_validate_github_url_newline_injection(self):
        """Test that newline injection is blocked in GitHub URLs."""
        assert validate_github_url("https://github.com/owner/repo\n") is False
        assert validate_github_url("https://github.com/owner/repo\n--upload-pack") is False

    def test_validate_skill_name_security(self):
        """Test skill name validation security rules."""
        assert validate_skill_name("valid.skill-123_") is True
        assert validate_skill_name("../traversal") is False
        assert validate_skill_name("skill/name") is False
        assert validate_skill_name("skill\n") is False
        assert validate_skill_name("a" * 65) is False
        assert validate_skill_name("") is False


class TestPathTraversalProtection:
    """Tests for path traversal protection in skills deletion."""

    @patch("agent_sync.skills_delete.console")
    @patch("agent_sync.config.Config")
    @patch("agent_sync.agents.get_agents")
    def test_delete_skills_path_traversal_blocked(self, mock_get_agents, mock_config, mock_console, tmp_path):
        """Test that path traversal attempts are blocked in delete_skills."""
        # Setup mock environment
        hub_dir = tmp_path / "hub"
        hub_dir.mkdir()

        deleter = SkillsDeleter()
        deleter.global_skills_dir = hub_dir
        deleter.agents = []

        # Attempt traversal
        stats = deleter.delete_skills(["../outside"])

        assert stats["errors"] > 0
        assert stats["deleted_from_hub"] == 0

        # Verify console warned about invalid name (regex check)
        mock_console.print.assert_any_call("[red]✗ Invalid skill name (security risk): ../outside[/red]")

    @patch("agent_sync.skills_delete.console")
    @patch("agent_sync.config.Config")
    @patch("agent_sync.agents.get_agents")
    @patch("agent_sync.skills_delete.shutil.rmtree")
    def test_delete_skills_defense_in_depth_blocked(self, mock_rmtree, mock_get_agents, mock_config, mock_console, tmp_path):
        """Test defense-in-depth path traversal check in delete_skills."""
        # Setup mock environment
        hub_dir = tmp_path / "hub"
        hub_dir.mkdir()

        # We need to bypass validate_skill_name to test the path.relative_to check
        # But wait, validate_skill_name is imported inside delete_skills
        # Let's mock it

        with patch("agent_sync.validators.validate_skill_name", return_value=True):
            deleter = SkillsDeleter()
            deleter.global_skills_dir = hub_dir
            deleter.agents = []

            # This should be caught by hub_skill_path.relative_to(self.global_skills_dir)
            stats = deleter.delete_skills([".."])

            assert stats["errors"] > 0
            assert stats["deleted_from_hub"] == 0
            mock_console.print.assert_any_call("[red]✗ Path traversal detected: ..[/red]")
            mock_rmtree.assert_not_called()
