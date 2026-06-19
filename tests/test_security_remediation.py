import shutil
import tempfile
from pathlib import Path
import pytest
from agent_sync.publish.git_publish import _ignore_func, DEFAULT_IGNORE_PATTERNS
from agent_sync.publish.local_source import _is_valid_skill_name as local_valid
from agent_sync.publish.external_source import _is_valid_skill_name as external_valid

def test_ignore_func_security():
    """Verify that sensitive files are correctly ignored by _ignore_func."""
    ignore = _ignore_func(*DEFAULT_IGNORE_PATTERNS)

    # Files that should be ignored
    assert 'sessions' in ignore(None, ['sessions', 'SKILL.md'])
    assert 'models.json' in ignore(None, ['models.json', 'README.md'])
    assert '.env' in ignore(None, ['.env', 'other.txt'])
    assert 'test.log' in ignore(None, ['test.log', 'main.py'])
    assert '.git' in ignore(None, ['.git', 'content'])

    # Files that should NOT be ignored
    assert 'SKILL.md' not in ignore(None, ['sessions', 'SKILL.md'])
    assert 'README.md' not in ignore(None, ['models.json', 'README.md'])

def test_skill_name_validation_newline_injection():
    """Verify that skill names with trailing newlines are rejected (security fix)."""
    bad_name = 'valid-name\n'

    assert local_valid('valid-name') is True
    assert local_valid(bad_name) is False

    assert external_valid('valid-name') is True
    assert external_valid(bad_name) is False

def test_shutil_copytree_with_ignore_integration():
    """Integration test to verify shutil.copytree actually respects the ignore function."""
    with tempfile.TemporaryDirectory() as tmp_src:
        src = Path(tmp_src)
        (src / 'sessions').mkdir()
        (src / 'sessions' / 'secret.txt').write_text('secret')
        (src / 'models.json').write_text('{}')
        (src / 'SKILL.md').write_text('content')
        (src / 'normal-dir').mkdir()
        (src / 'normal-dir' / 'file.txt').write_text('hello')

        with tempfile.TemporaryDirectory() as tmp_dest:
            dest = Path(tmp_dest) / 'dest'
            ignore = _ignore_func(*DEFAULT_IGNORE_PATTERNS)
            shutil.copytree(src, dest, ignore=ignore)

            assert dest.exists()
            assert (dest / 'SKILL.md').exists()
            assert (dest / 'normal-dir' / 'file.txt').exists()

            # These should NOT exist in destination
            assert not (dest / 'sessions').exists()
            assert not (dest / 'models.json').exists()
