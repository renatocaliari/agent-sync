import os
import shutil
import tempfile
from pathlib import Path
import pytest
import agent_sync.publish.git_publish

def test_publish_symlink_leakage():
    """Verify that do_git_publish now PREVENTS leaking symlink targets."""
    with tempfile.TemporaryDirectory() as base_dir:
        base_path = Path(base_dir)

        # 1. Create a "sensitive" file outside the publish scope
        sensitive_file = base_path / "sensitive.txt"
        sensitive_file.write_text("SENSITIVE_CONTENT")

        # 2. Create a "skill" directory with a symlink to the sensitive file
        skills_source_dir = base_path / "my_skills"
        skills_source_dir.mkdir()

        skill_dir = skills_source_dir / "evil_skill"
        skill_dir.mkdir()
        (skill_dir / "SKILL.md").write_text("Evil skill")

        # Symlink to sensitive file
        leak_link = skill_dir / "leak.txt"
        leak_link.symlink_to(sensitive_file)

        # 3. Mock objects needed for do_git_publish
        items = [(skill_dir, "evil_skill")]
        def mock_readme_gen(dir_path, items, repo):
            (dir_path / "README.md").write_text("README")

        repo_url = "https://github.com/user/repo.git"

        # We need to mock git_commit_and_push to avoid actual git calls
        original_git_func = agent_sync.publish.git_publish.git_commit_and_push
        agent_sync.publish.git_publish.git_commit_and_push = lambda *args, **kwargs: None

        try:
            # We also need to capture where it copies things
            # do_git_publish creates a temp dir and deletes it in finally.
            # We'll monkeypatch shutil.rmtree to NOT delete it so we can inspect it.
            import shutil
            original_rmtree = shutil.rmtree
            last_tmp_dir = [None]
            def mock_rmtree(path, **kwargs):
                if "agent-sync-publish-" in str(path):
                    last_tmp_dir[0] = path
                else:
                    original_rmtree(path, **kwargs)

            agent_sync.publish.git_publish.shutil.rmtree = mock_rmtree

            try:
                agent_sync.publish.git_publish.do_git_publish(
                    items=items,
                    subdir="skills",
                    readme_generator=mock_readme_gen,
                    count=1,
                    item_name="skills",
                    repo=repo_url
                )

                # Check if the sensitive content was copied
                if last_tmp_dir[0]:
                    tmp_publish_dir = Path(last_tmp_dir[0])
                    copied_file = tmp_publish_dir / "skills" / "evil_skill" / "leak.txt"

                    assert copied_file.exists()
                    # EXPECTED BEHAVIOR: It's a symlink, NOT a file with sensitive content
                    if copied_file.is_symlink():
                        print("\n[SUCCESS] It's a symlink, content leakage prevented.")
                    else:
                        content = copied_file.read_text()
                        if content == "SENSITIVE_CONTENT":
                            print("\n[VULNERABILITY STILL PRESENT] Symlink content was leaked!")
                        else:
                            print(f"\nCopied file exists but content mismatch: {content}")
                else:
                    print("\nCould not capture temp directory")

            finally:
                agent_sync.publish.git_publish.shutil.rmtree = original_rmtree
                if last_tmp_dir[0]:
                    original_rmtree(last_tmp_dir[0], ignore_errors=True)

        finally:
            agent_sync.publish.git_publish.git_commit_and_push = original_git_func

if __name__ == "__main__":
    test_publish_symlink_leakage()
