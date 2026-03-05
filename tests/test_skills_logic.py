"""Integration tests for all skills configuration methods (native, config, copy)."""

import json
import shutil
from pathlib import Path
from unittest.mock import patch
from agent_sync.skills import SkillsManager
from agent_sync.agents import BaseAgent


def setup_mock_environment(tmp_path):
    """Helper to setup a clean mock environment for each test."""
    home = tmp_path / "home"
    global_dir = home / ".agents" / "skills"
    global_dir.mkdir(parents=True)
    
    # Create a global skill
    (global_dir / "global-skill").mkdir()
    (global_dir / "global-skill" / "SKILL.md").write_text("global content")
    
    return home, global_dir


def test_method_native_does_no_copy(tmp_path):
    """Test that 'native' method just confirms the path without copying."""
    home, global_dir = setup_mock_environment(tmp_path)
    agent_home = home / ".native-agent"
    agent_home.mkdir(parents=True)
    
    agent = BaseAgent("native-agent", {
        "method": "native",
        "config_dir": str(agent_home),
        "skills_dir_name": "skills",
        "check": {"always": True}
    })
    
    manager = SkillsManager(global_skills_dir=global_dir)
    
    with patch("agent_sync.skills.get_all_agents", return_value=[agent]):
        result = manager._configure_agent(agent)
    
    assert result["method"] == "native"
    assert not (agent_home / "skills").exists()  # No copy should happen


def test_method_config_updates_json(tmp_path):
    """Test that 'config' method updates the agent JSON configuration."""
    home, global_dir = setup_mock_environment(tmp_path)
    agent_home = home / ".config-agent"
    agent_home.mkdir(parents=True)
    config_file = agent_home / "config.json"
    config_file.write_text(json.dumps({"settings": {"paths": []}}))
    
    agent = BaseAgent("config-agent", {
        "method": "config",
        "config_dir": str(agent_home),
        "config_filename": "config.json",
        "skills_dir_name": "skills",
        "check": {"always": True},
        "config_update": {"path": "settings.paths", "action": "append"}
    })
    
    manager = SkillsManager(global_skills_dir=global_dir)
    
    with patch("agent_sync.skills.get_all_agents", return_value=[agent]):
        result = manager._configure_agent(agent)
    
    assert result["method"] == "config"
    
    # Verify JSON update
    updated_config = json.loads(config_file.read_text())
    assert str(global_dir) in updated_config["settings"]["paths"]


def test_method_copy_performs_physical_copy(tmp_path):
    """Test that 'copy' method physically copies skills to the agent directory."""
    home, global_dir = setup_mock_environment(tmp_path)
    agent_home = home / ".copy-agent"
    agent_home.mkdir(parents=True)
    
    agent = BaseAgent("copy-agent", {
        "method": "copy",
        "config_dir": str(agent_home),
        "skills_dir_name": "plugins", # different name to test flexibility
        "check": {"always": True}
    })
    
    manager = SkillsManager(global_skills_dir=global_dir)
    
    with patch("agent_sync.skills.get_all_agents", return_value=[agent]):
        result = manager._configure_agent(agent)
    
    assert result["method"] == "copy"
    assert (agent_home / "plugins" / "global-skill" / "SKILL.md").exists()
    assert (agent_home / "plugins" / "global-skill" / "SKILL.md").read_text() == "global content"


def test_centralize_with_conflicts(tmp_path):
    """Test centralization when multiple agents have the same skill."""
    home, global_dir = setup_mock_environment(tmp_path)
    
    # Setup Agent A with skill X
    agent_a_home = home / ".agent-a"
    (agent_a_home / "skills" / "shared-skill").mkdir(parents=True)
    (agent_a_home / "skills" / "shared-skill" / "SKILL.md").write_text("content A")
    
    # Setup Agent B with same skill X
    agent_b_home = home / ".agent-b"
    (agent_b_home / "skills" / "shared-skill").mkdir(parents=True)
    (agent_b_home / "skills" / "shared-skill" / "SKILL.md").write_text("content B")
    
    agent_a = BaseAgent("agent-a", {"method": "copy", "config_dir": str(agent_a_home), "skills_dir_name": "skills", "check": {"always": True}})
    agent_b = BaseAgent("agent-b", {"method": "copy", "config_dir": str(agent_b_home), "skills_dir_name": "skills", "check": {"always": True}})
    
    manager = SkillsManager(global_skills_dir=global_dir)
    
    with patch("agent_sync.skills.get_all_agents", return_value=[agent_a, agent_b]):
        # Mocking console input might be tricky, but centralize should detect conflicts
        # and resolve them using the first one found if not interactive
        stats = manager.centralize(move=True)
    
    assert stats["conflicts_resolved"] >= 1
    assert (global_dir / "shared-skill" / "SKILL.md").exists()
