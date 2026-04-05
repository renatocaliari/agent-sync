"""Security regression tests for agent-sync."""

import pytest
from agent_sync.validators import validate_repo_name, validate_github_url, validate_skill_name


class TestSecurityValidators:
    """Security tests for validators."""

    def test_validate_skill_name_path_traversal(self):
        """Test that skill name validator blocks path traversal."""
        assert validate_skill_name("../etc/passwd") is False
        assert validate_skill_name("..") is False
        assert validate_skill_name("skill/name") is False
        assert validate_skill_name("/absolute/path") is False
        assert validate_skill_name("~/.ssh/id_rsa") is False

    def test_validate_skill_name_newline_injection(self):
        """Test that skill name validator blocks newline injection."""
        assert validate_skill_name("skill\nname") is False
        assert validate_skill_name("skill-name\n") is False
        assert validate_skill_name("\nskill-name") is False

    def test_validate_repo_name_newline_injection(self):
        """Test that repo name validator blocks newline injection."""
        assert validate_repo_name("repo-name\n") is False
        assert validate_repo_name("owner/repo\n") is False
        assert validate_repo_name("\nrepo") is False

    def test_validate_github_url_newline_injection(self):
        """Test that GitHub URL validator blocks newline injection."""
        assert validate_github_url("https://github.com/owner/repo\n") is False
        assert validate_github_url("https://github.com/owner/repo\nls") is False

    def test_validate_skill_name_valid_chars(self):
        """Test valid skill names."""
        assert validate_skill_name("my-skill") is True
        assert validate_skill_name("skill_123") is True
        assert validate_skill_name("skill.v1") is True
        assert validate_skill_name("a") is True
        assert validate_skill_name("skill") is True

    def test_validate_skill_name_invalid_starts(self):
        """Test invalid starting characters for skill names."""
        assert validate_skill_name("-skill") is False
        assert validate_skill_name(".skill") is False
        assert validate_skill_name("_skill") is False # My regex starts with [a-zA-Z0-9]
