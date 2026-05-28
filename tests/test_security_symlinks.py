import shutil
from pathlib import Path
import pytest

def test_shutil_symlink_leakage_repro(tmp_path):
    """
    Reproduction test for symlink content leakage.
    By default, shutil.copytree and copy2 follow symlinks.
    """
    source = tmp_path / "source"
    source.mkdir()

    external_file = tmp_path / "external.txt"
    external_file.write_text("SECRET_CONTENT")

    # Create a symlink inside source pointing outside
    symlink_path = source / "leaked_link"
    symlink_path.symlink_to(external_file)

    dest = tmp_path / "dest"

    # DEFAULT BEHAVIOR (Dangerous): follows symlinks
    shutil.copytree(source, dest)

    leaked_file = dest / "leaked_link"
    assert not leaked_file.is_symlink(), "Expected default shutil to follow symlinks (leaking content)"
    assert leaked_file.read_text() == "SECRET_CONTENT", "Content leaked!"

def test_shutil_symlink_preserved_fix(tmp_path):
    """
    Verify that using symlinks=True/follow_symlinks=False prevents leakage.
    """
    source = tmp_path / "source"
    source.mkdir()

    external_file = tmp_path / "external.txt"
    external_file.write_text("SECRET_CONTENT")

    # Create a symlink inside source pointing outside
    symlink_path = source / "leaked_link"
    symlink_path.symlink_to(external_file)

    dest = tmp_path / "dest"

    # SECURE BEHAVIOR: preserves symlinks
    shutil.copytree(source, dest, symlinks=True)

    preserved_link = dest / "leaked_link"
    assert preserved_link.is_symlink(), "Expected symlink to be preserved"
    # Note: symlink still points to the same external path, but content wasn't COPIED.
    # In git-sync context, git will store the symlink, which is what we want.
