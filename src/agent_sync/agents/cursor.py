"""Cursor agent handler - Native support for ~/.agents/skills/."""

from pathlib import Path
from typing import List, Optional, Dict, Any

from .base import BaseAgent, GLOBAL_SKILLS_DIR


class CursorAgent(BaseAgent):
    """
    Cursor IDE integration with native skills support.
    
    Cursor uses:
    - ~/.cursor/skills/{name}/SKILL.md (global)
    - .cursor/skills/{name}/SKILL.md (project)
    
    Native: Cursor can read from ~/.agents/skills/ natively.
    """

    def __init__(self, name: str, data: Dict[str, Any]):
        super().__init__(name, data)
        self.migrate_from = data.get("migrate_from", [])

    def get_source_paths(self) -> List[Path]:
        """Get all source paths for Cursor skills."""
        paths = []
        for p in self.migrate_from:
            paths.append(self._expand_path(p))
        return [p for p in paths if p.exists()]

    def sync_skills(self, source: Optional[Path] = None, dry_run: bool = False) -> List[str]:
        """
        Sync skills FROM Cursor directories TO ~/.agents/skills/.
        
        Args:
            source: Not used (we read from migrate_from paths)
            dry_run: If True, don't actually copy
        
        Returns:
            List of synced skills
        """
        import shutil
        
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
                        dest = GLOBAL_SKILLS_DIR / skill_dir.name
                        
                        if not dry_run:
                            GLOBAL_SKILLS_DIR.mkdir(parents=True, exist_ok=True)
                            if dest.exists():
                                shutil.rmtree(dest)
                            shutil.copytree(skill_dir, dest)
                        
                        synced.append(f"{skill_dir.name} (from {source_path})")
        
        return synced

    def get_all_skills_paths(self) -> List[Path]:
        """Get all skills paths for Cursor."""
        paths = self.get_source_paths()
        paths.append(GLOBAL_SKILLS_DIR)  # Hub
        return [p for p in paths if p.exists()]
