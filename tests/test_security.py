import pytest
import shutil
from pathlib import Path
from unittest.mock import MagicMock, patch
from agent_sync.skills_delete import SkillsDeleter
from agent_sync.validators import validate_skill_name

def test_validate_skill_name():
    """Test skill name validation rules."""
    assert validate_skill_name("valid-skill") is True
    assert validate_skill_name("valid.skill_123") is True
    assert validate_skill_name("skill") is True

    assert validate_skill_name("../traversal") is False
    assert validate_skill_name("/absolute/path") is False
    assert validate_skill_name("path/with/slash") is False
    assert validate_skill_name("-start-with-hyphen") is False
    assert validate_skill_name(".start-with-period") is False
    assert validate_skill_name("") is False
    assert validate_skill_name("a" * 65) is False
    assert validate_skill_name("skill\nnewline") is False

@patch('agent_sync.skills_delete.shutil.rmtree')
@patch('agent_sync.skills_delete.Path.home')
def test_delete_skills_path_traversal_protection(mock_home, mock_rmtree):
    """Test that path traversal attempts are blocked in delete_skills."""
    fake_home = Path('/tmp/fake_home')
    mock_home.return_value = fake_home

    deleter = SkillsDeleter()
    # Mock global_skills_dir
    deleter.global_skills_dir = (fake_home / ".agents" / "skills").resolve()

    # Attempt traversal
    malicious_skills = ["../traversal", "valid-skill/../../etc/passwd", "etc/passwd"]

    # We mock exists() to return True so it tries to delete
    with patch.object(Path, 'exists', return_value=True):
        stats = deleter.delete_skills(malicious_skills)

    # Check that no rmtree calls happened for these malicious paths
    assert mock_rmtree.call_count == 0
    assert stats["errors"] == len(malicious_skills)

@patch('agent_sync.skills_delete.shutil.rmtree')
@patch('agent_sync.skills_delete.Path.home')
def test_delete_skills_resolved_traversal(mock_home, mock_rmtree):
    """Test defense-in-depth: resolved path must be under skills hub."""
    fake_home = Path('/tmp/fake_home')
    mock_home.return_value = fake_home

    deleter = SkillsDeleter()
    deleter.global_skills_dir = (fake_home / ".agents" / "skills").resolve()

    # Suppose validate_skill_name was bypassed somehow but resolve() still catches it
    # We mock resolve to return something outside the hub

    # We need to mock resolve specifically on the Path instances being created
    # Inside delete_skills: hub_skill_path = (self.global_skills_dir / skill_name).resolve()

    with patch('agent_sync.skills_delete.Path.resolve') as mock_resolve:
        # First call is global_skills_dir.resolve()
        # Second call is hub_skill_path.resolve()
        mock_resolve.side_effect = [deleter.global_skills_dir, Path('/etc/passwd')]

        # We need to make sure validate_skill_name passes for this test case
        with patch('agent_sync.validators.validate_skill_name', return_value=True):
            stats = deleter.delete_skills(["some-skill"])

    assert mock_rmtree.call_count == 0
    assert stats["errors"] == 1
