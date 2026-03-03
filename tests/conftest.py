"""Test suite for agent-sync."""

import pytest


@pytest.fixture
def tmp_config_dir(tmp_path):
    """Create a temporary config directory."""
    config_dir = tmp_path / ".config" / "agent-sync"
    config_dir.mkdir(parents=True)
    return config_dir


@pytest.fixture
def tmp_env_file(tmp_config_dir):
    """Create a temporary .env file."""
    env_file = tmp_config_dir / ".env"
    env_file.touch()
    return env_file
