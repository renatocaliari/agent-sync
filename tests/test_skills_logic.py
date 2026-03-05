"""Integration tests for skills management logic."""

import json
from pathlib import Path
from unittest.mock import patch, MagicMock
from agent_sync.skills import SkillsManager
from agent_sync.agents import BaseAgent


def test_centralize_moves_files_correctly(tmp_path):
    """Test that centralize moves skills from agent dirs to global dir."""
    # Setup mock home structure
    home = tmp_path / "home"
    global_dir = home / ".agents" / "skills"
    
    # Use 'native' method so it doesn't try to copy back
    agent_home = home / ".native-agent"
    agent_skills = agent_home / "skills"
    agent_skills.mkdir(parents=True)
    
    # Create a mock skill
    skill_name = "test-skill"
    skill_path = agent_skills / skill_name
    skill_path.mkdir()
    (skill_path / "SKILL.md").write_text("test content")
    
    # Create mock agent with NATIVE method
    agent = BaseAgent("native-agent", {
        "method": "native",
        "config_dir": str(agent_home),
        "config_filename": "settings.json",
        "skills_dir_name": "skills",
        "check": {"always": True}
    })
    
    # Initialize manager
    manager = SkillsManager(global_skills_dir=global_dir)
    
    # Mock get_all_agents
    with patch("agent_sync.skills.get_all_agents", return_value=[agent]):
        stats = manager.centralize(move=True)
    
    # Verify
    assert stats["moved"] >= 1
    assert (global_dir / skill_name / "SKILL.md").exists()
    # For native agents, we clean up the local directory after moving
    assert not skill_path.exists()


def test_apply_config_method_updates_json(tmp_path):
    """Test that config method updates the agent's JSON file correctly."""
    config_dir = tmp_path / "opencode"
    config_dir.mkdir()
    config_file = config_dir / "opencode.json"
    
    # Initial empty config
    config_file.write_text(json.dumps({"skills": {"paths": []}}))
    
    # Mock agent
    agent = BaseAgent("opencode", {
        "method": "config",
        "config_dir": str(config_dir),
        "config_filename": "opencode.json",
        "skills_dir_name": "skills",
        "check": {"always": True},
        "config_update": {"path": "skills.paths", "action": "append"}
    })
    
    global_dir = tmp_path / "global_skills"
    global_dir.mkdir()
    
    manager = SkillsManager(global_skills_dir=global_dir)
    manager._apply_config_method(agent)
    
    # Verify JSON content
    updated_config = json.loads(config_file.read_text())
    assert str(global_dir) in updated_config["skills"]["paths"]


def test_cleanup_user_symlinks(tmp_path):
    """Test that old user-created symlinks are removed."""
    agent_home = tmp_path / "agent"
    agent_skills_dir = agent_home / "skills"
    agent_skills_dir.mkdir(parents=True)
    
    # Create a real symlink
    target = tmp_path / "target"
    target.mkdir()
    link = agent_skills_dir / "my-link"
    link.symlink_to(target)
    
    assert link.is_symlink()
    
    # Mock agent
    agent = BaseAgent("test", {
        "method": "copy",
        "config_dir": str(agent_home),
        "skills_dir_name": "skills",
        "check": {"always": True}
    })
    
    manager = SkillsManager(global_skills_dir=tmp_path / "global")
    
    with patch("agent_sync.skills.get_all_agents", return_value=[agent]):
        count = manager._cleanup_user_symlinks()
    
    assert count >= 1
    assert not link.exists()
