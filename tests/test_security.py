"""Security tests for path traversal and other vulnerabilities."""

import pytest
from pathlib import Path
from agent_sync.skills_delete import SkillsDeleter

class MockAgent:
    def __init__(self, name, skills_path):
        self.name = name
        self.skills_path = Path(skills_path)

    def is_available(self):
        return True

class TestPathTraversal:
    """Tests for path traversal prevention."""

    def test_delete_skills_traversal_prevention(self, tmp_path, monkeypatch):
        """Test that SkillsDeleter prevents path traversal during deletion."""

        # Setup fake directories
        home_dir = tmp_path / "home"
        home_dir.mkdir()
        monkeypatch.setattr(Path, "home", lambda: home_dir)

        global_skills_dir = home_dir / ".agents" / "skills"
        global_skills_dir.mkdir(parents=True)

        agent_dir = tmp_path / "agent_config"
        agent_skills_dir = agent_dir / "skills"
        agent_skills_dir.mkdir(parents=True)

        # Create a sensitive file outside the allowed directories
        sensitive_file = tmp_path / "sensitive.txt"
        sensitive_file.write_text("secrets")

        # Create a fake skill
        valid_skill_dir = global_skills_dir / "valid-skill"
        valid_skill_dir.mkdir()
        (valid_skill_dir / "SKILL.md").write_text("Valid skill")

        # Initialize deleter with mocked agents
        monkeypatch.setattr("agent_sync.config.Config", lambda: type('obj', (object,), {'repo_url': None})())

        deleter = SkillsDeleter()
        deleter.global_skills_dir = global_skills_dir
        deleter.agents = [MockAgent("test-agent", agent_skills_dir)]

        # Attempt path traversal
        traversal_name = "../../sensitive.txt"

        # 1. Test CLI-level validation (should block if we used click.Abort, but here we test the business logic)
        # The deleter should handle it gracefully or block it
        stats = deleter.delete_skills([traversal_name])

        assert stats["errors"] > 0
        assert sensitive_file.exists()
        assert sensitive_file.read_text() == "secrets"

    def test_delete_skills_symlink_safety(self, tmp_path, monkeypatch):
        """Test that SkillsDeleter handles symlinks safely without following them to dangerous locations."""

        home_dir = tmp_path / "home"
        home_dir.mkdir()
        monkeypatch.setattr(Path, "home", lambda: home_dir)

        global_skills_dir = home_dir / ".agents" / "skills"
        global_skills_dir.mkdir(parents=True)

        agent_skills_dir = tmp_path / "agent_skills"
        agent_skills_dir.mkdir()

        # External target that should NOT be deleted
        external_target = tmp_path / "external_target"
        external_target.mkdir()
        (external_target / "do_not_delete.txt").write_text("save me")

        # Create a symlink in the agent skills directory pointing to the external target
        skill_symlink = agent_skills_dir / "linked-skill"
        skill_symlink.symlink_to(external_target)

        # Create matching skill in hub so it's "found"
        hub_skill = global_skills_dir / "linked-skill"
        hub_skill.mkdir()
        (hub_skill / "SKILL.md").write_text("Linked skill")

        deleter = SkillsDeleter()
        deleter.global_skills_dir = global_skills_dir
        deleter.agents = [MockAgent("test-agent", agent_skills_dir)]

        # Delete the skill
        stats = deleter.delete_skills(["linked-skill"])

        # The symlink itself should be gone
        assert not skill_symlink.exists()
        assert not skill_symlink.is_symlink()

        # BUT the external target should still exist!
        assert external_target.exists()
        assert (external_target / "do_not_delete.txt").exists()
        assert (external_target / "do_not_delete.txt").read_text() == "save me"
