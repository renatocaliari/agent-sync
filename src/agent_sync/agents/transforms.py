"""Transform utilities for agent skills.

These transforms are used for agents that need format conversion:
- flatten: skills/{name}/SKILL.md → {name}.md (for agents that use flat .md files)
- unflatten: {name}.md → skills/{name}/SKILL.md (reverse conversion)
"""

import re
from pathlib import Path
from typing import Optional


def flatten_skill_to_md(skill_dir: Path, output_dir: Path) -> Optional[Path]:
    """
    Transform a skill directory (SKILL.md) to flat .md file.
    
    Some agents use flat .md files instead of skill directories.
    
    Args:
        skill_dir: Path to skill directory (e.g., ~/.agents/skills/pdf-processing/)
        output_dir: Path to output directory (e.g., agent's rules directory)
    
    Returns:
        Path to created file, or None if transformation failed
    """
    if not skill_dir.exists() or not skill_dir.is_dir():
        return None
    
    skill_file = skill_dir / "SKILL.md"
    if not skill_file.exists():
        return None
    
    skill_name = skill_dir.name
    output_file = output_dir / f"{skill_name}.md"
    
    # Read SKILL.md content
    content = skill_file.read_text()
    
    # Optional: Remove YAML frontmatter if target agent doesn't support it
    content = remove_yaml_frontmatter(content)
    
    # Write flat .md file
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file.write_text(content)
    
    return output_file


def unflatten_md_to_skill(md_file: Path, output_dir: Path) -> Optional[Path]:
    """
    Transform a flat .md file (from Cursor) to skill directory with SKILL.md.
    
    Transforms: {name}.md → skills/{name}/SKILL.md
    
    Args:
        md_file: Path to .md file (e.g., ~/.cursor/rules/pdf-processing.md)
        output_dir: Path to output directory (e.g., ~/.agents/skills/)
    
    Returns:
        Path to created skill directory, or None if transformation failed
    """
    if not md_file.exists() or not md_file.is_file():
        return None
    
    if md_file.suffix != ".md":
        return None
    
    skill_name = md_file.stem  # filename without .md
    skill_dir = output_dir / skill_name
    skill_file = skill_dir / "SKILL.md"
    
    # Read flat .md content
    content = md_file.read_text()
    
    # Create skill directory
    output_dir.mkdir(parents=True, exist_ok=True)
    skill_dir.mkdir(parents=True, exist_ok=True)
    
    # Add YAML frontmatter if not present
    if not content.strip().startswith("---"):
        # Generate frontmatter from filename
        frontmatter = f"""---
name: {skill_name}
description: Skill imported from {md_file.name}
---

"""
        content = frontmatter + content
    
    # Write SKILL.md
    skill_file.write_text(content)
    
    return skill_dir


def remove_yaml_frontmatter(content: str) -> str:
    """
    Remove YAML frontmatter from markdown content.
    
    Args:
        content: Markdown content with optional YAML frontmatter
    
    Returns:
        Content without frontmatter
    """
    # Pattern to match YAML frontmatter (--- at start, then --- to end)
    pattern = r'^---\s*\n.*?\n---\s*\n'
    
    # Remove frontmatter if present
    result = re.sub(pattern, '', content, flags=re.DOTALL)
    
    return result.strip()


def copy_skill_directory(skill_dir: Path, output_dir: Path) -> Optional[Path]:
    """
    Copy skill directory as-is (for Cline, Windsurf, RooCode).
    
    Args:
        skill_dir: Path to skill directory
        output_dir: Path to output directory
    
    Returns:
        Path to copied directory, or None if copy failed
    """
    import shutil
    
    if not skill_dir.exists() or not skill_dir.is_dir():
        return None
    
    skill_name = skill_dir.name
    dest = output_dir / skill_name
    
    # Copy entire directory
    output_dir.mkdir(parents=True, exist_ok=True)
    if dest.exists():
        shutil.rmtree(dest)
    shutil.copytree(skill_dir, dest)
    
    return dest


def transform_skill(skill_dir: Path, output_dir: Path, transform_type: str) -> Optional[Path]:
    """
    Transform skill based on type.
    
    Args:
        skill_dir: Path to source skill directory
        output_dir: Path to destination directory
        transform_type: Type of transformation ('flatten', 'copy', 'unflatten')
    
    Returns:
        Path to transformed output, or None if failed
    """
    if transform_type == "flatten":
        return flatten_skill_to_md(skill_dir, output_dir)
    elif transform_type == "unflatten":
        # For unflatten, skill_dir is actually the .md file parent
        # and we iterate over .md files
        return None  # Handled separately in copy_from logic
    elif transform_type == "copy":
        return copy_skill_directory(skill_dir, output_dir)
    else:
        # Default to copy
        return copy_skill_directory(skill_dir, output_dir)
