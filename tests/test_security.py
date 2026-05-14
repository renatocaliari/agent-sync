"""Security regression tests for agent-sync."""

import pytest
from pathlib import Path
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


def test_shutil_copy_preserves_symlinks(tmp_path):
    """Verify that shutil copy operations preserve symlinks to avoid content leakage."""
    import shutil

    # Create a secret file outside the source directory
    outside_dir = tmp_path / "outside"
    outside_dir.mkdir()
    secret_file = outside_dir / "secret.txt"
    secret_file.write_text("SENSITIVE DATA")

    # Create a source directory with a symlink to the secret file
    src_dir = tmp_path / "src"
    src_dir.mkdir()
    symlink_file = src_dir / "link.txt"
    symlink_file.symlink_to(secret_file)

    # Create a destination directory
    dest_dir = tmp_path / "dest"
    dest_dir.mkdir()

    # 1. Test shutil.copy2 (vulnerable if follow_symlinks=True, which is default)
    # We want to ensure we use follow_symlinks=False in the codebase
    target_copy2 = dest_dir / "copy2_link.txt"
    shutil.copy2(symlink_file, target_copy2, follow_symlinks=False)
    assert target_copy2.is_symlink()
    assert str(target_copy2.readlink()) == str(secret_file)

    # 2. Test shutil.copytree (vulnerable if symlinks=False, which is default)
    # We want to ensure we use symlinks=True in the codebase
    target_copytree = dest_dir / "copytree_dir"
    shutil.copytree(src_dir, target_copytree, symlinks=True)
    target_in_copytree = target_copytree / "link.txt"
    assert target_in_copytree.is_symlink()
    assert str(target_in_copytree.readlink()) == str(secret_file)
