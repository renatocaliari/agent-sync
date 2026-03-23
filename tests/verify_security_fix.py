from pathlib import Path
import os
import shutil
import sys

# Setup environment
src_path = Path.cwd() / "src"
sys.path.insert(0, str(src_path))

from agent_sync.skills_delete import SkillsDeleter

def test_path_traversal():
    # Setup dummy directory to "attack"
    dummy_dir = Path("/tmp/dummy_attack_dir")
    dummy_dir.mkdir(parents=True, exist_ok=True)
    secret_file = dummy_dir / "secret.txt"
    secret_file.write_text("sensitve data")

    # Initialize SkillsDeleter
    deleter = SkillsDeleter()

    # Ensure global skills dir exists for the test
    deleter.global_skills_dir.mkdir(parents=True, exist_ok=True)

    # Attempt path traversal
    attack_name = "../../../../../../../../../../../../../../../../../../../../../../../tmp/dummy_attack_dir"

    print(f"Attempting to delete: {attack_name}")
    stats = deleter.delete_skills([attack_name], dry_run=False)

    # Check if dummy_dir still exists
    if dummy_dir.exists():
        print("SUCCESS: Path traversal blocked!")
    else:
        print("FAILURE: Path traversal successful! Directory deleted.")
        sys.exit(1)

    if stats["errors"] > 0:
        print(f"Stats correctly recorded {stats['errors']} error(s).")
    else:
        print("FAILURE: Stats did not record any errors.")
        sys.exit(1)

    # Cleanup
    if dummy_dir.exists():
        shutil.rmtree(dummy_dir)

if __name__ == "__main__":
    test_path_traversal()
