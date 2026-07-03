import subprocess
from pathlib import Path
import pytest
from unittest.mock import patch, MagicMock

from agent_sync.publish.local_source import _is_valid_skill_name as _is_valid_local
from agent_sync.publish.external_source import _is_valid_skill_name as _is_valid_external
from agent_sync.publish.git_publish import _ignore_func, do_git_publish
from agent_sync.sync import _sanitize_git_args, SyncManager

def test_skill_name_validation_newline_injection():
    """Verify that skill names with newlines are rejected."""
    bad_name = "myskill\n"
    assert _is_valid_local(bad_name) is False
    assert _is_valid_external(bad_name) is False

    good_name = "my-skill-123"
    assert _is_valid_local(good_name) is True
    assert _is_valid_external(good_name) is True

def test_ignore_func_robustness():
    """Verify that _ignore_func correctly matches patterns."""
    patterns = ["sessions", "cache", "*.log", ".git"]
    ignore = _ignore_func(*patterns)

    names = ["sessions", "cache", "my.log", ".git", "valid.md"]
    ignored = ignore(None, names)

    assert "sessions" in ignored
    assert "cache" in ignored
    assert "my.log" in ignored
    assert ".git" in ignored
    assert "valid.md" not in ignored

def test_sanitize_git_args():
    """Verify that command arguments are sanitized."""
    args = ["git", "clone", "https://ghp_SECRET@github.com/u/r.git", "dest"]
    sanitized = _sanitize_git_args(args)
    assert "ghp_SECRET" not in sanitized[2]
    assert "https://***@github.com/u/r.git" == sanitized[2]

def test_do_git_publish_symlinks_protection(tmp_path):
    """Verify that do_git_publish uses symlinks=True and follow_symlinks=False."""
    # This is a bit tricky to test without complex mocking,
    # but we can verify the code by inspecting the call if we mock shutil.

    with patch("agent_sync.publish.git_publish.shutil.copytree") as mock_copytree, \
         patch("agent_sync.publish.git_publish.shutil.copy2") as mock_copy2, \
         patch("agent_sync.publish.git_publish.git_commit_and_push"):

        from agent_sync.publish.git_publish import do_git_publish

        items = [(tmp_path / "dir", "dir"), (tmp_path / "file.md", "file.md")]
        (tmp_path / "dir").mkdir()
        (tmp_path / "file.md").touch()

        do_git_publish(items, "subdir", MagicMock(), 2, "items", "repo")

        # Verify copytree called with symlinks=True
        assert mock_copytree.call_args[1]["symlinks"] is True
        # Verify copy2 called with follow_symlinks=False
        assert mock_copy2.call_args[1]["follow_symlinks"] is False

def test_sync_manager_run_git_sanitizes_args(tmp_path):
    """Verify SyncManager._run_git redacts tokens from cmd in CalledProcessError."""
    repo = tmp_path / "repo"
    repo.mkdir()

    sm = SyncManager(MagicMock())
    sm.repo_dir = repo

    fake_result = MagicMock()
    fake_result.returncode = 1
    fake_result.stdout = ""
    fake_result.stderr = ""

    cmd_with_token = ["git", "push", "https://ghp_TOKEN@github.com/u/r.git"]

    with patch("agent_sync.sync.subprocess.run", return_value=fake_result):
        with pytest.raises(subprocess.CalledProcessError) as excinfo:
            sm._run_git(*cmd_with_token[1:])

        assert "ghp_TOKEN" not in str(excinfo.value.cmd)
        assert "***" in str(excinfo.value.cmd)
