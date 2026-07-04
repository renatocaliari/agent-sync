
import pytest
import shutil
from pathlib import Path
import tempfile
from agent_sync.publish.git_publish import _ignore_func, DEFAULT_IGNORE_PATTERNS
from agent_sync.publish.local_source import _is_valid_skill_name as _is_valid_local
from agent_sync.publish.external_source import _is_valid_skill_name as _is_valid_external

def test_sensitive_data_exclusion():
    """Verify that sensitive directories and files are excluded from publish."""
    with tempfile.TemporaryDirectory() as tmp_src:
        src = Path(tmp_src)

        # Sensitive directories
        (src / "sessions").mkdir()
        (src / "sessions" / "secret.txt").write_text("sensitive")
        (src / "cache").mkdir()
        (src / ".git").mkdir()

        # Sensitive files
        (src / ".env").write_text("API_KEY=123")
        (src / "models.json").write_text("{}")
        (src / "personal.pem").write_text("key")

        # Normal files
        (src / "SKILL.md").write_text("# My Skill")
        (src / "script.py").write_text("print('hello')")

        ignore_callable = _ignore_func(*DEFAULT_IGNORE_PATTERNS)

        with tempfile.TemporaryDirectory() as tmp_dest:
            dest = Path(tmp_dest) / "out"
            shutil.copytree(src, dest, ignore=ignore_callable)

            # Check that sensitive items are NOT present
            assert not (dest / "sessions").exists()
            assert not (dest / "cache").exists()
            assert not (dest / ".git").exists()
            assert not (dest / ".env").exists()
            assert not (dest / "models.json").exists()
            assert not (dest / "personal.pem").exists()

            # Check that normal items ARE present
            assert (dest / "SKILL.md").exists()
            assert (dest / "script.py").exists()

def test_skill_name_validation_newline_injection():
    """Verify that skill names with trailing newlines are rejected."""
    # Both local and external should reject newlines
    assert _is_valid_local("valid-skill") is True
    assert _is_valid_local("invalid-skill\n") is False

    assert _is_valid_external("valid-skill") is True
    assert _is_valid_external("invalid-skill\n") is False

def test_skill_name_validation_consecutive_hyphens():
    """Verify that skill names with consecutive hyphens are rejected."""
    assert _is_valid_local("my--skill") is False
    assert _is_valid_external("my--skill") is False

def test_skill_name_validation_start_end_hyphens():
    """Verify that skill names starting or ending with hyphens are rejected."""
    assert _is_valid_local("-skill") is False
    assert _is_valid_local("skill-") is False
    assert _is_valid_external("-skill") is False
    assert _is_valid_external("skill-") is False
