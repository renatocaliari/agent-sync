"""Tests for agent-sync agent integrations based on YAML registry."""

import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

from agent_sync.agents import (
    get_all_agents,
    get_agent,
    BaseAgent,
)


class TestAgentIntegrations:
    """Test agent integrations."""
    
    def test_get_all_agents(self):
        """Test getting all agent integrations."""
        agents = get_all_agents()
        
        # Now we have 6 agents (opencode, claude-code, gemini-cli, pi.dev, qwen-code, global-skills)
        assert len(agents) == 6
        agent_names = [a.name for a in agents]
        
        assert "opencode" in agent_names
        assert "claude-code" in agent_names
        assert "gemini-cli" in agent_names
        assert "pi.dev" in agent_names
        assert "qwen-code" in agent_names
        assert "global-skills" in agent_names
    
    def test_get_agent_by_name(self):
        """Test getting specific agent by name."""
        agent = get_agent("opencode")
        assert agent is not None
        assert agent.name == "opencode"
        
        agent = get_agent("claude-code")
        assert agent is not None
        assert agent.name == "claude-code"
        
        # Non-existent agent
        agent = get_agent("nonexistent")
        assert agent is None
    
    def test_opencode_agent(self, tmp_path):
        """Test Opencode agent integration."""
        agent = get_agent("opencode")
        agent.config_dir = tmp_path
        
        assert agent.name == "opencode"
        assert "opencode" in str(agent.config_path)
        assert "skills" in str(agent.skills_path)
    
    def test_claude_code_agent(self, tmp_path):
        """Test Claude Code agent integration."""
        agent = get_agent("claude-code")
        agent.config_dir = tmp_path
        
        assert agent.name == "claude-code"
        assert "settings.json" in str(agent.config_path)
        assert "commands" in str(agent.skills_path)
    
    def test_gemini_cli_agent(self, tmp_path):
        """Test Gemini CLI agent integration."""
        agent = get_agent("gemini-cli")
        agent.config_dir = tmp_path
        
        assert agent.name == "gemini-cli"
        assert "settings.json" in str(agent.config_path)
        assert "tools" in str(agent.skills_path)
    
    def test_pi_dev_agent(self, tmp_path):
        """Test Pi.dev agent integration."""
        agent = get_agent("pi.dev")
        agent.config_dir = tmp_path
        
        assert agent.name == "pi.dev"
        assert "settings.json" in str(agent.config_path)
        assert "skills" in str(agent.skills_path)
    
    def test_qwen_code_agent(self, tmp_path):
        """Test Qwen Code agent integration."""
        agent = get_agent("qwen-code")
        agent.config_dir = tmp_path
        
        assert agent.name == "qwen-code"
        assert "settings.json" in str(agent.config_path)
        assert "skills" in str(agent.skills_path)
    
    def test_agent_config_path_structure(self, tmp_path):
        """Test agent config path structure."""
        agent = BaseAgent("test-agent", {
            "method": "copy",
            "config_dir": str(tmp_path),
            "config_filename": "config.json",
            "skills_dir_name": "skills",
            "check": {"binary": "test"}
        })
        
        expected_config = tmp_path / "config.json"
        expected_skills = tmp_path / "skills"
        
        assert agent.config_path == expected_config
        assert agent.skills_path == expected_skills
    
    def test_agent_repr(self):
        """Test agent string representation."""
        agent = get_agent("opencode")
        repr_str = repr(agent)
        
        assert "BaseAgent" in repr_str
        assert "opencode" in repr_str
