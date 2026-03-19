"""Tests for skills deletion logic."""

import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock
from agent_sync.skills_delete import SkillsDeleter


class TestSkillsDeleter:
    """Tests for SkillsDeleter class."""

    @pytest.fixture
    def deleter(self, tmp_path):
        """Create a SkillsDeleter with mocked config and agents."""
        with patch("agent_sync.config.Config"), \
             patch("agent_sync.agents.get_agents", return_value=[]):
            deleter = SkillsDeleter()
            deleter.global_skills_dir = tmp_path / "global_skills"
            deleter.global_skills_dir.mkdir()
            return deleter

    def test_delete_skills_invalid_name(self, deleter):
        """Test that invalid skill names are rejected and not deleted."""
        # Create a "fake" skill with an invalid name manually in the directory
        # (though our validator should stop it before it even checks the disk)
        bad_name = "../traversal"

        stats = deleter.delete_skills([bad_name])

        assert stats["errors"] == 1
        assert stats["deleted_from_hub"] == 0
        assert stats["not_found"] == 0

    def test_delete_skills_valid_name(self, deleter):
        """Test that valid skill names are processed."""
        skill_name = "valid-skill"
        skill_path = deleter.global_skills_dir / skill_name
        skill_path.mkdir()
        (skill_path / "SKILL.md").write_text("content")

        stats = deleter.delete_skills([skill_name])

        assert stats["deleted_from_hub"] == 1
        assert stats["errors"] == 0
        assert not skill_path.exists()

    def test_delete_skills_newline_injection(self, deleter):
        """Test that newline injection in skill name is rejected."""
        bad_name = "skill\n"

        stats = deleter.delete_skills([bad_name])

        assert stats["errors"] == 1
        assert stats["deleted_from_hub"] == 0
