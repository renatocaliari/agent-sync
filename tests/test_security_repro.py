import os
import shutil
from pathlib import Path
import pytest
from agent_sync.publish.git_publish import do_git_publish

def test_publish_symlink_leakage_fixed(tmp_path, monkeypatch):
    # Secret file outside
    secret_file = tmp_path / "secret.txt"
    secret_file.write_text("SENSITIVE DATA")

    # Skill directory with a symlink to the secret
    skills_source_dir = tmp_path / "my_skills"
    skills_source_dir.mkdir()
    skill_dir = skills_source_dir / "my-skill"
    skill_dir.mkdir()
    (skill_dir / "SKILL.md").write_text("# My Skill")

    exploit_symlink = skill_dir / "exploit.txt"
    exploit_symlink.symlink_to(secret_file)

    leakage_found = [False]
    is_symlink_at_dest = [False]

    # Mock git operations to avoid real push and inspect tmp_dir
    def mock_git_commit_and_push(tmp_dir, repo, count):
        # Path where the skill will be copied in the temp publish repo
        # Note: do_git_publish uses items_dir / dest_name
        # items = [(skill_dir, "local/my-skill")]
        # dest = items_dir / "local/my-skill"
        exploit_in_tmp = tmp_dir / "skills" / "local/my-skill" / "exploit.txt"

        if exploit_in_tmp.exists():
            if exploit_in_tmp.is_symlink():
                is_symlink_at_dest[0] = True
            else:
                content = exploit_in_tmp.read_text()
                if content == "SENSITIVE DATA":
                    leakage_found[0] = True

    monkeypatch.setattr("agent_sync.publish.git_publish.git_commit_and_push", mock_git_commit_and_push)

    items = [(skill_dir, "local/my-skill")]

    success = do_git_publish(
        items=items,
        subdir="skills",
        readme_generator=lambda a, b, c: None,
        count=1,
        item_name="skills",
        repo="https://github.com/user/repo.git"
    )

    assert success is True
    assert leakage_found[0] is False, "SENSITIVE DATA was leaked as a regular file!"
    assert is_symlink_at_dest[0] is True, "Symlink was not preserved as a symlink!"

def test_publish_agent_symlink_leakage_fixed(tmp_path, monkeypatch):
    # Secret file outside
    secret_file = tmp_path / "secret.txt"
    secret_file.write_text("SENSITIVE AGENT DATA")

    # Agent file that is actually a symlink to a secret
    agents_source_dir = tmp_path / "my_agents"
    agents_source_dir.mkdir()

    exploit_agent = agents_source_dir / "exploit.md"
    exploit_agent.symlink_to(secret_file)

    leakage_found = [False]
    is_symlink_at_dest = [False]

    def mock_git_commit_and_push(tmp_dir, repo, count):
        # do_git_publish for agents: subdir="agents", dest_name="exploit.md"
        exploit_in_tmp = tmp_dir / "agents" / "exploit.md"

        if exploit_in_tmp.exists():
            if exploit_in_tmp.is_symlink():
                is_symlink_at_dest[0] = True
            else:
                content = exploit_in_tmp.read_text()
                if content == "SENSITIVE AGENT DATA":
                    leakage_found[0] = True

    monkeypatch.setattr("agent_sync.publish.git_publish.git_commit_and_push", mock_git_commit_and_push)

    items = [(exploit_agent, "exploit.md")]

    success = do_git_publish(
        items=items,
        subdir="agents",
        readme_generator=lambda a, b, c: None,
        count=1,
        item_name="agents",
        repo="https://github.com/user/repo.git"
    )

    assert success is True
    assert leakage_found[0] is False, "SENSITIVE AGENT DATA was leaked as a regular file!"
    assert is_symlink_at_dest[0] is True, "Symlink agent was followed instead of being copied as a link!"
