import pytest
import re
from pathlib import Path
import shutil
import tempfile
from agent_sync.publish.git_publish import _ignore_func, DEFAULT_IGNORE_PATTERNS
from agent_sync.publish.local_source import _is_valid_skill_name as _is_valid_local
from agent_sync.publish.external_source import _is_valid_skill_name as _is_valid_external

def test_ignore_func_fix():
    # Verifies that _ignore_func correctly ignores 'sessions', 'cache', 'models.json'
    ignore = _ignore_func(*DEFAULT_IGNORE_PATTERNS)

    names = ['sessions', 'cache', 'models.json', 'SKILL.md', '.git', 'test.log']
    ignored = ignore(None, names)

    # These SHOULD be ignored
    should_be_ignored = {'sessions', 'cache', 'models.json', '.git', 'test.log'}

    for name in should_be_ignored:
        assert name in ignored, f"Fix Failed: {name} was NOT ignored but should be!"

    assert 'SKILL.md' not in ignored

def test_skill_name_newline_injection_fix():
    # Verifies that _is_valid_skill_name rejects trailing newlines
    name_with_newline = "valid-skill\n"

    assert _is_valid_local(name_with_newline) is False, "Fix Failed: local_source still accepts trailing newline"
    assert _is_valid_external(name_with_newline) is False, "Fix Failed: external_source still accepts trailing newline"

def test_copytree_does_not_follow_symlinks_fix():
    # Verifies that symlinks are preserved as links (security fix)
    with tempfile.TemporaryDirectory() as tmp_dir:
        src = Path(tmp_dir) / "src"
        dest = Path(tmp_dir) / "dest"
        src.mkdir()

        secret_file = Path(tmp_dir) / "secret.txt"
        secret_file.write_text("sensitive data")

        # Create a symlink inside src pointing to secret_file outside src
        link = src / "link_to_secret"
        link.symlink_to(secret_file)

        # In git_publish.py we now use symlinks=True
        shutil.copytree(src, dest, symlinks=True)

        assert dest / "link_to_secret" in dest.iterdir()
        assert (dest / "link_to_secret").is_symlink(), "Fix Failed: symlink was followed!"
        # It should still point to the original secret_file (or at least be a symlink)
        assert (dest / "link_to_secret").readlink() == secret_file
