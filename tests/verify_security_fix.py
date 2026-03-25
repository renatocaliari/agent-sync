import os
import sys
import shutil
from pathlib import Path

# Add src to sys.path to import local modules
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from agent_sync.skills_delete import SkillsDeleter

def test_path_traversal():
    deleter = SkillsDeleter()

    # Mock global skills dir
    test_hub = Path("/tmp/agent_sync_test_hub")
    if test_hub.exists():
        shutil.rmtree(test_hub)
    test_hub.mkdir(parents=True)

    # Create a dummy skill
    skill_dir = test_hub / "valid-skill"
    skill_dir.mkdir()
    (skill_dir / "SKILL.md").write_text("dummy")

    # Create a file outside the hub
    secret_file = Path("/tmp/agent_sync_secret.txt")
    secret_file.write_text("sensitive data")

    deleter.global_skills_dir = test_hub

    print("Testing path traversal blocking...")

    # Attempt traversal with ".."
    stats = deleter.delete_skills(["../agent_sync_secret.txt"])

    if secret_file.exists():
        print("✅ Path traversal '../' blocked successfully.")
    else:
        print("❌ Path traversal '../' FAILED! File deleted.")

    # Attempt traversal with absolute path (if possible via skill_name)
    stats = deleter.delete_skills(["/tmp/agent_sync_secret.txt"])

    if secret_file.exists():
        print("✅ Absolute path traversal blocked successfully.")
    else:
        print("❌ Absolute path traversal FAILED! File deleted.")

    # Verify valid skill can still be deleted
    stats = deleter.delete_skills(["valid-skill"])
    if not skill_dir.exists():
        print("✅ Valid skill deleted successfully.")
    else:
        print("❌ Valid skill deletion FAILED!")

    # Cleanup
    if test_hub.exists():
        shutil.rmtree(test_hub)
    if secret_file.exists():
        secret_file.unlink()

if __name__ == "__main__":
    test_path_traversal()
