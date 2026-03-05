"""RooCode agent handler - Native support for ~/.agents/skills/."""

from pathlib import Path
from typing import List, Optional, Dict, Any

from .base import BaseAgent, GLOBAL_SKILLS_DIR


class RooCodeAgent(BaseAgent):
    """
    RooCode integration with native skills support.
    
    RooCode natively reads from:
    - ~/.roo/skills/ (higher priority)
    - ~/.agents/skills/ (lower priority - cross-agent)
    - .roo/skills/ (project, higher priority)
    - .agents/skills/ (project, lower priority)
    
    Also supports mode-specific skills:
    - ~/.roo/skills-code/ (Code mode only)
    - ~/.roo/skills-architect/ (Architect mode only)
    """

    def __init__(self, name: str, data: Dict[str, Any]):
        super().__init__(name, data)
        self.mode_specific = data.get("mode_specific", False)

    def get_all_skills_paths(self) -> List[Path]:
        """Get all skills paths for RooCode."""
        paths = []
        
        # Global skills (native support)
        paths.append(GLOBAL_SKILLS_DIR)  # ~/.agents/skills/
        paths.append(self.config_dir / "skills")  # ~/.roo/skills/
        
        # Mode-specific global skills
        if self.mode_specific:
            # Could add logic to discover mode-specific directories
            pass
        
        return [p for p in paths if p.exists()]

    def sync_skills(self, source: Path, dry_run: bool = False) -> List[str]:
        """
        Sync skills from source to RooCode directories.
        
        Since RooCode natively supports ~/.agents/skills/, no copy is needed.
        This method ensures the directory structure is correct.
        
        Args:
            source: Source skills directory (usually ~/.agents/skills/)
            dry_run: If True, don't actually copy
        
        Returns:
            List of synced skills
        """
        # RooCode reads natively, so no sync needed
        # Just verify the structure
        synced = []
        
        if source.exists():
            for skill_dir in source.iterdir():
                if skill_dir.is_dir() and not skill_dir.name.startswith("."):
                    skill_file = skill_dir / "SKILL.md"
                    if skill_file.exists():
                        synced.append(skill_dir.name)
        
        return synced

    def supports_mode_specific(self) -> bool:
        """Check if this agent supports mode-specific skills."""
        return self.mode_specific

    def get_mode_specific_path(self, mode_slug: str, global_scope: bool = True) -> Path:
        """
        Get path for mode-specific skills.
        
        Args:
            mode_slug: Mode identifier (e.g., 'code', 'architect')
            global_scope: If True, return global path; else project path
        
        Returns:
            Path to mode-specific skills directory
        """
        if global_scope:
            return self.config_dir / f"skills-{mode_slug}"
        else:
            # Project scope - would need project root
            return Path(f".roo/skills-{mode_slug}")
