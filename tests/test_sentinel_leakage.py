import shutil
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock
from agent_sync.publish.git_publish import do_git_publish, publish_all
from agent_sync.publish.agents_source import publish_agents

def test_do_git_publish_preserves_symlinks(tmp_path):
    """Verify that do_git_publish preserves symlinks in skills (prevents content leakage)."""
    # 1. Setup: a secret file outside the source
    secret_file = tmp_path / "secret.txt"
    secret_file.write_text("TOP SECRET")

    # 2. Setup: a source skill directory with a symlink to the secret
    source_dir = tmp_path / "source_skill"
    source_dir.mkdir()
    (source_dir / "SKILL.md").write_text("My Skill")
    link_file = source_dir / "leak.txt"
    link_file.symlink_to(secret_file)

    items = [(source_dir, "my-skill")]

    # 3. Mock dependencies to avoid actual git/console output and deletion
    with patch("agent_sync.publish.git_publish.git_commit_and_push"), \
         patch("agent_sync.publish.git_publish.console"), \
         patch("agent_sync.publish.git_publish.shutil.rmtree"):

        publish_tmp = tmp_path / "publish_tmp"
        publish_tmp.mkdir()

        with patch("tempfile.mkdtemp", return_value=str(publish_tmp)):
            success = do_git_publish(
                items=items,
                subdir="skills",
                readme_generator=MagicMock(),
                count=1,
                item_name="skills",
                repo="https://github.com/user/repo.git"
            )

            assert success is True

            # 5. Verify the destination
            dest_link = publish_tmp / "skills" / "my-skill" / "leak.txt"
            assert dest_link.is_symlink(), "Symlink was followed and converted to a regular file!"
            assert Path(dest_link.readlink()).resolve() == secret_file.resolve()

def test_publish_all_preserves_agent_symlinks(tmp_path):
    """Verify that publish_all preserves symlinks for agents."""
    # Setup secret
    secret_file = tmp_path / "secret.txt"
    secret_file.write_text("AGENT SECRET")

    # Setup agent file as a symlink
    agent_source = tmp_path / "my-agent.md"
    agent_source.symlink_to(secret_file)

    # Mock discover_local_agents
    MockAgent = MagicMock()
    MockAgent.name = "my-agent"
    MockAgent.path = str(agent_source)

    with patch("agent_sync.publish.git_publish.git_commit_and_push"), \
         patch("agent_sync.publish.git_publish.console"), \
         patch("agent_sync.publish.git_publish.shutil.rmtree"), \
         patch("agent_sync.publish.agents_source.discover_local_agents", return_value=[MockAgent]):

        publish_tmp = tmp_path / "publish_all_tmp"
        publish_tmp.mkdir()

        with patch("tempfile.mkdtemp", return_value=str(publish_tmp)):
            success = publish_all(
                skills_selected={},
                skills_sources=[],
                agents_selected=["my-agent"],
                published_repo="https://github.com/user/repo.git"
            )

            assert success is True
            dest_agent = publish_tmp / "agents" / "my-agent.md"
            assert dest_agent.is_symlink(), "Agent symlink was followed!"
            assert Path(dest_agent.readlink()).resolve() == secret_file.resolve()

def test_publish_agents_source_preserves_symlinks(tmp_path):
    """Verify that publish_agents in agents_source module preserves symlinks."""
     # Setup secret
    secret_file = tmp_path / "secret.txt"
    secret_file.write_text("AGENT SOURCE SECRET")

    # Setup agent file as a symlink
    agent_source = tmp_path / "my-agent-source.md"
    agent_source.symlink_to(secret_file)

    # Mock discover_local_agents
    MockAgent = MagicMock()
    MockAgent.name = "my-agent-source"
    MockAgent.path = str(agent_source)

    with patch("agent_sync.publish.agents_source.subprocess.run"), \
         patch("agent_sync.publish.agents_source.console"), \
         patch("agent_sync.publish.agents_source.shutil.rmtree"), \
         patch("agent_sync.publish.agents_source.discover_local_agents", return_value=[MockAgent]):

        publish_tmp = tmp_path / "agents_source_tmp"
        publish_tmp.mkdir()

        # Patch tempfile.mkdtemp in agents_source
        with patch("tempfile.mkdtemp", return_value=str(publish_tmp)):
            success = publish_agents(
                selected={"agents": ["my-agent-source"]},
                published_repo="https://github.com/user/repo.git"
            )

            assert success is True
            dest_agent = publish_tmp / "agents" / "my-agent-source.md"
            assert dest_agent.is_symlink(), "Agent source symlink was followed!"
            assert Path(dest_agent.readlink()).resolve() == secret_file.resolve()
