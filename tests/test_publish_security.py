import pytest
import shutil
import tempfile
from pathlib import Path
import os
from agent_sync.publish.git_publish import do_git_publish, publish_all, DEFAULT_IGNORE_PATTERNS
from agent_sync.publish.local_source import _is_valid_skill_name as local_valid_name
from agent_sync.publish.external_source import _is_valid_skill_name as external_valid_name
from unittest.mock import MagicMock, patch

def test_publish_ignore_patterns_logic():
    """Verify that sensitive files are ignored during publish."""
    with tempfile.TemporaryDirectory() as tmp_src:
        src = Path(tmp_src)
        (src / "sessions").mkdir()
        (src / "sessions" / "sensitive.txt").write_text("secret")
        (src / "models.json").write_text("{}")
        (src / "normal.txt").write_text("hello")

        with tempfile.TemporaryDirectory() as tmp_dest:
            dest = Path(tmp_dest)

            # Simulate do_git_publish's copy logic
            shutil.copytree(src, dest / "items", ignore=shutil.ignore_patterns(*DEFAULT_IGNORE_PATTERNS))

            assert not (dest / "items" / "sessions").exists()
            assert not (dest / "items" / "models.json").exists()
            assert (dest / "items" / "normal.txt").exists()

def test_publish_valid_skill_name_anchors():
    """Verify that skill name validation correctly uses anchors to reject newlines."""
    # Test both local and external versions
    for validator in [local_valid_name, external_valid_name]:
        assert validator("valid-skill") is True
        assert validator("skill-123") is True
        assert validator("skill\n") is False
        assert validator("skill\r") is False
        assert validator("skill-name\n") is False
        assert validator("invalid_name") is False # Only hyphens allowed in these specific validators
