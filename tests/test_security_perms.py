import os
import stat
from pathlib import Path
from agent_sync.security import secure_open, ensure_secure_dir

def test_ensure_secure_dir(tmp_path):
    secure_dir = tmp_path / "secure_dir"
    ensure_secure_dir(secure_dir)
    assert secure_dir.exists()
    mode = os.stat(secure_dir).st_mode
    assert stat.S_IMODE(mode) == 0o700

def test_secure_open_new_file(tmp_path):
    secure_file = tmp_path / "secure_file.txt"
    with secure_open(secure_file, "w") as f:
        f.write("sensitive data")
    assert secure_file.exists()
    mode = os.stat(secure_file).st_mode
    assert stat.S_IMODE(mode) == 0o600

def test_secure_open_existing_file(tmp_path):
    loose_file = tmp_path / "loose_file.txt"
    loose_file.write_text("initial")
    os.chmod(loose_file, 0o666)
    with secure_open(loose_file, "w") as f:
        f.write("new sensitive data")
    mode = os.stat(loose_file).st_mode
    assert stat.S_IMODE(mode) == 0o600
