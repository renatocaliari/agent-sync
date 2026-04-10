from unittest.mock import patch

import pytest

from agent_sync.skills_diff import SkillsDiff


@pytest.fixture
def skills_diff_setup(tmp_path):
    with (
        patch("agent_sync.config.Config") as mock_config,
        patch("agent_sync.sync.SyncManager") as mock_sync_manager,
    ):
        mock_config_instance = mock_config.return_value
        mock_config_instance.repo_url = "https://github.com/user/repo"

        mock_sync_manager_instance = mock_sync_manager.return_value
        mock_sync_manager_instance.repo_dir = tmp_path / "repo"

        sd = SkillsDiff()
        # Override global_skills_dir to use tmp_path for local tests
        sd.global_skills_dir = tmp_path / "global_skills"

        yield sd, mock_config_instance, mock_sync_manager_instance


def test_get_remote_skills_repo_dir_none(skills_diff_setup):
    sd, _, mock_sync_manager_instance = skills_diff_setup
    mock_sync_manager_instance.repo_dir = None

    # Need to re-init or manually set because __init__ sets it
    sd.repo_dir = None
    assert sd.get_remote_skills() == set()


def test_get_remote_skills_repo_dir_not_exists(skills_diff_setup):
    sd, _, _ = skills_diff_setup
    # sd.repo_dir is tmp_path / "repo" which doesn't exist yet
    assert sd.get_remote_skills() == set()


def test_get_remote_skills_no_skills_subdir(skills_diff_setup):
    sd, _, _ = skills_diff_setup
    sd.repo_dir.mkdir()
    assert sd.get_remote_skills() == set()


def test_get_remote_skills_happy_path(skills_diff_setup):
    sd, _, _ = skills_diff_setup
    remote_skills_dir = sd.repo_dir / "skills"
    remote_skills_dir.mkdir(parents=True)

    # Valid skill
    skill1 = remote_skills_dir / "skill1"
    skill1.mkdir()
    (skill1 / "SKILL.md").write_text("content")

    # Invalid skill (no SKILL.md)
    skill2 = remote_skills_dir / "skill2"
    skill2.mkdir()

    # Hidden dir
    hidden = remote_skills_dir / ".hidden"
    hidden.mkdir()
    (hidden / "SKILL.md").write_text("content")

    remote_skills = sd.get_remote_skills()
    assert remote_skills == {"skill1"}


def test_get_local_skills_not_exists(skills_diff_setup):
    sd, _, _ = skills_diff_setup
    # sd.global_skills_dir doesn't exist
    assert sd.get_local_skills() == set()


def test_get_local_skills_happy_path(skills_diff_setup):
    sd, _, _ = skills_diff_setup
    sd.global_skills_dir.mkdir(parents=True)

    # Valid local skill
    skill_a = sd.global_skills_dir / "skill-a"
    skill_a.mkdir()
    (skill_a / "SKILL.md").write_text("local content")

    # Invalid local skill
    skill_b = sd.global_skills_dir / "not-a-skill"
    skill_b.mkdir()

    local_skills = sd.get_local_skills()
    assert local_skills == {"skill-a"}


def test_diff_logic(skills_diff_setup):
    sd, _, _ = skills_diff_setup

    # Setup local
    sd.global_skills_dir.mkdir(parents=True)
    (sd.global_skills_dir / "local-only").mkdir()
    (sd.global_skills_dir / "local-only" / "SKILL.md").write_text("content")
    (sd.global_skills_dir / "both").mkdir()
    (sd.global_skills_dir / "both" / "SKILL.md").write_text("content")

    # Setup remote
    remote_skills_dir = sd.repo_dir / "skills"
    remote_skills_dir.mkdir(parents=True)
    (remote_skills_dir / "remote-only").mkdir()
    (remote_skills_dir / "remote-only" / "SKILL.md").write_text("content")
    (remote_skills_dir / "both").mkdir()
    (remote_skills_dir / "both" / "SKILL.md").write_text("content")

    result = sd.diff()

    assert result["local_only"] == ["local-only"]
    assert result["remote_only"] == ["remote-only"]
    assert result["both"] == ["both"]
