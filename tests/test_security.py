"""Security tests for path traversal and newline injection."""

import pytest
import os
import shutil
from pathlib import Path
from agent_sync.skills_delete import SkillsDeleter

class TestSecurityFixes:
    """Security verification suite."""

    def setup_method(self):
        """Set up a safe testing environment."""
        self.test_hub = Path.home() / ".agents_test_hub" / "skills"
        self.test_hub.mkdir(parents=True, exist_ok=True)

        # Create a dummy skill
        self.skill_name = "safe-skill"
        self.skill_path = self.test_hub / self.skill_name
        self.skill_path.mkdir(exist_ok=True)
        (self.skill_path / "SKILL.md").write_text("safe skill")

        # Create a sensitive directory outside the hub
        self.sensitive_dir = Path.home() / "sensitive_test_data"
        self.sensitive_dir.mkdir(parents=True, exist_ok=True)
        (self.sensitive_dir / "secret.txt").write_text("TOP SECRET")

        # Mock deleter with test hub
        self.deleter = SkillsDeleter()
        self.deleter.global_skills_dir = self.test_hub.resolve()

    def teardown_method(self):
        """Clean up test directories."""
        if self.test_hub.parent.exists():
            shutil.rmtree(self.test_hub.parent)
        if self.sensitive_dir.exists():
            shutil.rmtree(self.sensitive_dir)

    def test_path_traversal_blocked(self, capsys):
        """Verify that path traversal attempts are blocked."""
        # Attempt to delete the sensitive directory using traversal
        traversal_name = "../" + self.sensitive_dir.name

        stats = self.deleter.delete_skills([traversal_name])

        assert stats["errors"] > 0
        assert self.sensitive_dir.exists()
        assert (self.sensitive_dir / "secret.txt").exists()

        captured = capsys.readouterr()
        assert "Security Error" in captured.out

    def test_newline_injection_blocked(self, capsys):
        """Verify that newline injection is blocked by validator."""
        injection_name = "safe-skill\n"

        stats = self.deleter.delete_skills([injection_name])

        assert stats["errors"] > 0
        assert self.skill_path.exists() # Should NOT be deleted due to invalid name

        captured = capsys.readouterr()
        assert "Security Error: Invalid skill name" in captured.out

    def test_safe_deletion_works(self):
        """Verify that legitimate deletion still works."""
        stats = self.deleter.delete_skills([self.skill_name])

        assert stats["deleted_from_hub"] == 1
        assert not self.skill_path.exists()
        assert self.sensitive_dir.exists() # Unrelated dir should be untouched
