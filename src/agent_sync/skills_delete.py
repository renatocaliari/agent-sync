"""Skills deletion management."""

import shutil
from pathlib import Path
from typing import List, Optional
from rich.console import Console

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
        from .validators import validate_skill_name

        stats = {
            "deleted_from_hub": 0,
            "hub_files": 0,
            "deleted_from_agents": 0,
            "agent_files": 0,
            "not_found": 0,
            "errors": 0,
        }
        
        # Ensure global skills dir is resolved for safety checks
        self.global_skills_dir.mkdir(parents=True, exist_ok=True)
        resolved_hub_base = self.global_skills_dir.resolve()

        for skill_name in skill_names:
            # Security check: validate skill name format
            if not validate_skill_name(skill_name):
                stats["errors"] += 1
                console.print(f"[red]✗ Invalid skill name: {skill_name}[/red]")
                continue

            # Delete from hub
            hub_skill_path = (self.global_skills_dir / skill_name).resolve()
            
            # Security check: ensure path is still within hub directory
            try:
                hub_skill_path.relative_to(resolved_hub_base)
            except ValueError:
                stats["errors"] += 1
                console.print(f"[red]✗ Security: Path traversal attempt detected for skill '{skill_name}'[/red]")
                continue

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
                
                resolved_agent_base = agent_skills_path.resolve()
                
                # Security check: ensure path is still within agent skills directory
                try:
                    # Note: agent_skill_path might be a symlink to hub.
                    # If it's a symlink, resolving it will point to the hub.
                    # shutil.rmtree or unlink on a symlink deletes the link, not the target.
                    # But we want to be sure we are unlinking something inside the agent skills dir.
                    # If it's a symlink, we should NOT resolve it before relative_to check
                    # IF we want to make sure the LINK is inside the agent dir.

                    # Re-evaluate: if it's a symlink, Path(agent_skills_path / skill_name) is what we want to delete.
                    # If we use .resolve(), we might get a path outside agent_skills_path if it's a symlink.

                    target_to_check = agent_skills_path / skill_name
                    # Check if it would escape the base directory
                    if ".." in skill_name or skill_name.startswith("/"):
                         # validate_skill_name already caught this, but defense in depth
                         raise ValueError("Path traversal")

                    # Use .resolve() only if it's NOT a symlink?
                    # Actually, if it's a symlink, we want to remove the symlink itself.
                    # The safest way to check for path traversal without resolving symlinks
                    # to their targets is to check the absolute path but WITHOUT resolving.

                    abs_target = target_to_check.absolute()
                    abs_base = resolved_agent_base.absolute()
                    abs_target.relative_to(abs_base)

                except ValueError:
                    stats["errors"] += 1
                    console.print(f"[red]✗ Security: Path traversal attempt detected in agent {agent.name}[/red]")
                    continue

                if target_to_check.exists() or target_to_check.is_symlink():
                    agent_files = self.count_skill_files(target_to_check)
                    agent_files_total += agent_files
                    
                    if not dry_run:
                        try:
                            if target_to_check.is_symlink():
                                target_to_check.unlink()
                            elif target_to_check.is_dir():
                                shutil.rmtree(target_to_check)
                            else:
                                target_to_check.unlink()
                            
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
