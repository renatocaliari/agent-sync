import os
import shutil
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock
import pytest

from agent_sync.publish.git_publish import do_git_publish

def test_symlink_content_leakage_in_publish(tmp_path):
    """
    Verify that publishing follows symlinks and leaks content of files
    outside the intended directory.
    """
    # 1. Setup: Create a secret file outside the source directory
    secret_dir = tmp_path / "secrets"
    secret_dir.mkdir()
    secret_file = secret_dir / "confidential.txt"
    secret_file.write_text("THIS IS SENSITIVE CONTENT")

    # 2. Setup: Create a source directory (simulating a skill)
    skill_dir = tmp_path / "my_skill"
    skill_dir.mkdir()
    (skill_dir / "SKILL.md").write_text("# My Skill")

    # 3. Setup: Create a symlink inside the skill directory pointing to the secret file
    leaking_symlink = skill_dir / "leak.txt"
    leaking_symlink.symlink_to(secret_file)

    # 4. Prepare for publishing
    published_repo = "https://github.com/user/published-skills.git"
    items = [(skill_dir, "my_skill")]

    # We want to inspect the temporary directory before it's deleted or before git push
    # So we patch git_commit_and_push to capture the temp directory path
    captured_tmp_dir = []

    def mock_commit_and_push(tmp_dir, repo, count):
        captured_tmp_dir.append(Path(tmp_dir))
        # Do nothing else

    with patch("agent_sync.publish.git_publish.git_commit_and_push", side_effect=mock_commit_and_push):
        with patch("agent_sync.publish.git_publish.console.print"):
            # We don't want it to actually try to rmtree the captured_tmp_dir while we're using it
            # but do_git_publish has a finally block.
            # We can patch shutil.rmtree to be a no-op for our captured dir
            original_rmtree = shutil.rmtree
            def mock_rmtree(path, **kwargs):
                if Path(path) in captured_tmp_dir:
                    return
                original_rmtree(path, **kwargs)

            with patch("shutil.rmtree", side_effect=mock_rmtree):
                success = do_git_publish(
                    items=items,
                    subdir="skills",
                    readme_generator=lambda *args: None,
                    count=1,
                    item_name="skills",
                    repo=published_repo
                )

                assert success is True

    assert len(captured_tmp_dir) == 1
    tmp_repo_dir = captured_tmp_dir[0]

    published_skill_dir = tmp_repo_dir / "skills" / "my_skill"
    published_leaked_file = published_skill_dir / "leak.txt"

    assert published_leaked_file.exists()

    # Check if it's a symlink or a real file
    is_symlink = published_leaked_file.is_symlink()

    # If it leaked, it's NOT a symlink (shutil followed it and copied content)
    # or it IS a symlink but pointing to a non-existent path (if it preserved relative path blindly)
    # but shutil.copytree(symlinks=False) makes it a real file.

    try:
        if not is_symlink:
            content = published_leaked_file.read_text()
            if content == "THIS IS SENSITIVE CONTENT":
                pytest.fail("SECURITY VULNERABILITY: Symlink content was leaked into the published repository!")
        else:
            # If it is a symlink, check where it points.
            # If it still points to the absolute path of the secret file, it might still be a leak
            # if the git repo is then checked out on the same machine, but usually symlinks in git
            # are just text files with the path.
            pass
    finally:
        # Cleanup
        if tmp_repo_dir.exists():
            original_rmtree(tmp_repo_dir)
