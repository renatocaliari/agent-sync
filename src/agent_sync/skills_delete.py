"""Skills deletion management."""

import shutil
from pathlib import Path
from typing import List, Optional
from rich.console import Console
from .validators import validate_skill_name

console = Console()


class SkillsDeleter:
    """Manages deletion of skills from hub and agents."""

    def __init__(self):
        from .config import Config
        from .agents import get_agents
        
        self.config = Config()
        self.global_skills_dir = Path.home() / ".agents" / "skills"
        self.agents = get_agents()

    def list_skills(self) -> List[str]:
        """List all skills in the global hub."""
        if not self.global_skills_dir.exists():
            return []
        
        skills = []
        for item in self.global_skills_dir.iterdir():
            if item.is_dir() and not item.name.startswith("."):
                if (item / "SKILL.md").exists():
                    skills.append(item.name)
        
        return sorted(skills)

    def count_skill_files(self, skill_path: Path) -> int:
        """Count files in a skill directory."""
        if not skill_path.exists() or not skill_path.is_dir():
            return 0
        return sum(1 for f in skill_path.rglob('*') if f.is_file())

    def delete_skills(self, skill_names: List[str], dry_run: bool = False) -> dict:
        """
        Delete skills from hub and all agent directories.
        
        Args:
            skill_names: List of skill names to delete
            dry_run: If True, only show what would be deleted
        
        Returns:
            Dictionary with deletion statistics
        """
        stats = {
            "deleted_from_hub": 0,
            "hub_files": 0,
            "deleted_from_agents": 0,
            "agent_files": 0,
            "not_found": 0,
            "errors": 0,
        }
        
        for skill_name in skill_names:
            # SECURITY: Validate skill name to prevent path traversal
            if not validate_skill_name(skill_name):
                stats["errors"] += 1
                console.print(f"[red]✗ Invalid skill name (security risk): {skill_name}[/red]")
                continue

            # Delete from hub
            hub_skill_path = self.global_skills_dir / skill_name
            
            if not hub_skill_path.exists():
                stats["not_found"] += 1
                console.print(f"[yellow]⚠ Skill '{skill_name}' not found in hub[/yellow]")
                continue
            
            # Count files before deletion
            hub_files = self.count_skill_files(hub_skill_path)
            
            if not dry_run:
                try:
                    shutil.rmtree(hub_skill_path)
                    stats["deleted_from_hub"] += 1
                    stats["hub_files"] += hub_files
                    console.print(f"[green]✓ Deleted[/green] {skill_name} from hub ({hub_files} files)")
                except Exception as e:
                    stats["errors"] += 1
                    console.print(f"[red]✗ Error deleting {skill_name} from hub: {e}[/red]")
            else:
                console.print(f"[dim]Would delete {skill_name} from hub ({hub_files} files)[/dim]")
            
            # Delete from all agents
            agent_files_total = 0
            for agent in self.agents:
                if agent.name == "global-skills":
                    continue
                
                # Get agent skills path
                agent_skills_path = agent.skills_path
                
                if not agent_skills_path.exists():
                    continue
                
                agent_skill_path = agent_skills_path / skill_name
                
                if agent_skill_path.exists():
                    agent_files = self.count_skill_files(agent_skill_path)
                    agent_files_total += agent_files
                    
                    if not dry_run:
                        try:
                            if agent_skill_path.is_dir():
                                shutil.rmtree(agent_skill_path)
                            else:
                                agent_skill_path.unlink()
                            
                            stats["deleted_from_agents"] += 1
                            stats["agent_files"] += agent_files
                        except Exception as e:
                            stats["errors"] += 1
                            console.print(f"[red]✗ Error deleting {skill_name} from {agent.name}: {e}[/red]")
                    else:
                        console.print(f"[dim]Would delete {skill_name} from {agent.name} ({agent_files} files)[/dim]")
            
            if not dry_run and agent_files_total > 0:
                console.print(f"[dim]  └─ {agent_files_total} files removed from agent directories[/dim]")
        
        return stats
