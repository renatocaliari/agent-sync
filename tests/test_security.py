"""Security regression tests."""

import pytest
from pathlib import Path
import shutil
from agent_sync.validators import validate_skill_name, validate_repo_name, validate_github_url
from agent_sync.skills_delete import SkillsDeleter


class TestSecurity:
    """Security tests for path traversal and input validation."""

    def test_validate_skill_name_traversal(self):
        """Test that skill name validator blocks traversal characters."""
        assert validate_skill_name("../forbidden") is False
        assert validate_skill_name("..") is False
        assert validate_skill_name("/") is False
        assert validate_skill_name("skill/name") is False
        assert validate_skill_name("\\") is False
        assert validate_skill_name(";") is False
        assert validate_skill_name(" ") is False

    def test_validate_skill_name_valid(self):
        """Test valid skill names."""
        assert validate_skill_name("my-skill") is True
        assert validate_skill_name("my.skill") is True
        assert validate_skill_name("my_skill") is True
        assert validate_skill_name("Skill123") is True

    def test_newline_injection_bypass(self):
        """Test that \\Z prevents newline injection bypass."""
        assert validate_repo_name("my-repo\n") is False
        assert validate_repo_name("my-repo\nls") is False
        assert validate_skill_name("my-skill\n") is False
        assert validate_github_url("https://github.com/owner/repo\n") is False

    def test_delete_skills_path_traversal_hub(self, tmp_path, monkeypatch):
        """Test that delete_skills blocks path traversal in hub."""
        # Setup fake home and hub
        fake_home = tmp_path / "home"
        hub_dir = fake_home / ".agents" / "skills"
        hub_dir.mkdir(parents=True)

        forbidden_dir = fake_home / ".agents" / "forbidden"
        forbidden_dir.mkdir(parents=True)
        (forbidden_dir / "secret.txt").write_text("secret")

        # Mock Path.home()
        monkeypatch.setattr(Path, "home", lambda: fake_home)

        deleter = SkillsDeleter()
        # Should be blocked by validator and relative_to
        stats = deleter.delete_skills(["../forbidden"], dry_run=False)

        assert stats["errors"] > 0
        assert stats["deleted_from_hub"] == 0
        assert forbidden_dir.exists()
        assert (forbidden_dir / "secret.txt").exists()

    def test_delete_skills_path_traversal_agent(self, tmp_path, monkeypatch):
        """Test that delete_skills blocks path traversal in agent directories."""
        # Setup fake home and hub
        fake_home = tmp_path / "home"
        hub_dir = fake_home / ".agents" / "skills"
        hub_dir.mkdir(parents=True)

        # Setup fake agent
        agent_dir = fake_home / "agent_config"
        agent_skills = agent_dir / "skills"
        agent_skills.mkdir(parents=True)

        forbidden_dir = agent_dir / "forbidden"
        forbidden_dir.mkdir(parents=True)
        (forbidden_dir / "secret.txt").write_text("secret")

        # Mock Path.home()
        monkeypatch.setattr(Path, "home", lambda: fake_home)

        class MockAgent:
            def __init__(self, name, skills_path):
                self.name = name
                self.skills_path = skills_path

        mock_agent = MockAgent("test-agent", agent_skills)

        # Instead of monkeypatching the module-level function, we mock it on the instance
        deleter = SkillsDeleter()
        deleter.agents = [mock_agent]

        # Even if it passes validator (which it won't), it should be blocked by relative_to
        stats = deleter.delete_skills(["../forbidden"], dry_run=False)

        assert stats["errors"] > 0
        assert forbidden_dir.exists()
        assert (forbidden_dir / "secret.txt").exists()
