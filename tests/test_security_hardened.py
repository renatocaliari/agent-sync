"""Tests for security hardening (permissions and editor validation)."""

import os
import stat
import subprocess
from pathlib import Path
import pytest
from unittest.mock import MagicMock, patch

from agent_sync.security import ensure_secure_dir, secure_open
from agent_sync.validators import validate_editor


def test_ensure_secure_dir_permissions(tmp_path):
    """Test that ensure_secure_dir sets 0o700 permissions."""
    test_dir = tmp_path / "secure_dir"
    ensure_secure_dir(test_dir)

    assert test_dir.exists()
    assert test_dir.is_dir()

    mode = os.stat(test_dir).st_mode
    assert stat.S_IMODE(mode) == 0o700


def test_secure_open_permissions(tmp_path):
    """Test that secure_open sets 0o600 permissions."""
    test_file = tmp_path / "secure_file.txt"
    with secure_open(test_file, "w") as f:
        f.write("test content")

    assert test_file.exists()

    mode = os.stat(test_file).st_mode
    assert stat.S_IMODE(mode) == 0o600


def test_validate_editor_safe():
    """Test validate_editor with safe editor commands."""
    assert validate_editor("nano") is True
    assert validate_editor("vim") is True
    assert validate_editor("code") is True
    assert validate_editor("/usr/bin/nano") is True
    assert validate_editor("subl") is True
    # Test flags
    assert validate_editor("code --wait") is True
    assert validate_editor("vim -n") is True
    # Test Windows paths
    assert validate_editor("C:/Program Files/Editor.exe") is True


def test_validate_editor_unsafe():
    """Test validate_editor with unsafe editor commands."""
    assert validate_editor("nano; rm -rf /") is False
    assert validate_editor("vim | wall") is False
    assert validate_editor("code & whoami") is False
    assert validate_editor("`id`") is False
    assert validate_editor("$(id)") is False
    assert validate_editor("editor_name$IFS") is False
    assert validate_editor("") is False


@patch("subprocess.run")
def test_config_edit_safe(mock_run, monkeypatch):
    """Test that config_edit uses shlex.split and works with safe editor."""
    from agent_sync.cli import main
    from click.testing import CliRunner

    runner = CliRunner()

    # Mock environment and config
    monkeypatch.setenv("EDITOR", "nano")

    with patch("agent_sync.cli.Config") as MockConfig:
        instance = MockConfig.return_value
        fake_path = MagicMock(spec=Path)
        fake_path.__str__.return_value = "/tmp/fake_config.yaml"
        fake_path.exists.return_value = True
        instance.config_path = fake_path

        result = runner.invoke(main, ["config", "edit"])

        # Verify subprocess.run was called with split command
        mock_run.assert_called_once()
        args = mock_run.call_args[0][0]
        assert args[0] == "nano"
        assert result.exit_code == 0


@patch("subprocess.run")
def test_config_edit_with_flags(mock_run, monkeypatch):
    """Test that config_edit handles EDITOR with flags."""
    from agent_sync.cli import main
    from click.testing import CliRunner

    runner = CliRunner()

    # Editor with flags
    monkeypatch.setenv("EDITOR", "code --wait")

    with patch("agent_sync.cli.Config") as MockConfig:
        instance = MockConfig.return_value
        fake_path = MagicMock(spec=Path)
        fake_path.__str__.return_value = "/tmp/fake_config.yaml"
        fake_path.exists.return_value = True
        instance.config_path = fake_path

        result = runner.invoke(main, ["config", "edit"])

        mock_run.assert_called_once()
        args = mock_run.call_args[0][0]
        assert args == ["code", "--wait", "/tmp/fake_config.yaml"]
        assert result.exit_code == 0


@patch("subprocess.run")
def test_config_edit_unsafe_editor(mock_run, monkeypatch):
    """Test that config_edit blocks unsafe EDITOR."""
    from agent_sync.cli import main
    from click.testing import CliRunner

    runner = CliRunner()

    # Unsafe editor in environment
    monkeypatch.setenv("EDITOR", "nano; id")

    with patch("agent_sync.cli.Config") as MockConfig:
        instance = MockConfig.return_value
        fake_path = MagicMock(spec=Path)
        fake_path.__str__.return_value = "/tmp/fake_config.yaml"
        fake_path.exists.return_value = True
        instance.config_path = fake_path

        result = runner.invoke(main, ["config", "edit"])

        # Verify subprocess.run was NOT called
        mock_run.assert_not_called()
        assert "Invalid editor command" in result.output
        assert result.exit_code == 0 # Command finished gracefully with error message
