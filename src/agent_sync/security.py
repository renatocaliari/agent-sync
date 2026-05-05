import os
from pathlib import Path
from typing import Optional

def ensure_secure_dir(path: Path) -> None:
    """Ensure directory has 0o700 permissions."""
    path.mkdir(parents=True, exist_ok=True)
    os.chmod(path, 0o700)

def secure_open(path: Path, mode: str = "w", encoding: Optional[str] = None):
    """Open file with 0o600 permissions."""
    def opener(file_path, flags):
        return os.open(file_path, flags | os.O_CREAT, 0o600)

    use_opener = any(m in mode for m in "wax")
    f = open(path, mode, opener=opener if use_opener else None, encoding=encoding)
    if use_opener:
        try:
            os.fchmod(f.fileno(), 0o600)
        except (AttributeError, OSError):
            try:
                os.chmod(path, 0o600)
            except OSError:
                pass
    return f
