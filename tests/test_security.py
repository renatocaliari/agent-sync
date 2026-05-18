"""Security regression tests for agent-sync."""

from agent_sync.skills_delete import SkillsDeleter
from agent_sync.validators import validate_github_url, validate_repo_name, validate_skill_name


def test_validate_repo_name_argument_injection():
    """Verify argument injection prevention in repo names."""
    assert validate_repo_name("-bad/repo") is False
    assert validate_repo_name("owner/repo") is True


def test_validate_github_url_argument_injection():
    """Verify argument injection prevention in GitHub URLs."""
    assert validate_github_url("https://github.com/-bad/repo") is False
    assert validate_github_url("https://github.com/owner/repo") is True


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


def test_shutil_copy_preserves_symlinks(tmp_path, monkeypatch):
    """Verify that publishing preserves symlinks instead of following them.

    This prevents leaking content of files outside the intended sync directory.
    """
    import shutil
    from unittest.mock import MagicMock, patch

    from agent_sync.publish import _push_agents_to_repo

    # 1. Setup source with a symlink to a sensitive file
    agent_dir = tmp_path / "agent_config"
    agent_dir.mkdir()

    sensitive_file = tmp_path / "sensitive.txt"
    sensitive_file.write_text("SECRET")

    symlink_file = agent_dir / "AGENTS.md"
    symlink_file.symlink_to(sensitive_file)

    # 2. Mock dependencies
    mock_config = MagicMock()
    mock_config.published_agents = []

    # Mock git operations to avoid real calls
    monkeypatch.setattr("agent_sync.publish._git_clone_or_init", MagicMock())
    monkeypatch.setattr("agent_sync.publish._git_push", MagicMock())

    # 3. Test _push_agents_to_repo
    items = [{"agent": "test-agent", "filename": "AGENTS.md", "path": symlink_file}]

    repo_url = "https://github.com/user/repo"

    # We need to capture the temporary directory used by _push_agents_to_repo
    # or mock tempfile.TemporaryDirectory. For simplicity, we'll verify shutil.copy2 call.
    with patch("agent_sync.publish.shutil.copy2", wraps=shutil.copy2) as mock_copy2:
        _push_agents_to_repo(items, repo_url, mock_config)

        # Verify copy2 was called with follow_symlinks=False
        mock_copy2.assert_called_once()
        args, kwargs = mock_copy2.call_args
        assert kwargs.get("follow_symlinks") is False, (
            "shutil.copy2 must be called with follow_symlinks=False"
        )

    # 4. Verify the actual effect using a controlled shutil.copytree call (as in publish_skills)
    dst_dir = tmp_path / "dst"
    shutil.copytree(agent_dir, dst_dir, symlinks=True)

    copied_link = dst_dir / "AGENTS.md"
    assert copied_link.is_symlink(), "copytree should preserve symlinks when symlinks=True"
    # Content should not be "SECRET" if it's a symlink (it just points to it)
    assert not copied_link.is_file() or copied_link.is_symlink()
