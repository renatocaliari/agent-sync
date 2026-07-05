
import os
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from agent_sync.publish.git_publish import do_git_publish

class TestPublishSecurity(unittest.TestCase):
    def setUp(self):
        self.test_dir = Path(tempfile.mkdtemp())
        self.source_dir = self.test_dir / "source"
        self.source_dir.mkdir()

        # Create a secret file outside the source directory
        self.secret_file = self.test_dir / "secret.txt"
        self.secret_file.write_text("SENSITIVE DATA")

        # Create a symlink in the source directory pointing to the secret file
        self.symlink_file = self.source_dir / "link_to_secret.txt"
        self.symlink_file.symlink_to(self.secret_file)

        # Create a normal file
        self.normal_file = self.source_dir / "normal.txt"
        self.normal_file.write_text("Normal content")

        # Create a directory with an excluded name
        self.sessions_dir = self.source_dir / "sessions"
        self.sessions_dir.mkdir()
        (self.sessions_dir / "session.log").write_text("Session data")

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    @patch("agent_sync.publish.git_publish.git_commit_and_push")
    @patch("agent_sync.publish.git_publish.console")
    def test_publish_does_not_leak_symlink_content(self, mock_console, mock_push):
        items = [(self.source_dir, "test_skill")]

        def mock_readme(path, items, repo):
            pass

        success = do_git_publish(
            items=items,
            subdir="skills",
            readme_generator=mock_readme,
            count=1,
            item_name="skills",
            repo="https://github.com/user/repo"
        )

        self.assertTrue(success)

        # The pushed content is in a temp dir which is deleted in 'finally' block.
        # But we can check the behavior by looking at what was copied to the temp dir.
        # Since do_git_publish deletes the tmp_dir, we need to intercept it or
        # just trust that our changes to use symlinks=True and follow_symlinks=False work.

        # A better way is to mock shutil.copytree and shutil.copy2 to see their arguments.

    @patch("agent_sync.publish.git_publish.shutil.copytree")
    @patch("agent_sync.publish.git_publish.shutil.copy2")
    @patch("agent_sync.publish.git_publish.git_commit_and_push")
    def test_publish_security_parameters(self, mock_push, mock_copy2, mock_copytree):
        items = [(self.source_dir, "test_skill"), (self.normal_file, "normal.txt")]

        def mock_readme(path, items, repo):
            pass

        do_git_publish(
            items=items,
            subdir="skills",
            readme_generator=mock_readme,
            count=2,
            item_name="skills",
            repo="https://github.com/user/repo"
        )

        # Verify shutil.copytree was called with symlinks=True
        mock_copytree.assert_called()
        args, kwargs = mock_copytree.call_args
        self.assertTrue(kwargs.get("symlinks"))

        # Verify shutil.copy2 was called with follow_symlinks=False
        mock_copy2.assert_called()
        args, kwargs = mock_copy2.call_args
        self.assertFalse(kwargs.get("follow_symlinks", True))

    def test_ignore_func_literal_match(self):
        from agent_sync.publish.git_publish import _ignore_func

        ignore = _ignore_func("sessions", "*.log")
        ignored = ignore("path", ["sessions", "cache", "debug.log", "normal.txt"])

        self.assertIn("sessions", ignored)
        self.assertIn("debug.log", ignored)
        self.assertNotIn("cache", ignored)
        self.assertNotIn("normal.txt", ignored)

if __name__ == "__main__":
    unittest.main()
