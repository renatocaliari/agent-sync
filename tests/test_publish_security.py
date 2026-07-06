import pytest
from pathlib import Path
from agent_sync.publish.local_source import _is_valid_skill_name as local_valid
from agent_sync.publish.external_source import _is_valid_skill_name as external_valid

def test_skill_name_validation_no_newline():
    assert local_valid("my-skill") is True
    assert local_valid("my-skill\n") is False
    assert external_valid("ext-skill") is True
    assert external_valid("ext-skill\n") is False

def test_publish_ignore_logic():
    from agent_sync.publish.git_publish import _ignore_func, DEFAULT_IGNORE_PATTERNS
    ignore = _ignore_func(*DEFAULT_IGNORE_PATTERNS)

    # Files/dirs that should be ignored
    ignored_cases = [
        'sessions',
        '.git',
        'cache',
        '.cache',
        'my.log',
        'models.json',
        'db.sqlite',
        '.env',
        'key.pem'
    ]

    # Files that should NOT be ignored
    safe_cases = [
        'SKILL.md',
        'README.md',
        'script.py',
        'data.csv'
    ]

    all_test_names = ignored_cases + safe_cases
    ignored_result = ignore(None, all_test_names)

    for case in ignored_cases:
        assert case in ignored_result, f"'{case}' should have been ignored"

    for case in safe_cases:
        assert case not in ignored_result, f"'{case}' should NOT have been ignored"
