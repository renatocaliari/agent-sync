"""Security-focused tests for agent-sync."""

import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch
from agent_sync.skills_delete import SkillsDeleter

class TestSecurity:
    """Security tests for input validation and path traversal."""

    @patch("agent_sync.config.Config")
    @patch("agent_sync.agents.get_agents")
    def test_skills_deleter_rejects_malicious_input(self, mock_get_agents, mock_config, tmp_path):
        """Test that SkillsDeleter rejects malicious skill names."""
        # Setup mock environment
        home = tmp_path / "home"
        skills_dir = home / ".agents" / "skills"
        skills_dir.mkdir(parents=True)

        # Create a real skill
        (skills_dir / "valid-skill").mkdir()
        (skills_dir / "valid-skill" / "SKILL.md").write_text("content")

        # Create a file outside the skills dir that we'll try to target
        sensitive_file = home / "sensitive.txt"
        sensitive_file.write_text("secret data")

        with patch("pathlib.Path.home", return_value=home):
            deleter = SkillsDeleter()

            # Malicious skill names
            malicious_names = [
                "../sensitive.txt",
                "valid-skill/../../sensitive.txt",
                "skill\n",
                "; ls -la",
                "$(rm -rf /)"
            ]

            stats = deleter.delete_skills(malicious_names, dry_run=False)

            # All malicious names should have resulted in errors and NOT been processed
            assert stats["errors"] == len(malicious_names)
            assert stats["deleted_from_hub"] == 0

            # Verify sensitive file is still there
            assert sensitive_file.exists()
            assert sensitive_file.read_text() == "secret data"

            # Verify valid skill is still there (since we only passed malicious names)
            assert (skills_dir / "valid-skill").exists()

    @patch("agent_sync.config.Config")
    @patch("agent_sync.agents.get_agents")
    def test_skills_deleter_processes_valid_input(self, mock_get_agents, mock_config, tmp_path):
        """Test that SkillsDeleter still works for valid skill names."""
        home = tmp_path / "home"
        skills_dir = home / ".agents" / "skills"
        skills_dir.mkdir(parents=True)

        # Create a real skill
        (skills_dir / "valid-skill").mkdir()
        (skills_dir / "valid-skill" / "SKILL.md").write_text("content")

        mock_get_agents.return_value = [] # No agents for this test

        with patch("pathlib.Path.home", return_value=home):
            deleter = SkillsDeleter()
            stats = deleter.delete_skills(["valid-skill"], dry_run=False)

            assert stats["deleted_from_hub"] == 1
            assert stats["errors"] == 0
            assert not (skills_dir / "valid-skill").exists()
