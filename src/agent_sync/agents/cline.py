"""Cline agent handler - Copy method for skills sync."""

import shutil
from pathlib import Path
from typing import List, Optional, Dict, Any

from .base import BaseAgent, GLOBAL_SKILLS_DIR


class ClineAgent(BaseAgent):
    """
    Cline integration with copy-based skills sync.
    
    Cline uses:
    - ~/.cline/skills/{name}/SKILL.md (global)
    - .cline/skills/{name}/SKILL.md (project)
    - .clinerules/skills/{name}/SKILL.md (project alternative)
    - .claude/skills/{name}/SKILL.md (project legacy)
    
    Method: Copy FROM project/global directories TO ~/.agents/skills/
    """

    def __init__(self, name: str, data: Dict[str, Any]):
        super().__init__(name, data)
        self.copy_from = data.get("copy_from", [])  # List of source paths
        self.copy_to = self._expand_path(data.get("copy_to", "~/.agents/skills/"))

    def get_source_paths(self) -> List[Path]:
        """Get all source paths for Cline skills."""
        paths = []
        for p in self.copy_from:
            paths.append(self._expand_path(p))
        return [p for p in paths if p.exists()]

    def sync_skills(self, source: Optional[Path] = None, dry_run: bool = False) -> List[str]:
        """
        Sync skills FROM Cline directories TO ~/.agents/skills/.
        
        Args:
            source: Not used (we read from copy_from paths)
            dry_run: If True, don't actually copy
        
        Returns:
            List of synced skills
        """
        synced = []
        
        # Read from all source paths
        for source_path in self.get_source_paths():
            if not source_path.exists():
                continue
            
            # Copy each skill directory
            for skill_dir in source_path.iterdir():
                if skill_dir.is_dir() and not skill_dir.name.startswith("."):
                    skill_file = skill_dir / "SKILL.md"
                    if skill_file.exists():
                        dest = self.copy_to / skill_dir.name
                        
                        if not dry_run:
                            self.copy_to.mkdir(parents=True, exist_ok=True)
                            if dest.exists():
                                shutil.rmtree(dest)
                            shutil.copytree(skill_dir, dest)
                        
                        synced.append(f"{skill_dir.name} (from {source_path})")
        
        return synced

    def sync_to_cline(self, source: Optional[Path] = None, dry_run: bool = False) -> List[str]:
        """
        Sync skills TO Cline FROM ~/.agents/skills/.
        
        Args:
            source: Source skills directory (defaults to ~/.agents/skills/)
            dry_run: If True, don't actually copy
        
        Returns:
            List of synced skills
        """
        if source is None:
            source = GLOBAL_SKILLS_DIR
        
        synced = []
        
        if not source.exists():
            return synced
        
        # Ensure destination exists
        cline_skills_dir = self._expand_path("~/.cline/skills/")
        if not dry_run:
            cline_skills_dir.mkdir(parents=True, exist_ok=True)
        
        # Copy each skill
        for skill_dir in source.iterdir():
            if skill_dir.is_dir() and not skill_dir.name.startswith("."):
                skill_file = skill_dir / "SKILL.md"
                if skill_file.exists():
                    dest = cline_skills_dir / skill_dir.name
                    
                    if not dry_run:
                        if dest.exists():
                            shutil.rmtree(dest)
                        shutil.copytree(skill_dir, dest)
                    
                    synced.append(skill_dir.name)
        
        return synced

    def get_all_skills_paths(self) -> List[Path]:
        """Get all skills paths for Cline."""
        paths = self.get_source_paths()
        paths.append(self.copy_to)  # Hub destination
        return [p for p in paths if p.exists()]
