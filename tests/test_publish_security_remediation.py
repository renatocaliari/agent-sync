"""Security remediation tests for publish flow regex vulnerabilities."""

from agent_sync.publish.local_source import _is_valid_skill_name as local_valid
from agent_sync.publish.external_source import _is_valid_skill_name as external_valid


def test_local_skill_name_newline_injection():
    """Verify that local_source._is_valid_skill_name rejects newlines."""
    # These should be rejected now that we use \Z
    assert local_valid("skill\n") is False
    assert local_valid("skill\r") is False
    assert local_valid("skill\r\n") is False

    # Valid names should still pass
    assert local_valid("valid-skill") is True
    assert local_valid("skill123") is True


def test_external_skill_name_newline_injection():
    """Verify that external_source._is_valid_skill_name rejects newlines."""
    # These should be rejected now that we use \Z
    assert external_valid("skill\n") is False
    assert external_valid("skill\r") is False
    assert external_valid("skill\r\n") is False

    # Valid names should still pass
    assert external_valid("valid-skill") is True
    assert external_valid("skill123") is True
