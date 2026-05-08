"""Security regression tests for agent-sync."""

import pytest
from pathlib import Path
from unittest.mock import MagicMock
from agent_sync.validators import validate_skill_name, validate_repo_name, validate_github_url
from agent_sync.skills_delete import SkillsDeleter


def test_validate_skill_name_security():
    """Verify that validate_skill_name blocks dangerous names."""
    # Safe names
    assert validate_skill_name("my-skill") is True
    assert validate_skill_name("skill.v1") is True
    assert validate_skill_name("skill_2") is True

    # Path traversal attempts
    assert validate_skill_name("../dangerous") is False
    assert validate_skill_name("..") is False
    assert validate_skill_name("/") is False
    assert validate_skill_name("/etc/passwd") is False
    assert validate_skill_name("skills/../base") is False

    # Newline injection
    assert validate_skill_name("skill\n") is False
    assert validate_skill_name("skill\r\n") is False

    # Shell characters
    assert validate_skill_name("skill;ls") is False
    assert validate_skill_name("skill|rm") is False
    assert validate_skill_name("skill&whoami") is False
    assert validate_skill_name("skill`id`") is False
    assert validate_skill_name("skill$(id)") is False


def test_validate_repo_name_newline_injection():
    """Verify that validate_repo_name blocks newline injection."""
    assert validate_repo_name("repo\n") is False
    assert validate_repo_name("repo\r") is False
    assert validate_repo_name("owner/repo\n") is False


def test_validate_github_url_newline_injection():
    """Verify that validate_github_url blocks newline injection."""
    assert validate_github_url("https://github.com/owner/repo\n") is False
    assert validate_github_url("https://github.com/owner/repo\r.git") is False


def test_skills_deleter_path_traversal_blocking(tmp_path, monkeypatch):
    """Verify that SkillsDeleter blocks path traversal attempts."""
    # Setup mock environment
    hub_dir = tmp_path / "hub"
    hub_dir.mkdir()

    # Create a dummy skill
    skill_dir = hub_dir / "my-skill"
    skill_dir.mkdir()
    (skill_dir / "SKILL.md").write_text("dummy")

    # Create a file outside the hub
    outside_file = tmp_path / "secret.txt"
    outside_file.write_text("secret content")

    class MockConfig:
        def __init__(self):
            pass

    class MockAgent:
        def __init__(self, name, path):
            self.name = name
            self.skills_path = path

    monkeypatch.setattr("agent_sync.config.Config", MockConfig)

    deleter = SkillsDeleter()
    deleter.global_skills_dir = hub_dir
    deleter.agents = []

    # Attempt to delete using path traversal
    # Note: validate_skill_name will block this first
    stats = deleter.delete_skills(["../secret.txt"])

    assert stats["errors"] == 1
    assert outside_file.exists()

    # Attempt another traversal that might pass validate_skill_name if it was weak
    # (though our regex is quite strict now)
    stats = deleter.delete_skills([".."])
    assert stats["errors"] == 1
    assert hub_dir.exists()


def test_sync_stage_skills_symlink_blocking(tmp_path, monkeypatch):
    """Verify that SyncManager skips symlinks in global skills during staging."""
    import shutil
    import os
    from agent_sync.sync import SyncManager

    # Setup
    global_skills_dir = tmp_path / "global_skills"
    global_skills_dir.mkdir()

    repo_dir = tmp_path / "repo"
    repo_dir.mkdir()
    (repo_dir / "skills").mkdir()

    secrets_dir = tmp_path / "secrets"
    secrets_dir.mkdir()
    (secrets_dir / "confidential.txt").write_text("SENSITIVE DATA")

    # Create symlink in global_skills pointing to secrets
    os.symlink(secrets_dir, global_skills_dir / "malicious_skill")
    (global_skills_dir / "valid_skill").mkdir()
    (global_skills_dir / "valid_skill" / "SKILL.md").write_text("valid")

    class MockConfig:
        def __init__(self):
            self.repo_url = "https://github.com/user/repo"
            self.agents = []
            self.published_skills = []
        def is_agent_enabled(self, name): return False
        def get_agent_config(self, name): return {}

    # Mock Path.home() to return our tmp_path
    monkeypatch.setattr("pathlib.Path.home", lambda: tmp_path)
    # The actual path used in sync.py is Path.home() / ".agents" / "skills"
    real_global_skills = tmp_path / ".agents" / "skills"
    real_global_skills.parent.mkdir(parents=True, exist_ok=True)
    # Move our setup to the expected location
    shutil.move(str(global_skills_dir), str(real_global_skills))

    sync_manager = SyncManager(MockConfig())
    sync_manager.repo_dir = repo_dir

    # Mock _create_manifest and _save_manifest to avoid more setup
    monkeypatch.setattr(sync_manager, "_create_manifest", lambda: {})
    monkeypatch.setattr(sync_manager, "_save_manifest", lambda x: None)
    monkeypatch.setattr(sync_manager, "_stage_symlinks_for_backup", lambda: None)

    # Trigger staging
    sync_manager._stage_skills()

    # Verify malicious_skill was NOT copied
    # Note: Currently this Fails because it IS copied (vulnerable)
    assert not (repo_dir / "skills" / "malicious_skill").exists()
    # Verify valid_skill WAS copied
    assert (repo_dir / "skills" / "valid_skill").exists()


def test_publish_skills_symlink_blocking(tmp_path, monkeypatch):
    """Verify that publish_skills skips symlinks."""
    import shutil
    import os
    from agent_sync.publish import publish_skills
    import agent_sync.publish

    # Setup
    global_skills_dir = tmp_path / ".agents" / "skills"
    global_skills_dir.mkdir(parents=True)

    secrets_dir = tmp_path / "secrets"
    secrets_dir.mkdir()
    (secrets_dir / "confidential.txt").write_text("SENSITIVE DATA")

    # Create symlink and valid skill
    os.symlink(secrets_dir, global_skills_dir / "malicious_skill")
    valid_skill = global_skills_dir / "valid_skill"
    valid_skill.mkdir()
    (valid_skill / "SKILL.md").write_text("valid")

    monkeypatch.setattr("pathlib.Path.home", lambda: tmp_path)
    monkeypatch.setattr(agent_sync.publish, "SKILLS_DIR", global_skills_dir)
    monkeypatch.setattr(agent_sync.publish, "PUBLISH_CONFIG_PATH", tmp_path / "publish.yaml")

    # Mock subprocess and other things to avoid actual publishing
    monkeypatch.setattr("subprocess.run", MagicMock())
    monkeypatch.setattr("agent_sync.publish.Confirm.ask", lambda *args, **kwargs: True)
    monkeypatch.setattr("agent_sync.publish.Prompt.ask", lambda *args, **kwargs: "https://github.com/user/repo")

    # We want to check the temp directory before it's deleted, but publish_skills uses it as a context manager
    # We can mock shutil.copytree and shutil.copy2 to see if they are called with malicious_skill
    import shutil
    original_copytree = shutil.copytree

    copied_paths = []
    def mock_copytree(src, dst, *args, **kwargs):
        copied_paths.append(Path(src).name)
        return original_copytree(src, dst, *args, **kwargs)

    monkeypatch.setattr("shutil.copytree", mock_copytree)

    # Run publish (dry_run=True to skip git commands)
    publish_skills(repo_url="https://github.com/user/pub-repo", dry_run=False, interactive=False)

    # Verify malicious_skill was NOT copied
    # Note: Currently this Fails because it IS copied (vulnerable)
    assert "malicious_skill" not in copied_paths
    assert "valid_skill" in copied_paths
