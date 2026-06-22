import pytest
import re
from pathlib import Path
from agent_sync.publish.local_source import _is_valid_skill_name as _is_valid_local
from agent_sync.publish.external_source import _is_valid_skill_name as _is_valid_external
from agent_sync.publish.git_publish import _ignore_func, DEFAULT_IGNORE_PATTERNS

def test_skill_name_newline_remediation():
    """Verify that internal skill name validators now reject newline injection."""
    bad_name = "valid-skill\n"
    # These should now be False
    assert _is_valid_local(bad_name) is False
    assert _is_valid_external(bad_name) is False

    # Valid names should still pass
    assert _is_valid_local("valid-skill") is True
    assert _is_valid_external("valid-skill") is True

def test_ignore_func_logic_remediation():
    """Verify that _ignore_func correctly ignores default patterns after fix."""
    ignore = _ignore_func(*DEFAULT_IGNORE_PATTERNS)

    # Should be ignored (now fixed)
    assert "sessions" in ignore(None, ["sessions"])
    assert "cache" in ignore(None, ["cache"])
    assert "models.json" in ignore(None, ["models.json"])
    assert ".env" in ignore(None, [".env"])
    assert "test.log" in ignore(None, ["test.log"])

    # Should NOT be ignored
    assert "SKILL.md" not in ignore(None, ["SKILL.md"])
    assert "valid-skill" not in ignore(None, ["valid-skill"])
