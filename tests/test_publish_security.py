import os
import shutil
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from agent_sync.publish.local_source import _is_valid_skill_name as local_valid
from agent_sync.publish.external_source import _is_valid_skill_name as external_valid
from agent_sync.publish.git_publish import _ignore_func, DEFAULT_IGNORE_PATTERNS, do_git_publish

def test_skill_name_newline_injection_fixed():
    """SECURE: Skill names with trailing newlines MUST be rejected."""
    # These should now be False
    assert local_valid("valid-skill\n") is False
    assert external_valid("valid-skill\n") is False
    assert local_valid("valid-skill") is True
    assert external_valid("valid-skill") is True

def test_ignore_func_robustness_fixed():
    """SECURE: _ignore_func MUST correctly handle DEFAULT_IGNORE_PATTERNS."""
    ignore = _ignore_func(*DEFAULT_IGNORE_PATTERNS)

    names = ["sessions", "valid_file.txt", "models.json", ".git", "cache", "my.log"]
    ignored = ignore(Path("/tmp"), names)

    assert "sessions" in ignored
    assert "models.json" in ignored
    assert ".git" in ignored
    assert "cache" in ignored
    assert "my.log" in ignored
    assert "valid_file.txt" not in ignored

@patch("agent_sync.publish.git_publish.shutil.copytree")
@patch("agent_sync.publish.git_publish.shutil.copy2")
@patch("agent_sync.publish.git_publish.git_commit_and_push")
def test_git_publish_hardening(mock_push, mock_copy2, mock_copytree):
    """SECURE: do_git_publish must call shutil with security-hardened parameters."""
    mock_readme = MagicMock()

    with tempfile.TemporaryDirectory() as tmp_dir:
        src_dir = Path(tmp_dir) / "src_dir"
        src_dir.mkdir()
        src_file = Path(tmp_dir) / "src_file.txt"
        src_file.write_text("content")

        items = [(src_dir, "dest_dir"), (src_file, "dest_file.txt")]

        # Trigger publish
        do_git_publish(items, "skills", mock_readme, 2, "skills", "https://github.com/repo")

        # Verify copytree was called with symlinks=True
        assert mock_copytree.called
        # It's called once for the directory
        kwargs = mock_copytree.call_args.kwargs
        assert kwargs.get("symlinks") is True, "Security: copytree MUST preserve symlinks"

        # Verify copy2 was called with follow_symlinks=False
        assert mock_copy2.called
        kwargs = mock_copy2.call_args.kwargs
        assert kwargs.get("follow_symlinks") is False, "Security: copy2 MUST NOT follow symlinks"

def test_symlink_preservation_behavior():
    """Verify that shutil.copytree with symlinks=True actually preserves links."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        src = Path(tmp_dir) / "src"
        src.mkdir()
        secret = Path(tmp_dir) / "secret"
        secret.write_text("shh")
        link = src / "link"
        link.symlink_to(secret)

        dest = Path(tmp_dir) / "dest"
        shutil.copytree(src, dest, symlinks=True)

        assert (dest / "link").is_symlink(), "Expected symlink to be preserved"
