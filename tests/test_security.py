import os
from pathlib import Path
from agent_sync.validators import validate_skill_name, validate_repo_name, validate_github_url
from agent_sync.skills_delete import SkillsDeleter

def test_validate_skill_name():
    assert validate_skill_name("valid-skill")
    assert validate_skill_name("valid.skill_2")
    assert not validate_skill_name("../traversal")
    assert not validate_skill_name("/absolute/path")
    assert not validate_skill_name("skill\nwith-newline")
    assert not validate_skill_name("a" * 65)
    assert not validate_skill_name("")
    assert not validate_skill_name("-start-with-hyphen")
    assert validate_skill_name("1-starts-with-number")

def test_validate_repo_name_newline():
    assert not validate_repo_name("owner/repo\n")
    assert not validate_repo_name("owner/repo\r")

def test_validate_github_url_newline():
    assert not validate_github_url("https://github.com/owner/repo\n")
    assert not validate_github_url("https://github.com/owner/repo.git\n")

def test_path_traversal_protection(tmp_path, monkeypatch):
    # Setup dummy environment
    home = tmp_path / "home"
    home.mkdir()

    global_skills_dir = home / ".agents" / "skills"
    global_skills_dir.mkdir(parents=True)

    # Create a secret file outside the skills dir
    secret_dir = home / "secret_dir"
    secret_dir.mkdir()
    secret_file = secret_dir / "secret.txt"
    secret_file.write_text("secret")

    # Mock Path.home()
    monkeypatch.setattr(Path, "home", lambda: home)

    deleter = SkillsDeleter()

    # Try relative traversal
    stats = deleter.delete_skills(["../../secret_dir"], dry_run=False)
    assert stats["errors"] > 0
    assert secret_dir.exists()

    # Try absolute traversal
    stats = deleter.delete_skills([str(secret_dir)], dry_run=False)
    assert stats["errors"] > 0
    assert secret_dir.exists()

def test_agent_symlink_deletion(tmp_path, monkeypatch):
    # Setup dummy environment
    home = tmp_path / "home"
    home.mkdir()

    global_skills_dir = home / ".agents" / "skills"
    global_skills_dir.mkdir(parents=True)

    skill_dir = global_skills_dir / "my-skill"
    skill_dir.mkdir()
    (skill_dir / "SKILL.md").write_text("info")

    # Setup agent dir with symlink
    agent_dir = home / ".claude" / "commands"
    agent_dir.mkdir(parents=True)

    agent_skill_symlink = agent_dir / "my-skill"
    agent_skill_symlink.symlink_to(skill_dir)

    assert agent_skill_symlink.is_symlink()
    assert agent_skill_symlink.exists()

    # Mock Path.home()
    monkeypatch.setattr(Path, "home", lambda: home)

    # Mock agents in deleter
    from agent_sync.agents.base import BaseAgent

    mock_agent = BaseAgent(
        name="test-agent",
        data={
            "method": "copy",
            "skills_dir_name": "commands",
            "config_dir": str(home / ".claude"),
            "config_filename": "settings.json"
        }
    )

    deleter = SkillsDeleter()
    deleter.agents = [mock_agent]

    # Delete skill
    deleter.delete_skills(["my-skill"], dry_run=False)

    # Verify symlink is deleted but hub was also deleted by the deleter
    assert not agent_skill_symlink.exists()
    assert not agent_skill_symlink.is_symlink()
    assert not skill_dir.exists()

if __name__ == "__main__":
    # If run directly, just run these tests
    test_validate_skill_name()
    test_validate_repo_name_newline()
    test_validate_github_url_newline()
    print("Security tests passed!")
