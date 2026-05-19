import os
import shutil
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from agent_sync.agent_discovery import discover_agent_instructions
from agent_sync.publish import _push_agents_to_repo, get_available_skills, publish_skills


def test_get_available_skills_excludes_symlinks(tmp_path, monkeypatch):
    """Verify that get_available_skills skips symbolic links."""
    skills_dir = tmp_path / "skills"
    skills_dir.mkdir()

    # Create a real skill
    real_skill = skills_dir / "real-skill"
    real_skill.mkdir()
    (real_skill / "SKILL.md").write_text("real content")

    # Create a sensitive file outside
    sensitive_file = tmp_path / "secrets.txt"
    sensitive_file.write_text("SENSITIVE_DATA")

    # Create a symlink in skills dir pointing to sensitive file
    # Use .md extension so it matches the allowed file extensions in get_available_skills
    linked_skill = skills_dir / "linked-skill.md"
    linked_skill.symlink_to(sensitive_file)

    # Patch SKILLS_DIR in publish module
    monkeypatch.setattr("agent_sync.publish.SKILLS_DIR", skills_dir)

    skills = get_available_skills()

    skill_names = [s["name"] for s in skills]
    assert "real-skill" in skill_names
    # This is expected to FAIL before the fix
    assert "linked-skill.md" not in skill_names


def test_discover_agent_instructions_excludes_symlinks(tmp_path, monkeypatch):
    """Verify that discover_agent_instructions skips symbolic links."""
    config_dir = tmp_path / "pi-config"
    config_dir.mkdir()

    # Create a real AGENTS.md
    real_agents = config_dir / "AGENTS.md"
    real_agents.write_text("real agent instructions")

    # Create a sensitive file outside
    sensitive_file = tmp_path / "secrets.txt"
    sensitive_file.write_text("SENSITIVE_DATA")

    # Create a symlink in config dir pointing to sensitive file
    linked_agents = config_dir / "LINKED.md"
    linked_agents.symlink_to(sensitive_file)

    # Mock registry
    mock_registry = {
        "pi.dev": {
            "config_dir": str(config_dir),
            "config_patterns": ["*.md"]
        }
    }

    with patch("agent_sync.agent_discovery.load_registry", return_value=mock_registry):
        # We need to ensure expanduser() doesn't mess up our tmp_path if it had ~ (unlikely in tmp_path)
        instructions = discover_agent_instructions(include_agents=["pi.dev"])

        filenames = [i.filename for i in instructions]
        assert "AGENTS.md" in filenames
        # This is expected to FAIL before the fix
        assert "LINKED.md" not in filenames


@patch("agent_sync.publish.subprocess.run")
def test_publish_skills_does_not_follow_symlinks(mock_run, tmp_path, monkeypatch):
    """Verify that publish_skills doesn't follow symlinks during staging."""
    skills_dir = tmp_path / "skills"
    skills_dir.mkdir()

    skill_dir = skills_dir / "my-skill"
    skill_dir.mkdir()
    (skill_dir / "SKILL.md").write_text("skill content")

    # Create a sensitive file outside
    sensitive_file = tmp_path / "secrets.txt"
    sensitive_file.write_text("SENSITIVE_DATA")

    # Create a symlink INSIDE the skill directory pointing to sensitive file
    linked_file = skill_dir / "leak.txt"
    linked_file.symlink_to(sensitive_file)

    # Patch SKILLS_DIR
    monkeypatch.setattr("agent_sync.publish.SKILLS_DIR", skills_dir)

    # Mock other dependencies to avoid real GitHub/Git calls
    with patch("agent_sync.publish.Config"), \
         patch("agent_sync.publish.Prompt.ask", return_value="https://github.com/user/repo"), \
         patch("agent_sync.publish.Confirm.ask", return_value=True), \
         patch("agent_sync.publish.tempfile.TemporaryDirectory") as mock_tmp:

        # Setup a real temporary directory for staging so we can inspect it
        stage_dir = tmp_path / "stage"
        stage_dir.mkdir()
        mock_tmp.return_value.__enter__.return_value = stage_dir

        # We need to mock the git/gh calls so it doesn't fail
        mock_run.return_value = MagicMock(returncode=0, stdout="")

        # Mock validate_repo_name and validate_github_url to return True
        with patch("agent_sync.publish.validate_github_url", return_value=True), \
             patch("agent_sync.publish.validate_repo_name", return_value=True):

            publish_skills(interactive=False)

            staged_leak = stage_dir / "skills" / "my-skill" / "leak.txt"

            if staged_leak.exists():
                # If it exists, it MUST be a symlink, not a regular file with content
                assert staged_leak.is_symlink(), "Symlink was followed and copied as a regular file!"
                # Optionally check it doesn't point to the sensitive file or points to nothing
            else:
                # If it doesn't exist, that's also fine (if we skip symlinks during file collection)
                pass

@patch("agent_sync.publish.subprocess.run")
def test_push_agents_to_repo_does_not_follow_symlinks(mock_run, tmp_path):
    """Verify that _push_agents_to_repo doesn't follow symlinks during staging."""
    agent_dir = tmp_path / "agent-instructions"
    agent_dir.mkdir()

    instr_file = agent_dir / "AGENTS.md"
    instr_file.write_text("instructions")

    # Create a sensitive file outside
    sensitive_file = tmp_path / "secrets.txt"
    sensitive_file.write_text("SENSITIVE_DATA")

    # Create a symlink in agent-instructions pointing to sensitive file
    linked_file = agent_dir / "leak.txt"
    linked_file.symlink_to(sensitive_file)

    items = [
        {"agent": "my-agent", "filename": "AGENTS.md", "path": instr_file},
        {"agent": "my-agent", "filename": "leak.txt", "path": linked_file}
    ]

    mock_config = MagicMock()
    repo_url = "https://github.com/user/repo"

    with patch("agent_sync.publish.tempfile.TemporaryDirectory") as mock_tmp:
        stage_dir = tmp_path / "stage_agents"
        stage_dir.mkdir()
        mock_tmp.return_value.__enter__.return_value = stage_dir

        mock_run.return_value = MagicMock(returncode=0)

        _push_agents_to_repo(items, repo_url, mock_config)

        staged_leak = stage_dir / "agents" / "my-agent" / "leak.txt"

        if staged_leak.exists():
            assert staged_leak.is_symlink(), "Symlink in agents was followed and copied as a regular file!"
