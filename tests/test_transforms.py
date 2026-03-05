"""Tests for agent-sync transform utilities."""

import pytest
from pathlib import Path
import shutil

from agent_sync.agents.transforms import (
    remove_yaml_frontmatter,
    flatten_skill_to_md,
    unflatten_md_to_skill,
    copy_skill_directory,
    transform_skill,
)


class TestTransforms:
    """Test transform utilities."""

    def test_remove_yaml_frontmatter(self):
        """Test removing YAML frontmatter from markdown."""
        content = """---
name: test-skill
description: A test skill
---

# Test Skill

This is a test.
"""
        result = remove_yaml_frontmatter(content)
        assert result.strip() == "# Test Skill\n\nThis is a test."

    def test_remove_yaml_frontmatter_no_frontmatter(self):
        """Test content without frontmatter."""
        content = "# Test Skill\n\nThis is a test."
        result = remove_yaml_frontmatter(content)
        assert result.strip() == "# Test Skill\n\nThis is a test."

    def test_remove_yaml_frontmatter_empty(self):
        """Test empty content."""
        result = remove_yaml_frontmatter("")
        assert result.strip() == ""

    def test_flatten_skill_to_md(self, tmp_path):
        """Test flattening skill directory to flat .md file."""
        # Create skill directory structure
        skill_dir = tmp_path / "test-skill"
        skill_dir.mkdir()
        
        skill_file = skill_dir / "SKILL.md"
        skill_file.write_text("""---
name: test-skill
description: A test skill
---

# Test Skill

This is a test.
""")
        
        output_dir = tmp_path / "output"
        output_dir.mkdir()
        
        # Transform
        result = flatten_skill_to_md(skill_dir, output_dir)
        
        assert result is not None
        assert result.name == "test-skill.md"
        assert result.exists()
        
        # Check content (frontmatter removed)
        content = result.read_text()
        assert "# Test Skill" in content
        assert "name:" not in content
        assert "description:" not in content

    def test_flatten_skill_to_md_no_skill_file(self, tmp_path):
        """Test flattening when SKILL.md doesn't exist."""
        skill_dir = tmp_path / "test-skill"
        skill_dir.mkdir()
        
        output_dir = tmp_path / "output"
        output_dir.mkdir()
        
        result = flatten_skill_to_md(skill_dir, output_dir)
        assert result is None

    def test_unflatten_md_to_skill(self, tmp_path):
        """Test unflattening flat .md file to skill directory."""
        # Create flat .md file
        md_file = tmp_path / "test-skill.md"
        md_file.write_text("# Test Skill\n\nThis is a test.")
        
        output_dir = tmp_path / "output"
        output_dir.mkdir()
        
        # Transform
        result = unflatten_md_to_skill(md_file, output_dir)
        
        assert result is not None
        assert result.name == "test-skill"
        assert result.exists()
        assert (result / "SKILL.md").exists()
        
        # Check content (frontmatter added)
        content = (result / "SKILL.md").read_text()
        assert "name: test-skill" in content
        assert "description:" in content
        assert "# Test Skill" in content

    def test_unflatten_md_to_skill_with_frontmatter(self, tmp_path):
        """Test unflattening .md file that already has frontmatter."""
        # Create flat .md file with frontmatter
        md_file = tmp_path / "test-skill.md"
        md_file.write_text("""---
name: test-skill
description: Existing frontmatter
---

# Test Skill

This is a test.
""")
        
        output_dir = tmp_path / "output"
        output_dir.mkdir()
        
        # Transform
        result = unflatten_md_to_skill(md_file, output_dir)
        
        assert result is not None
        
        # Check content (original frontmatter preserved)
        content = (result / "SKILL.md").read_text()
        assert "name: test-skill" in content
        assert "Existing frontmatter" in content

    def test_unflatten_md_to_skill_no_md_file(self, tmp_path):
        """Test unflattening when .md file doesn't exist."""
        md_file = tmp_path / "nonexistent.md"
        output_dir = tmp_path / "output"
        output_dir.mkdir()
        
        result = unflatten_md_to_skill(md_file, output_dir)
        assert result is None

    def test_unflatten_md_to_skill_wrong_extension(self, tmp_path):
        """Test unflattening file without .md extension."""
        txt_file = tmp_path / "test-skill.txt"
        txt_file.write_text("Test content")
        
        output_dir = tmp_path / "output"
        output_dir.mkdir()
        
        result = unflatten_md_to_skill(txt_file, output_dir)
        assert result is None

    def test_copy_skill_directory(self, tmp_path):
        """Test copying skill directory as-is."""
        # Create skill directory structure
        skill_dir = tmp_path / "test-skill"
        skill_dir.mkdir()
        
        skill_file = skill_dir / "SKILL.md"
        skill_file.write_text("# Test Skill")
        
        # Add extra file
        extra_file = skill_dir / "helper.py"
        extra_file.write_text("print('hello')")
        
        output_dir = tmp_path / "output"
        output_dir.mkdir()
        
        # Copy
        result = copy_skill_directory(skill_dir, output_dir)
        
        assert result is not None
        assert result.name == "test-skill"
        assert result.exists()
        assert (result / "SKILL.md").exists()
        assert (result / "helper.py").exists()

    def test_copy_skill_directory_no_source(self, tmp_path):
        """Test copying when source doesn't exist."""
        skill_dir = tmp_path / "nonexistent"
        output_dir = tmp_path / "output"
        output_dir.mkdir()
        
        result = copy_skill_directory(skill_dir, output_dir)
        assert result is None

    def test_transform_skill_flatten(self, tmp_path):
        """Test transform_skill with flatten type."""
        skill_dir = tmp_path / "test-skill"
        skill_dir.mkdir()
        skill_file = skill_dir / "SKILL.md"
        skill_file.write_text("---\nname: test\n---\n# Test")
        
        output_dir = tmp_path / "output"
        output_dir.mkdir()
        
        result = transform_skill(skill_dir, output_dir, "flatten")
        assert result is not None
        assert result.suffix == ".md"

    def test_transform_skill_copy(self, tmp_path):
        """Test transform_skill with copy type."""
        skill_dir = tmp_path / "test-skill"
        skill_dir.mkdir()
        skill_file = skill_dir / "SKILL.md"
        skill_file.write_text("# Test")
        
        output_dir = tmp_path / "output"
        output_dir.mkdir()
        
        result = transform_skill(skill_dir, output_dir, "copy")
        assert result is not None
        assert result.is_dir()

    def test_transform_skill_default(self, tmp_path):
        """Test transform_skill with unknown type (defaults to copy)."""
        skill_dir = tmp_path / "test-skill"
        skill_dir.mkdir()
        skill_file = skill_dir / "SKILL.md"
        skill_file.write_text("# Test")
        
        output_dir = tmp_path / "output"
        output_dir.mkdir()
        
        result = transform_skill(skill_dir, output_dir, "unknown")
        assert result is not None
        assert result.is_dir()
