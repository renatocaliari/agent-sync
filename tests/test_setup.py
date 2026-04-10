"""Tests for the setup wizard."""

import pytest
from unittest.mock import patch, MagicMock
from pathlib import Path

from agent_sync.setup import run_setup_wizard, SetupWizard


class TestSetupWizard:
    """Test the SetupWizard class and run_setup_wizard function."""

    @patch("agent_sync.setup.SetupWizard")
    def test_run_setup_wizard_success(self, mock_wizard_class):
        """Test run_setup_wizard when the wizard completes successfully."""
        # Setup mock
        mock_wizard_instance = mock_wizard_class.return_value
        mock_wizard_instance.run.return_value = True
        mock_repo_config = {
            "name": "test-repo",
            "private": True,
            "agents": ("agent1", "agent2"),
        }
        mock_wizard_instance.get_repo_config.return_value = mock_repo_config

        # Execute
        result = run_setup_wizard()

        # Assert
        assert result == mock_repo_config
        mock_wizard_instance.run.assert_called_once()
        mock_wizard_instance.get_repo_config.assert_called_once()

    @patch("agent_sync.setup.SetupWizard")
    def test_run_setup_wizard_canceled(self, mock_wizard_class):
        """Test run_setup_wizard when the wizard is canceled."""
        # Setup mock
        mock_wizard_instance = mock_wizard_class.return_value
        mock_wizard_instance.run.return_value = False

        # Execute
        result = run_setup_wizard()

        # Assert
        assert result is None
        mock_wizard_instance.run.assert_called_once()
        mock_wizard_instance.get_repo_config.assert_not_called()

    @patch("agent_sync.setup.Config")
    def test_setup_wizard_initialization(self, mock_config_class):
        """Test SetupWizard initialization."""
        wizard = SetupWizard()
        assert wizard.selected_agents == []
        assert wizard.agent_configs == {}
        assert wizard.include_global_skills is True
        assert wizard.repo_name == ""
        assert wizard.is_private is True
        assert wizard.skills_centralized is False
        assert wizard.agent_configure_results == {}

    def test_get_repo_config(self):
        """Test get_repo_config returns correct data."""
        with patch("agent_sync.setup.Config"):
            wizard = SetupWizard()
            wizard.repo_name = "my-repo"
            wizard.is_private = False
            wizard.selected_agents = ["agent1", "agent2"]

            config = wizard.get_repo_config()

            assert config == {
                "name": "my-repo",
                "private": False,
                "agents": ("agent1", "agent2"),
            }

    @patch("agent_sync.setup.Config")
    def test_save_configuration(self, mock_config_class):
        """Test _save_configuration saves all agent configs."""
        mock_config_instance = mock_config_class.return_value
        wizard = SetupWizard()
        wizard.agent_configs = {
            "agent1": {"enabled": True},
            "agent2": {"enabled": False},
        }

        # Use patch.object to capture the output print if needed,
        # but here we focus on the logic
        with patch("agent_sync.setup.console.print"):
            wizard._save_configuration()

        assert mock_config_instance.set_agent_config.call_count == 2
        mock_config_instance.set_agent_config.assert_any_call("agent1", {"enabled": True})
        mock_config_instance.set_agent_config.assert_any_call("agent2", {"enabled": False})

    @patch("agent_sync.setup.get_all_agents")
    @patch("agent_sync.setup.console.print")
    @patch("agent_sync.setup.Config")
    def test_step_detect_agents(self, mock_config, mock_print, mock_get_agents):
        """Test _step_detect_agents identifies installed and non-installed agents."""
        # Setup mocks
        mock_agent1 = MagicMock()
        mock_agent1.name = "agent1"
        mock_agent1.is_available.return_value = True
        mock_agent1.config_path = MagicMock(spec=Path)
        mock_agent1.config_path.exists.return_value = True
        mock_agent1.config_path.__str__.return_value = "/path/to/config1"

        mock_agent2 = MagicMock()
        mock_agent2.name = "agent2"
        mock_agent2.is_available.return_value = False

        mock_global = MagicMock()
        mock_global.name = "global-skills"

        mock_get_agents.return_value = [mock_agent1, mock_agent2, mock_global]

        wizard = SetupWizard()
        wizard._step_detect_agents()

        # Check if console output contains expected info (via mock_print calls)
        # Instead of checking all prints, we can verify get_all_agents was called
        mock_get_agents.assert_called()
        mock_agent1.is_available.assert_called()
        mock_agent2.is_available.assert_called()
        # global-skills should be skipped in the loop
        mock_global.is_available.assert_not_called()

    @patch("agent_sync.setup.get_all_agents")
    @patch("agent_sync.setup.Prompt.ask")
    @patch("agent_sync.setup.console.print")
    @patch("agent_sync.setup.Config")
    def test_step_select_agents_all(self, mock_config, mock_print, mock_ask, mock_get_agents):
        """Test _step_select_agents with 'all' option."""
        # Setup mocks
        mock_agent1 = MagicMock()
        mock_agent1.name = "agent1"
        mock_agent1.is_available.return_value = True

        mock_agent2 = MagicMock()
        mock_agent2.name = "agent2"
        mock_agent2.is_available.return_value = False

        mock_global = MagicMock()
        mock_global.name = "global-skills"

        mock_get_agents.return_value = [mock_agent1, mock_agent2, mock_global]
        mock_ask.return_value = "all"

        wizard = SetupWizard()
        wizard._step_select_agents()

        assert "agent1" in wizard.selected_agents
        assert "agent2" not in wizard.selected_agents
        assert "global-skills" not in wizard.selected_agents

    @patch("agent_sync.setup.SkillsManager")
    @patch("agent_sync.setup.Confirm.ask")
    @patch("agent_sync.setup.console.print")
    @patch("agent_sync.setup.Config")
    def test_step_centralize_skills(self, mock_config, mock_print, mock_confirm, mock_skills_mgr_class):
        """Test _step_centralize_skills."""
        mock_skills_mgr = mock_skills_mgr_class.return_value
        mock_skills_mgr.scan_all_agents.return_value = {
            "agent1": [Path("skill1"), Path("skill2")]
        }
        mock_confirm.return_value = True

        wizard = SetupWizard()
        wizard._step_centralize_skills()

        assert wizard.skills_centralized is True
        mock_skills_mgr.centralize.assert_called_once()
        assert "global-skills" in wizard.selected_agents
        assert wizard.agent_configs["global-skills"]["enabled"] is True

    @patch("agent_sync.setup.validate_repo_name")
    @patch("agent_sync.setup.Prompt.ask")
    @patch("agent_sync.setup.console.print")
    @patch("agent_sync.setup.Config")
    def test_step_repo_settings(self, mock_config, mock_print, mock_ask, mock_validate):
        """Test _step_repo_settings."""
        mock_ask.side_effect = ["invalid!", "valid-repo"]
        mock_validate.side_effect = [False, True]

        wizard = SetupWizard()
        wizard._step_repo_settings()

        assert wizard.repo_name == "valid-repo"
        assert wizard.is_private is True
        assert mock_validate.call_count == 2
