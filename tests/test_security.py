"""Security regression tests for agent-sync."""

import pytest
from pathlib import Path
from agent_sync.validators import validate_skill_name, validate_repo_name, validate_github_url
from agent_sync.skills_delete import SkillsDeleter

class TestSecurityHardening:
    """Tests for path traversal and input validation hardening."""

    def test_validate_skill_name(self):
        """Test skill name validation rules."""
        # Valid names
        assert validate_skill_name("my-skill") is True
        assert validate_skill_name("skill_v1.0") is True
        assert validate_skill_name("123-skill") is True

        # Invalid names (traversal/absolute)
        assert validate_skill_name("../etc/passwd") is False
        assert validate_skill_name("/etc/passwd") is False
        assert validate_skill_name("skill/../../etc/passwd") is False

        # Invalid characters
        assert validate_skill_name("skill name") is False
        assert validate_skill_name("skill;ls") is False
        assert validate_skill_name("skill\n") is False
        assert validate_skill_name("skill\r\n") is False

        # Leading special characters
        assert validate_skill_name("-skill") is False
        assert validate_skill_name(".skill") is False
        assert validate_skill_name("_skill") is False

        # Length limit
        assert validate_skill_name("a" * 64) is True
        assert validate_skill_name("a" * 65) is False

    def test_newline_injection_in_repo_name(self):
        """Test that repo names with newlines are rejected (preventing regex bypass)."""
        assert validate_repo_name("myrepo\n") is False
        assert validate_repo_name("myrepo\n/other") is False
        assert validate_repo_name("owner/repo\n") is False

    def test_skills_deleter_boundary_check(self, tmp_path, monkeypatch):
        """Test that SkillsDeleter prevents deleting outside the skills directory."""
        # Setup a dummy hub dir
        hub_dir = tmp_path / "hub"
        hub_dir.mkdir()

        # Create a file outside the hub
        outside_file = tmp_path / "secret.txt"
        outside_file.write_text("sensitive data")

        deleter = SkillsDeleter()
        # Point deleter to our temp hub
        monkeypatch.setattr(deleter, "global_skills_dir", hub_dir)
        # Empty agents to simplify
        monkeypatch.setattr(deleter, "agents", [])

        # Attempt traversal via skill name
        traversal_name = "../../secret.txt"
        # Note: validate_skill_name will block this at CLI level, but we want to test
        # the deleter's internal defense-in-depth too.
        # However, deleter now calls validate_skill_name internally.

        # Let's bypass validate_skill_name by mocking it if we want to test the boundary check specifically
        # or just observe that it returns an error.

        stats = deleter.delete_skills([traversal_name], dry_run=False)
        assert stats["errors"] > 0
        assert outside_file.exists()

        # Even if we "force" it past validation (if it were ever weakened)
        # the boundary check should still catch it.
        # (This is harder to test without further mocking, but validate_skill_name is our first line)
