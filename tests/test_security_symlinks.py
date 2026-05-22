import os
import shutil
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock
import pytest
from agent_sync.publish.git_publish import do_git_publish, publish_all

def test_do_git_publish_preserves_symlinks(tmp_path):
    """Verify that do_git_publish preserves symlinks and doesn't leak content."""
    # 1. Setup secret file outside source
    secret_content = "SENSITIVE DATA"
    secret_file = tmp_path / "secret.txt"
    secret_file.write_text(secret_content)

    # 2. Setup source directory with a symlink
    source_dir = tmp_path / "source_skill"
    source_dir.mkdir()
    (source_dir / "SKILL.md").write_text("# Test Skill")

    # Create symlink pointing to secret
    symlink_path = source_dir / "secret_link.txt"
    os.symlink(secret_file, symlink_path)

    # 3. Mock git operations to prevent actual git commands
    with patch("agent_sync.publish.git_publish.git_commit_and_push"):
        # Patch rmtree to keep the directory for inspection
        with patch("agent_sync.publish.git_publish.shutil.rmtree"):
            # We need to capture the temporary directory created by do_git_publish
            publish_tmp = tmp_path / "publish_tmp"
            publish_tmp.mkdir()

            with patch("agent_sync.publish.git_publish.tempfile.mkdtemp", return_value=str(publish_tmp)):
                items = [(source_dir, "test-skill")]

                do_git_publish(
                    items=items,
                    subdir="skills",
                    readme_generator=MagicMock(),
                    count=1,
                    item_name="skills",
                    repo="https://github.com/test/repo"
                )

                # 4. Verify that the symlink in the temporary directory is still a symlink
                published_file = publish_tmp / "skills" / "test-skill" / "secret_link.txt"

                assert published_file.is_symlink(), f"Published file {published_file} should be a symlink"
                assert os.readlink(published_file) == str(secret_file), "Symlink should point to the original secret file"

def test_publish_all_preserves_symlinks(tmp_path):
    """Verify that publish_all preserves symlinks."""
    # Setup secret
    secret_file = tmp_path / "secret.txt"
    secret_file.write_text("SENSITIVE")

    # Setup skill source
    skill_dir = tmp_path / "skill_dir"
    skill_dir.mkdir()
    os.symlink(secret_file, skill_dir / "link.txt")

    # Mock SkillSource
    mock_skill = MagicMock()
    mock_skill.name = "my-skill"
    mock_skill.path = skill_dir

    mock_source = MagicMock()
    mock_source.source_id = "local"
    mock_source.skills = [mock_skill]

    publish_tmp = tmp_path / "publish_all_tmp"
    publish_tmp.mkdir()

    with patch("agent_sync.publish.git_publish.git_commit_and_push"):
        with patch("agent_sync.publish.git_publish.shutil.rmtree"):
            with patch("agent_sync.publish.git_publish.tempfile.mkdtemp", return_value=str(publish_tmp)):
                publish_all(
                    skills_selected={"local": ["my-skill"]},
                    skills_sources=[mock_source],
                    agents_selected=[],
                    published_repo="https://github.com/test/repo"
                )

                published_link = publish_tmp / "skills" / "local" / "my-skill" / "link.txt"
                assert published_link.is_symlink()
                assert os.readlink(published_link) == str(secret_file)

def test_publish_agents_preserves_symlinks(tmp_path):
    """Verify that publish_agents preserves symlinks."""
    from agent_sync.publish.agents_source import publish_agents as agents_publish_logic

    # Setup secret
    secret_file = tmp_path / "secret.txt"
    secret_file.write_text("SENSITIVE AGENT DATA")

    # Setup agent instruction file as a symlink
    agent_instr = tmp_path / "agent_instr.md"
    os.symlink(secret_file, agent_instr)

    # Mock discover_local_agents
    mock_agent = MagicMock()
    mock_agent.name = "my-agent"
    mock_agent.path = str(agent_instr)

    publish_tmp = tmp_path / "publish_agents_tmp"
    publish_tmp.mkdir()

    with patch("agent_sync.publish.agents_source.discover_local_agents", return_value=[mock_agent]):
        with patch("agent_sync.publish.agents_source.tempfile.mkdtemp", return_value=str(publish_tmp)):
            with patch("agent_sync.publish.agents_source.shutil.rmtree"):
                # Mock subprocess.run for git commands
                with patch("agent_sync.publish.agents_source.subprocess.run"):
                    agents_publish_logic(
                        selected={"agents": ["my-agent"]},
                        published_repo="https://github.com/test/repo"
                    )

                    published_agent = publish_tmp / "agents" / "my-agent.md"
                    assert published_agent.is_symlink()
                    assert os.readlink(published_agent) == str(secret_file)
