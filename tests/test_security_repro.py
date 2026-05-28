import shutil
from pathlib import Path
import pytest
from agent_sync.sync import SyncManager
from agent_sync.config import Config

def test_sync_manager_copy_item_security(tmp_path):
    """
    Verify that SyncManager._copy_item preserves symlinks.
    """
    config = Config()
    # Mock repo_dir to avoid interference with real files
    config.repo_url = "https://github.com/test/repo"

    manager = SyncManager(config)
    manager.repo_dir = tmp_path / "repo"
    manager.repo_dir.mkdir()

    source_dir = tmp_path / "source"
    source_dir.mkdir()

    external_file = tmp_path / "external.txt"
    external_file.write_text("SECRET")

    symlink_path = source_dir / "link"
    symlink_path.symlink_to(external_file)

    dest_dir = tmp_path / "dest"
    dest_dir.mkdir()

    # Test _copy_item
    manager._copy_item(symlink_path, source_dir, dest_dir)

    copied_link = dest_dir / "link"
    assert copied_link.is_symlink(), "SyncManager should preserve symlinks"
    assert str(copied_link.readlink()) == str(external_file), "Symlink should point to the same target"

def test_sync_manager_copy_directory_security(tmp_path):
    """
    Verify that SyncManager._copy_directory preserves symlinks.
    """
    config = Config()
    manager = SyncManager(config)
    manager.repo_dir = tmp_path / "repo"
    manager.repo_dir.mkdir()

    source_dir = tmp_path / "source"
    source_dir.mkdir()

    external_file = tmp_path / "external.txt"
    external_file.write_text("SECRET")

    symlink_path = source_dir / "link"
    symlink_path.symlink_to(external_file)

    dest_dir = tmp_path / "dest"

    # Test _copy_directory
    manager._copy_directory(source_dir, dest_dir)

    copied_link = dest_dir / "link"
    assert copied_link.is_symlink(), "SyncManager._copy_directory should preserve symlinks"
