"""Tests for agent-sync agent integrations."""

import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

from agent_sync.agents import (
    get_all_agents,
    get_agent,
    BaseAgent,
    OpencodeAgent,
    ClaudeCodeAgent,
    GeminiCliAgent,
    PiDevAgent,
    QwenCodeAgent,
)


class TestAgentIntegrations:
    """Test agent integrations."""
    
    def test_get_all_agents(self):
        """Test getting all agent integrations."""
        agents = get_all_agents()
        
        assert len(agents) == 5
        agent_names = [a.name for a in agents]
        
        assert "opencode" in agent_names
        assert "claude-code" in agent_names
        assert "gemini-cli" in agent_names
        assert "pi.dev" in agent_names
        assert "qwen-code" in agent_names
    
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
        with patch.object(OpencodeAgent, 'config_dir', tmp_path):
            agent = OpencodeAgent()
            
            assert agent.name == "opencode"
            assert "opencode" in str(agent.config_path)
            assert "tool" in str(agent.skills_path)
    
    def test_claude_code_agent(self, tmp_path):
        """Test Claude Code agent integration."""
        with patch.object(ClaudeCodeAgent, 'config_dir', tmp_path):
            agent = ClaudeCodeAgent()
            
            assert agent.name == "claude-code"
            assert "claude-code" in str(agent.config_path)
            assert "commands" in str(agent.skills_path)
    
    def test_gemini_cli_agent(self, tmp_path):
        """Test Gemini CLI agent integration."""
        with patch.object(GeminiCliAgent, 'config_dir', tmp_path):
            agent = GeminiCliAgent()
            
            assert agent.name == "gemini-cli"
            assert "gemini-cli" in str(agent.config_path)
            assert "tools" in str(agent.skills_path)
    
    def test_pi_dev_agent(self, tmp_path):
        """Test Pi.dev agent integration."""
        with patch.object(PiDevAgent, 'config_dir', tmp_path):
            agent = PiDevAgent()
            
            assert agent.name == "pi.dev"
            assert "pi.dev" in str(agent.config_path)
            assert "skills" in str(agent.skills_path)
    
    def test_qwen_code_agent(self, tmp_path):
        """Test Qwen Code agent integration."""
        with patch.object(QwenCodeAgent, 'config_dir', tmp_path):
            agent = QwenCodeAgent()
            
            assert agent.name == "qwen-code"
            assert "qwen-code" in str(agent.config_path)
            assert "skills" in str(agent.skills_path)
    
    def test_agent_config_path_structure(self, tmp_path):
        """Test agent config path structure."""
        with patch.object(BaseAgent, 'config_dir', tmp_path):
            agent = BaseAgent()
            agent.name = "test-agent"
            agent.config_filename = "config.json"
            agent.skills_dir_name = "skills"
            
            expected_config = tmp_path / "test-agent" / "config.json"
            expected_skills = tmp_path / "test-agent" / "skills"
            
            assert agent.config_path == expected_config
            assert agent.skills_path == expected_skills
    
    def test_agent_is_available_abstract(self):
        """Test that BaseAgent.is_available is abstract."""
        with pytest.raises(TypeError):
            BaseAgent()
    
    def test_agent_repr(self, tmp_path):
        """Test agent string representation."""
        with patch.object(OpencodeAgent, 'config_dir', tmp_path):
            agent = OpencodeAgent()
            repr_str = repr(agent)
            
            assert "OpencodeAgent" in repr_str
            assert "opencode" in repr_str
