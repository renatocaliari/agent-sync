"""Skills management for agent-sync.

Centralizes skills from all agents to ~/.agents/skills/ (source of truth).
Automatically configures agents to use global skills.
"""

import shutil
from pathlib import Path
from typing import Optional
from rich.console import Console

from .agents import get_all_agents, BaseAgent


console = Console()

GLOBAL_SKILLS_DIR = Path.home() / ".agents" / "skills"


class SkillsManager:
    """Manages skills centralization and distribution."""
    
    def __init__(self):
        self.global_skills_dir = GLOBAL_SKILLS_DIR
        self.conflicts: list[dict] = []
        self.resolved_conflicts: dict[str, str] = {}
    
    def scan_all_agents(self) -> dict[str, list[Path]]:
        """Scan all agents for existing skills.
        
        Only directories containing SKILL.md are considered valid skills.
        Files directly in the skills directory are ignored.
        
        Returns:
            dict mapping agent name to list of skill paths
        """
        skills_found = {}
        
        for agent in get_all_agents():
            if agent.name == "global-skills":
                continue
            
            agent_skills = []
            
            # Scan agent's skills directory
            if agent.skills_path.exists():
                for item in agent.skills_path.iterdir():
                    # Only sync directories (not files)
                    if item.is_dir():
                        # Check if it's a valid skill (has SKILL.md)
                        if (item / "SKILL.md").exists():
                            agent_skills.append(item)
                        # Also accept directories with common skill files
                        elif any(item.glob("*.md")) or any(item.glob("*.py")) or any(item.glob("*.sh")):
                            # Has markdown or script files, likely a skill
                            agent_skills.append(item)
                    # Ignore files directly in skills directory (.DS_Store, README, etc.)
            
            if agent_skills:
                skills_found[agent.name] = agent_skills
        
        return skills_found
    
    def find_conflicts(self, skills: dict[str, list[Path]]) -> list[dict]:
        """Find skills with same name across different agents.
        
        Returns:
            list of conflict dicts with 'name', 'agents', 'paths'
        """
        name_to_agents: dict[str, list[tuple[str, Path]]] = {}
        
        for agent_name, skill_paths in skills.items():
            for skill_path in skill_paths:
                skill_name = skill_path.stem if skill_path.is_file() else skill_path.name
                
                if skill_name not in name_to_agents:
                    name_to_agents[skill_name] = []
                
                name_to_agents[skill_name].append((agent_name, skill_path))
        
        conflicts = []
        for skill_name, agent_paths in name_to_agents.items():
            if len(agent_paths) > 1:
                conflicts.append({
                    "name": skill_name,
                    "agents": [ap[0] for ap in agent_paths],
                    "paths": [ap[1] for ap in agent_paths],
                })
        
        self.conflicts = conflicts
        return conflicts
    
    def resolve_conflicts(self, conflicts: Optional[list[dict]] = None, auto: bool = True) -> dict[str, str]:
        """Resolve conflicts by renaming duplicates.
        
        Args:
            conflicts: List of conflicts (uses self.conflicts if None)
            auto: If True, auto-rename with agent prefix. If False, would prompt user.
        
        Returns:
            dict mapping original name to resolved name
        """
        if conflicts is None:
            conflicts = self.conflicts
        
        resolved = {}
        
        for conflict in conflicts:
            skill_name = conflict["name"]
            agents = conflict["agents"]
            
            if auto:
                # Auto-rename: keep first as-is, prefix others
                resolved[skill_name] = skill_name  # First keeps name
                
                for i, agent in enumerate(agents[1:], start=1):
                    new_name = f"{skill_name}-{agent}"
                    resolved[f"{skill_name}_{agent}"] = new_name
            else:
                # Would prompt user (not implemented, auto always)
                resolved[skill_name] = skill_name
        
        self.resolved_conflicts = resolved
        return resolved
    
    def centralize(self, dry_run: bool = False) -> dict:
        """Centralize all skills to ~/.agents/skills/.
        
        Args:
            dry_run: If True, don't actually copy files
        
        Returns:
            dict with stats: copied, skipped, conflicts_resolved
        """
        stats = {
            "copied": 0,
            "skipped": 0,
            "conflicts_resolved": 0,
            "errors": 0,
        }
        
        # Ensure global skills directory exists
        if not dry_run:
            self.global_skills_dir.mkdir(parents=True, exist_ok=True)
        
        # Scan all agents
        console.print("\n[bold]Scanning for existing skills...[/bold]\n")
        skills_found = self.scan_all_agents()
        
        if not skills_found:
            console.print("[yellow]No existing skills found in any agent.[/yellow]\n")
            return stats
        
        # Show what was found
        total_skills = sum(len(skills) for skills in skills_found.values())
        console.print(f"Found [cyan]{total_skills}[/cyan] skills:\n")
        
        for agent_name, skill_paths in skills_found.items():
            console.print(f"  • {agent_name}: [green]{len(skill_paths)}[/green] skills")
        
        console.print()
        
        # Find and resolve conflicts
        conflicts = self.find_conflicts(skills_found)
        if conflicts:
            console.print(f"[yellow]⚠ Conflicts detected ({len(conflicts)}):[/yellow]\n")
            for conflict in conflicts:
                console.print(f"  • \"{conflict['name']}\" exists in: {', '.join(conflict['agents'])}")
            console.print()
        
        resolved = self.resolve_conflicts(auto=True)
        stats["conflicts_resolved"] = len(conflicts)
        
        # Copy skills to global directory
        console.print("[bold]Centralizing skills to ~/.agents/skills/...[/bold]\n")
        
        for agent_name, skill_paths in skills_found.items():
            for skill_path in skill_paths:
                skill_name = skill_path.stem if skill_path.is_file() else skill_path.name
                
                # Determine destination name
                dest_name = resolved.get(skill_name, skill_name)
                dest_path = self.global_skills_dir / dest_name
                
                # Check if already exists
                if dest_path.exists():
                    stats["skipped"] += 1
                    continue
                
                try:
                    if not dry_run:
                        if skill_path.is_dir():
                            shutil.copytree(skill_path, dest_path)
                        else:
                            shutil.copy2(skill_path, dest_path)
                    
                    stats["copied"] += 1
                    console.print(f"  [green]✓[/green] {agent_name}: {skill_name}")
                
                except Exception as e:
                    stats["errors"] += 1
                    console.print(f"  [red]✗[/red] {agent_name}: {skill_name} - {e}")
        
        console.print()
        console.print(f"[green]✓ Centralized {stats['copied']} skills[/green]")
        if stats["conflicts_resolved"] > 0:
            console.print(f"  Resolved [yellow]{stats['conflicts_resolved']}[/yellow] conflicts")
        if stats["skipped"] > 0:
            console.print(f"  Skipped [dim]{stats['skipped']}[/dim] (already exists)")
        console.print()
        
        return stats
    
    def configure_agents(self) -> dict[str, dict]:
        """Configure all agents to use global skills.
        
        Returns:
            dict mapping agent name to configuration result
        """
        results = {}
        
        console.print("\n[bold]Configuring agents to use global skills...[/bold]\n")
        
        for agent in get_all_agents():
            if agent.name == "global-skills":
                continue
            
            result = self._configure_agent(agent)
            results[agent.name] = result
            
            status_icon = "✓" if result["success"] else "⚠"
            status_color = "green" if result["success"] else "yellow"
            console.print(f"  [{status_color}]{status_icon}[/{status_color}] {agent.name}: {result['message']}")
        
        console.print()
        return results
    
    def _configure_agent(self, agent: BaseAgent) -> dict:
        """Configure a single agent to use global skills.
        
        Returns:
            dict with success, method, message
        """
        # Try symlink first
        if agent.supports_symlink():
            try:
                self._create_symlink(agent)
                return {
                    "success": True,
                    "method": "symlink",
                    "message": f"Created symlink {agent.commands_path.name}/_global",
                }
            except Exception as e:
                return {
                    "success": False,
                    "method": "symlink",
                    "message": f"Symlink failed: {e}",
                }
        
        # Try config update
        elif agent.supports_config():
            try:
                self._update_config(agent)
                return {
                    "success": True,
                    "method": "config",
                    "message": "Updated config to include global skills",
                }
            except Exception as e:
                return {
                    "success": False,
                    "method": "config",
                    "message": f"Config update failed: {e}",
                }
        
        # Fallback: copy skills
        else:
            try:
                self._copy_skills(agent)
                return {
                    "success": True,
                    "method": "fallback",
                    "message": "Using fallback (skills copied to agent path)",
                }
            except Exception as e:
                return {
                    "success": False,
                    "method": "fallback",
                    "message": f"Fallback failed: {e}",
                }
    
    def _create_symlink(self, agent: BaseAgent) -> None:
        """Create symlink from agent path to global skills."""
        # For Claude Code: ~/.claude/commands/_global -> ~/.agents/skills/
        target_dir = agent.commands_path if hasattr(agent, 'commands_path') else agent.skills_path
        target_dir.mkdir(parents=True, exist_ok=True)
        
        symlink_path = target_dir / "_global"
        
        # Remove existing symlink if present
        if symlink_path.is_symlink():
            symlink_path.unlink()
        elif symlink_path.exists():
            # Backup existing directory
            backup_path = target_dir / "_global_backup"
            shutil.move(str(symlink_path), str(backup_path))
        
        # Create symlink
        symlink_path.symlink_to(self.global_skills_dir)
    
    def _update_config(self, agent: BaseAgent) -> None:
        """Update agent config file to include global skills."""
        config = agent.get_config() or {}
        
        # Add global skills path to config
        if "skills" not in config:
            config["skills"] = {}
        
        if "paths" not in config["skills"]:
            config["skills"]["paths"] = []
        
        global_path = str(self.global_skills_dir)
        if global_path not in config["skills"]["paths"]:
            config["skills"]["paths"].append(global_path)
        
        agent.save_config(config)
    
    def _copy_skills(self, agent: BaseAgent) -> None:
        """Copy skills from global to agent path (fallback)."""
        if not self.global_skills_dir.exists():
            return
        
        agent.skills_path.mkdir(parents=True, exist_ok=True)
        
        for skill_item in self.global_skills_dir.iterdir():
            dest = agent.skills_path / skill_item.name
            
            if not dest.exists():
                if skill_item.is_dir():
                    shutil.copytree(skill_item, dest)
                else:
                    shutil.copy2(skill_item, dest)
    
    def get_summary(self) -> dict:
        """Get summary of skills configuration."""
        return {
            "global_skills_dir": str(self.global_skills_dir),
            "exists": self.global_skills_dir.exists(),
            "skill_count": len(list(self.global_skills_dir.glob("*"))) if self.global_skills_dir.exists() else 0,
        }
