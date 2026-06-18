import fnmatch
from agent_sync.publish.local_source import _is_valid_skill_name as local_validate
from agent_sync.publish.external_source import _is_valid_skill_name as external_validate
from agent_sync.publish.git_publish import _ignore_func, DEFAULT_IGNORE_PATTERNS

def test_validate_skill_name_rejects_newline():
    """Verify that skill name validation rejects trailing newlines."""
    name_with_newline = "myskill\n"
    assert local_validate(name_with_newline) is False, "Local validation should reject newline"
    assert external_validate(name_with_newline) is False, "External validation should reject newline"

    assert local_validate("my-skill-123") is True
    assert external_validate("my-skill-123") is True

def test_ignore_func_correctly_filters_sensitive_files():
    """Verify that _ignore_func correctly filters sensitive files and directories."""
    ignore = _ignore_func(*DEFAULT_IGNORE_PATTERNS)

    # Test cases: (name, should_be_ignored)
    test_cases = [
        ("sessions", True),
        ("cache", True),
        (".cache", True),
        ("models.json", True),
        ("models.yaml", True),
        (".env", True),
        ("my_skill.md", False),
        ("SKILL.md", False),
        (".git", True),
        ("debug.log", True),
        ("data.sqlite", True),
        ("private.key", True),
    ]

    names = [tc[0] for tc in test_cases]
    ignored = ignore(None, names)

    for name, should_ignore in test_cases:
        is_ignored = name in ignored
        assert is_ignored == should_ignore, f"Expected {name} to be ignored={should_ignore}, but got {is_ignored}"

if __name__ == "__main__":
    # If run directly, run the tests
    try:
        test_validate_skill_name_rejects_newline()
        print("✓ test_validate_skill_name_rejects_newline passed")
        test_ignore_func_correctly_filters_sensitive_files()
        print("✓ test_ignore_func_correctly_filters_sensitive_files passed")
    except AssertionError as e:
        print(f"✗ Test failed: {e}")
        exit(1)
