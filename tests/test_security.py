"""Security regression tests."""

import pytest
from agent_sync.validators import validate_repo_name, validate_github_url, validate_skill_name


class TestSecurityValidators:
    """Security tests for validators."""

    def test_validate_repo_name_newline_injection(self):
        """Test that validate_repo_name rejects newline injection."""
        # Previous implementation (with $) would match this
        assert validate_repo_name("myrepo\n") is False
        assert validate_repo_name("myrepo\r") is False
        assert validate_repo_name("owner/repo\n") is False

    def test_validate_github_url_newline_injection(self):
        """Test that validate_github_url rejects newline injection."""
        assert validate_github_url("https://github.com/owner/repo\n") is False
        assert validate_github_url("https://github.com/owner\n/repo") is False
        # netloc is checked by urlparse, but owner/repo parts use regex
        assert validate_github_url("https://github.com/owner\n/repo") is False

    def test_validate_skill_name_basic(self):
        """Test basic valid skill names."""
        assert validate_skill_name("my-skill") is True
        assert validate_skill_name("skill.v1") is True
        assert validate_skill_name("skill_name") is True
        assert validate_skill_name("a") is True

    def test_validate_skill_name_traversal(self):
        """Test that validate_skill_name rejects path traversal attempts."""
        assert validate_skill_name("../etc/passwd") is False
        assert validate_skill_name("..") is False
        assert validate_skill_name("/") is False
        assert validate_skill_name("skill/name") is False
        assert validate_skill_name("./skill") is False

    def test_validate_skill_name_invalid_chars(self):
        """Test that validate_skill_name rejects invalid characters."""
        assert validate_skill_name("skill name") is False
        assert validate_skill_name("skill$") is False
        assert validate_skill_name("skill;") is False
        assert validate_skill_name("skill\n") is False
        assert validate_skill_name("-skill") is False  # Must start with alphanumeric
        assert validate_skill_name(".skill") is False  # Must start with alphanumeric

    def test_validate_skill_name_length(self):
        """Test skill name length limits."""
        assert validate_skill_name("a" * 64) is True
        assert validate_skill_name("a" * 65) is False
