import shutil
import tempfile
from pathlib import Path
import pytest

def test_shutil_copytree_leaks_content():
    """
    Demonstrate that by default, shutil.copytree follows symlinks and leaks content
    of files outside the source directory.
    """
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)

        # Create a "sensitive" file outside the directory to be copied
        sensitive_file = tmp_path / "sensitive.txt"
        sensitive_file.write_text("TOP SECRET DATA")

        # Create the source directory
        src_dir = tmp_path / "src"
        src_dir.mkdir()

        # Create a symlink inside src pointing to the sensitive file
        leak_link = src_dir / "leak.txt"
        leak_link.symlink_to(sensitive_file)

        # Destination directory
        dest_dir = tmp_path / "dest"

        # Perform the copy using hardened settings
        shutil.copytree(src_dir, dest_dir, symlinks=True)

        copied_file = dest_dir / "leak.txt"

        # If it is a symlink, it means it preserved it and didn't copy the content
        assert copied_file.is_symlink()
        assert copied_file.readlink() == sensitive_file

def test_shutil_copy2_leaks_content():
    """
    Demonstrate that by default, shutil.copy2 follows symlinks.
    """
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)

        sensitive_file = tmp_path / "sensitive.txt"
        sensitive_file.write_text("TOP SECRET DATA")

        src_dir = tmp_path / "src"
        src_dir.mkdir()

        leak_link = src_dir / "leak.txt"
        leak_link.symlink_to(sensitive_file)

        dest_file = tmp_path / "dest.txt"

        # Perform copy2 using hardened settings
        shutil.copy2(leak_link, dest_file, follow_symlinks=False)

        assert dest_file.is_symlink()
        assert dest_file.readlink() == sensitive_file
