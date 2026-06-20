import os
import shutil
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

from agent_sync.publish.git_publish import _ignore_func, DEFAULT_IGNORE_PATTERNS, publish_skills
from agent_sync.publish.local_source import _is_valid_skill_name as _is_valid_local
from agent_sync.publish.external_source import _is_valid_skill_name as _is_valid_external
from agent_sync.publish.agents_source import publish_agents

class TestPublishSecurityRegression:
    """Security regression tests for the publish flow."""

    def test_ignore_func_data_leakage(self):
        """Verify that _ignore_func correctly filters sensitive patterns."""
        ignore = _ignore_func(*DEFAULT_IGNORE_PATTERNS)

        # Test directory patterns
        assert "sessions" in ignore(None, ["sessions", "normal_dir"])
        assert ".git" in ignore(None, [".git", "normal_dir"])

        # Test file patterns
        assert "models.json" in ignore(None, ["models.json", "data.txt"])
        assert "test.log" in ignore(None, ["test.log", "test.txt"])
        assert ".env" in ignore(None, [".env", "README.md"])

    def test_skill_name_regex_newline_injection(self):
        """Verify that skill name validation rejects trailing newlines (regression)."""
        bad_name = "skill-name\n"
        assert _is_valid_local(bad_name) is False, "Local skill name validation should reject trailing newlines"
        assert _is_valid_external(bad_name) is False, "External skill name validation should reject trailing newlines"

    def test_publish_skills_symlink_leakage(self, tmp_path):
        """Verify that publish_skills does not follow symlinks during copy."""
        # Use a fixed temporary directory that we don't shutil.rmtree in finally
        # or at least we can control it.
        # Actually, let's just not mock mkdtemp and use the real one, but we need to find where it is.
        src_dir = tmp_path / "src_skills"
        src_dir.mkdir()
        skill_dir = src_dir / "my-skill"
        skill_dir.mkdir()
        (skill_dir / "SKILL.md").write_text("# My Skill")

        # Create a sensitive file outside the skill directory
        sensitive_file = tmp_path / "sensitive.txt"
        sensitive_file.write_text("SENSITIVE DATA")

        # Create a symlink inside the skill directory pointing to the sensitive file
        leak_link = skill_dir / "leak.txt"
        leak_link.symlink_to(sensitive_file)

        # Mock dependencies for publish_skills
        mock_source = MagicMock()
        mock_source.source_id = "local"
        mock_skill = MagicMock()
        mock_skill.name = "my-skill"
        mock_skill.path = skill_dir
        mock_source.skills = [mock_skill]

        with patch("agent_sync.publish.git_publish.git_commit_and_push"):
            # Instead of mocking mkdtemp and letting the real code rmtree it,
            # let's mock shutil.rmtree to prevent it from deleting our verification directory.
            with patch("agent_sync.publish.git_publish.shutil.rmtree") as mock_rmtree:
                with patch("agent_sync.publish.git_publish.tempfile.mkdtemp") as mock_mkdtemp:
                    publish_tmp = tmp_path / "publish_tmp"
                    publish_tmp.mkdir()
                    mock_mkdtemp.return_value = str(publish_tmp)

                    publish_skills({"local": ["my-skill"]}, [mock_source], "https://github.com/test/repo")

                    # Check if the leaked file content was copied
                    published_link = publish_tmp / "skills" / "local" / "my-skill" / "leak.txt"
                    assert os.path.lexists(str(published_link)), f"Published file should exist (at least as a symlink) at {published_link}"
                if published_link.is_symlink():
                    # Symlink preserved, success
                    pass
                else:
                    # If it's a regular file, it means it followed the symlink and copied the content!
                    content = published_link.read_text()
                    assert content != "SENSITIVE DATA", "Security breach: symlink content was leaked!"

    def test_publish_agents_symlink_leakage(self, tmp_path):
        """Verify that publish_agents does not follow symlinks during copy."""
        # Create a mock agent instruction file
        agent_file = tmp_path / "my-agent.md"
        agent_file.write_text("# My Agent")

        # Create a sensitive file
        sensitive_file = tmp_path / "sensitive_agent.txt"
        sensitive_file.write_text("AGENT SECRET")

        # Mock discover_local_agents to return a symlink
        mock_agent = MagicMock()
        mock_agent.name = "my-agent"

        # In reality, path is usually a string. Let's make it a symlink.
        agent_link = tmp_path / "agent_link.md"
        agent_link.symlink_to(sensitive_file)
        mock_agent.path = str(agent_link)

        with patch("agent_sync.publish.agents_source.discover_local_agents", return_value=[mock_agent]):
            with patch("agent_sync.publish.agents_source.shutil.rmtree") as mock_rmtree:
                with patch("agent_sync.publish.agents_source.tempfile.mkdtemp") as mock_mkdtemp:
                    publish_tmp = tmp_path / "agent_publish_tmp"
                    publish_tmp.mkdir()
                    mock_mkdtemp.return_value = str(publish_tmp)

                    with patch("agent_sync.publish.agents_source.subprocess.run"):
                        publish_agents({"agents": ["my-agent"]}, "https://github.com/test/repo")

                        published_agent = publish_tmp / "agents" / "my-agent.md"
                        assert os.path.lexists(str(published_agent)), f"Published agent should exist at {published_agent}"
                    if not published_agent.is_symlink():
                        # If it's a regular file, check it didn't copy sensitive data
                        content = published_agent.read_text()
                        assert content != "AGENT SECRET", "Security breach: agent symlink followed!"
