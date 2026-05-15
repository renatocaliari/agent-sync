import shutil
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

from agent_sync.agent_discovery import discover_agent_instructions
from agent_sync.publish import get_available_skills, _push_agents_to_repo, publish_skills


def test_get_available_skills_skips_symlinks(tmp_path, monkeypatch):
    """Verify that get_available_skills skips symbolic links."""
    skills_dir = tmp_path / "skills"
    skills_dir.mkdir()

    # Create a real skill file
    real_skill = skills_dir / "real-skill.md"
    real_skill.write_text("real skill")

    # Create a symlink
    target = tmp_path / "target.md"
    target.write_text("target content")
    symlinked_skill = skills_dir / "symlinked-skill.md"
    symlinked_skill.symlink_to(target)

    # Patch SKILLS_DIR in publish module
    monkeypatch.setattr("agent_sync.publish.SKILLS_DIR", skills_dir)

    skills = get_available_skills()

    # Should only find the real skill
    assert len(skills) == 1
    assert skills[0]["name"] == "real-skill.md"


def test_discover_agent_instructions_skips_symlinks(tmp_path, monkeypatch):
    """Verify that discover_agent_instructions skips symbolic links."""
    config_dir = tmp_path / "config"
    config_dir.mkdir()

    # Create a real instruction file
    real_file = config_dir / "AGENTS.md"
    real_file.write_text("real agents")

    # Create a symlink
    target = tmp_path / "target.md"
    target.write_text("target content")
    symlinked_file = config_dir / "LINKED.md"
    symlinked_file.symlink_to(target)

    # Mock registry
    mock_registry = {
        "test-agent": {
            "config_dir": str(config_dir),
            "config_patterns": ["*.md"]
        }
    }

    with patch("agent_sync.agent_discovery.load_registry", return_value=mock_registry):
        instructions = discover_agent_instructions()

    # Should only find the real file
    assert len(instructions) == 1
    assert instructions[0].filename == "AGENTS.md"


def test_push_agents_to_repo_uses_no_follow_symlinks(tmp_path):
    """Verify that _push_agents_to_repo uses follow_symlinks=False."""
    items = [
        {
            "agent": "test-agent",
            "filename": "AGENTS.md",
            "path": tmp_path / "AGENTS.md"
        }
    ]
    items[0]["path"].write_text("content")

    mock_config = MagicMock()
    repo_url = "https://github.com/owner/repo.git"

    with patch("agent_sync.publish._git_clone_or_init"), \
         patch("agent_sync.publish._git_push"), \
         patch("shutil.copy2") as mock_copy2:

        _push_agents_to_repo(items, repo_url, mock_config)

        # Verify copy2 called with follow_symlinks=False
        mock_copy2.assert_called_once()
        args, kwargs = mock_copy2.call_args
        assert kwargs.get("follow_symlinks") is False


def test_publish_skills_uses_safe_copy_params(tmp_path, monkeypatch):
    """Verify that publish_skills uses safe copy parameters (symlinks=True for copytree, follow_symlinks=False for copy2)."""
    skills_dir = tmp_path / "skills"
    skills_dir.mkdir()

    # Create a directory skill
    dir_skill = skills_dir / "dir-skill"
    dir_skill.mkdir()
    (dir_skill / "SKILL.md").write_text("dir skill")

    # Create a file skill
    file_skill = skills_dir / "file-skill.md"
    file_skill.write_text("file skill")

    monkeypatch.setattr("agent_sync.publish.SKILLS_DIR", skills_dir)

    # Mock other requirements for publish_skills to reach the execution part
    mock_config = MagicMock()
    mock_config.published_skills = ["dir-skill", "file-skill.md"]

    with patch("agent_sync.publish.Config", return_value=mock_config), \
         patch("agent_sync.publish.validate_github_url", return_value=True), \
         patch("agent_sync.publish.validate_repo_name", return_value=True), \
         patch("agent_sync.publish.Confirm.ask", return_value=True), \
         patch("subprocess.run"), \
         patch("shutil.copytree") as mock_copytree, \
         patch("shutil.copy2") as mock_copy2:

        # Run in non-interactive mode with repo_url provided to avoid Prompt.ask
        publish_skills(repo_url="https://github.com/owner/repo", interactive=False)

        # Verify copytree called with symlinks=True
        mock_copytree.assert_called_once()
        _, kwargs_tree = mock_copytree.call_args
        assert kwargs_tree.get("symlinks") is True

        # Verify copy2 called with follow_symlinks=False
        mock_copy2.assert_called_once()
        _, kwargs_copy2 = mock_copy2.call_args
        assert kwargs_copy2.get("follow_symlinks") is False
