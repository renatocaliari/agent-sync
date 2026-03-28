"""Security regression tests for agent-sync."""

import pytest
from pathlib import Path
from agent_sync.validators import validate_repo_name, validate_github_url, validate_skill_name
from agent_sync.skills_delete import SkillsDeleter

class TestSecurityHardening:
    """Security tests for path traversal and injection vulnerabilities."""

    def test_newline_injection_repo_name(self):
        """Verify that newline injection is blocked in repo names."""
        assert validate_repo_name("agent-sync\n") is False
        assert validate_repo_name("agent-sync\r") is False
        assert validate_repo_name("owner/repo\n") is False

    def test_newline_injection_github_url(self):
        """Verify that newline injection is blocked in GitHub URLs."""
        assert validate_github_url("https://github.com/owner/repo\n") is False
        assert validate_github_url("https://github.com/owner/repo\r") is False
        # Already blocked by whitespace check but good to verify with regex too
        assert validate_github_url("https://github.com/owner/repo.git\n") is False

    def test_skill_name_validation(self):
        """Verify skill name validation rules."""
        assert validate_skill_name("valid-skill") is True
        assert validate_skill_name("valid.skill_123") is True

        # Path traversal attempts
        assert validate_skill_name("../traversal") is False
        assert validate_skill_name("skill/subdir") is False
        assert validate_skill_name("/absolute/path") is False

        # Newline injection
        assert validate_skill_name("skill\n") is False

        # Invalid starts
        assert validate_skill_name("-invalid") is False
        assert validate_skill_name(".invalid") is False

        # Too long
        assert validate_skill_name("a" * 65) is False

    def test_path_traversal_in_deletion(self, tmp_path, monkeypatch):
        """Verify that SkillsDeleter blocks path traversal during deletion."""
        # Setup mock global hub
        hub_dir = tmp_path / ".agents" / "skills"
        hub_dir.mkdir(parents=True)

        # Create a 'protected' file outside the hub
        protected_file = tmp_path / ".agents" / "protected.txt"
        protected_file.write_text("protected")

        # Create a legitimate skill
        skill_dir = hub_dir / "legit-skill"
        skill_dir.mkdir()
        (skill_dir / "SKILL.md").write_text("info")

        deleter = SkillsDeleter()
        # Mock global_skills_dir to use our tmp hub
        monkeypatch.setattr(deleter, "global_skills_dir", hub_dir)
        monkeypatch.setattr(deleter, "agents", []) # No agents for this test

        # Attempt to delete using traversal
        # 1. Using ../protected.txt
        stats = deleter.delete_skills(["../protected.txt"])
        assert stats["errors"] > 0
        assert protected_file.exists()

        # 2. Using absolute path (if it were allowed by validator, which it isn't)
        # But we verify the defense-in-depth anyway
        stats = deleter.delete_skills([str(protected_file)])
        assert stats["errors"] > 0
        assert protected_file.exists()

        # 3. Legitimate deletion should still work
        stats = deleter.delete_skills(["legit-skill"])
        assert stats["deleted_from_hub"] == 1
        assert not skill_dir.exists()
