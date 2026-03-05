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
        Symlinks created by users are detected for removal.

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
                    # Skip hidden files (.DS_Store, .git, etc.)
                    if item.name.startswith("."):
                        continue

                    # Detect and skip symlinks (user-created or otherwise)
                    if item.is_symlink():
                        # Symlinks will be removed during centralize
                        continue

                    # Only sync directories (not files)
                    if item.is_dir():
                        # Check if it's a valid skill (has SKILL.md)
                        if (item / "SKILL.md").exists():
                            agent_skills.append(item)
                        # Also accept directories with common skill files
                        elif (
                            any(item.glob("*.md"))
                            or any(item.glob("*.py"))
                            or any(item.glob("*.sh"))
                        ):
                            # Has markdown or script files, likely a skill
                            agent_skills.append(item)
                    # Ignore files directly in skills directory

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
                conflicts.append(
                    {
                        "name": skill_name,
                        "agents": [ap[0] for ap in agent_paths],
                        "paths": [ap[1] for ap in agent_paths],
                    }
                )

        self.conflicts = conflicts
        return conflicts

    def resolve_conflicts(
        self, conflicts: Optional[list[dict]] = None, auto: bool = True
    ) -> dict[str, str]:
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

    def _sync_from_repo(self) -> int:
        """Sync skills from git repo to global skills directory.

        Returns:
            Number of skills synced from repo
        """
        from .sync import SyncManager

        repo_skills_dir = SyncManager.DEFAULT_REPO_DIR / "skills"

        if not repo_skills_dir.exists():
            return 0

        synced = 0
        for skill_dir in repo_skills_dir.iterdir():
            if skill_dir.name.startswith("."):
                continue

            dest = self.global_skills_dir / skill_dir.name
            if not dest.exists():
                if skill_dir.is_dir():
                    shutil.copytree(skill_dir, dest)
                    synced += 1

        return synced

    def centralize(self, dry_run: bool = False, move: bool = True) -> dict:
        """Centralize all skills to ~/.agents/skills/.

        Args:
            dry_run: If True, don't actually move files
            move: If True, move skills (delete from source). If False, copy.

        Returns:
            dict with stats: moved, copied, skipped, conflicts_resolved
        """
        stats = {
            "moved": 0,
            "copied": 0,
            "skipped": 0,
            "conflicts_resolved": 0,
            "errors": 0,
            "symlinks_removed": 0,
        }

        # Ensure global skills directory exists
        if not dry_run:
            self.global_skills_dir.mkdir(parents=True, exist_ok=True)

        # Sync from repo to global skills directory first
        console.print("[bold]📥 Syncing skills from repo to ~/.agents/skills/...[/bold]\n")
        repo_synced = self._sync_from_repo()
        if repo_synced > 0:
            console.print(f"  [green]✓ Synced {repo_synced} skills from repo[/green]\n")

        # Scan all agents
        console.print("[bold]📚 Scanning for existing skills...[/bold]\n")
        skills_found = self.scan_all_agents()

        if not skills_found:
            console.print("[yellow]No new skills found in agent directories.[/yellow]\n")

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
                console.print(
                    f'  • "{conflict["name"]}" exists in: {", ".join(conflict["agents"])}'
                )
            console.print()

        resolved = self.resolve_conflicts(auto=True)
        stats["conflicts_resolved"] = len(conflicts)

        # Move/copy skills to global directory
        action = "Moving" if move else "Copying"
        console.print(f"[bold]{action} skills to ~/.agents/skills/...[/bold]\n")

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
                            if move:
                                shutil.move(str(skill_path), str(dest_path))
                            else:
                                shutil.copytree(skill_path, dest_path)
                        else:
                            if move:
                                shutil.move(str(skill_path), str(dest_path))
                            else:
                                shutil.copy2(skill_path, dest_path)

                        # Remove empty parent directories if moving
                        if move and skill_path.is_dir():
                            try:
                                skill_path.parent.rmdir()  # Only if empty
                            except OSError:
                                pass  # Not empty, that's ok

                    if move:
                        stats["moved"] += 1
                        console.print(
                            f"  [green]✓[/green] {agent_name}: {skill_name} [dim](moved)[/dim]"
                        )
                    else:
                        stats["copied"] += 1
                        console.print(
                            f"  [green]✓[/green] {agent_name}: {skill_name} [dim](copied)[/dim]"
                        )

                except Exception as e:
                    stats["errors"] += 1
                    console.print(f"  [red]✗[/red] {agent_name}: {skill_name} - {e}")

        console.print()

        # Clean up user-created symlinks from agent directories
        console.print("[bold]🧹 Cleaning up user symlinks...[/bold]\n")
        stats["symlinks_removed"] = self._cleanup_user_symlinks()

        if stats["symlinks_removed"] > 0:
            console.print(f"  Removed [yellow]{stats['symlinks_removed']}[/yellow] user symlinks\n")
        else:
            console.print("  [green]✓[/green] No user symlinks found\n")

        # Configure all agents to use global skills (cleans up native agent duplicates)
        console.print("[bold]⚙️  Configuring agents to use global skills...[/bold]\n")
        self.configure_agents()

        # Show summary
        console.print("[bold]📊 Summary:[/bold]\n")
        if move:
            console.print(f"  [green]✓ Moved {stats['moved']} skills[/green] to ~/.agents/skills/")
        else:
            console.print(
                f"  [green]✓ Copied {stats['copied']} skills[/green] to ~/.agents/skills/"
            )

        if stats["conflicts_resolved"] > 0:
            console.print(f"  [yellow]⚠ Resolved {stats['conflicts_resolved']} conflicts[/yellow]")
        if stats["skipped"] > 0:
            console.print(f"  [dim]⊘ Skipped {stats['skipped']} (already exists)[/dim]")
        if stats["symlinks_removed"] > 0:
            console.print(f"  [yellow]🗑 Removed {stats['symlinks_removed']} user symlinks[/yellow]")

        console.print("\n[green]✨ All skills are now centralized in ~/.agents/skills/[/green]")
        console.print("[dim]  This is the single source of truth for all your skills.[/dim]\n")

        return stats

    def _cleanup_user_symlinks(self) -> int:
        """Remove user-created symlinks from agent skill directories.

        Returns:
            Number of symlinks removed
        """
        symlinks_removed = 0

        for agent in get_all_agents():
            if agent.name == "global-skills":
                continue

            if not agent.skills_path.exists():
                continue

            for item in agent.skills_path.iterdir():
                if item.is_symlink():
                    try:
                        item.unlink()
                        symlinks_removed += 1
                    except Exception:
                        pass

        return symlinks_removed

    def configure_agents(self) -> dict[str, dict]:
        """Configure all agents to use global skills."""
        results = {}

        console.print("\n[bold]Configuring agents to use global skills...[/bold]\n")

        for agent in get_all_agents():
            if agent.name == "global-skills":
                continue

            result = self._configure_agent(agent)
            results[agent.name] = result

            status_icon = "✓" if result["success"] else "⚠"
            status_color = "green" if result["success"] else "yellow"
            console.print(
                f"  [{status_color}]{status_icon}[/{status_color}] {agent.name}: {result['message']} [dim]({result['method']})[/dim]"
            )

        console.print()
        return results

    def _configure_agent(self, agent: BaseAgent) -> dict:
        """Configure a single agent to use global skills.

        New order (per plan):
        1. User override (from config.yaml)
        2. YAML Registry default (agent.method)
        3. Implementation (native | config | copy)
        """
        from .config import Config
        user_config = Config()
        
        # Determine method (priority: user override -> registry default)
        agent_conf = user_config.get_agent_config(agent.name)
        method = agent_conf.get("skills_method") or agent.method

        # First, clean up any local skills
        self._cleanup_agent_local_skills(agent)

        # Apply the chosen method
        result = None
        if method == "native":
            result = {
                "success": True,
                "method": "native",
                "message": f"Reads from {self.global_skills_dir} (native support)",
            }

        elif method == "config":
            try:
                self._apply_config_method(agent)
                result = {
                    "success": True,
                    "method": "config",
                    "message": "Updated agent config to include global skills",
                }
            except Exception as e:
                # Fallback to copy if config failed and it's not a user override
                if agent_conf.get("skills_method"):
                     return {"success": False, "method": "config", "message": f"Config update failed: {e}"}
                # Else continue to copy fallback

        if not result:
            # Default fallback (copy) or explicit copy
            try:
                copied = self._copy_skills_to_agent(agent)
                result = {
                    "success": True,
                    "method": "copy",
                    "message": f"Copied {copied} skills to {agent.skills_path}",
                }
            except Exception as e:
                result = {
                    "success": False,
                    "method": "copy",
                    "message": f"Copy failed: {e}",
                }

        # Save successful method to config if not already there
        if result["success"] and not agent_conf.get("skills_method"):
            user_config.set_skills_method(agent.name, result["method"])
            
        return result

    def _apply_config_method(self, agent: BaseAgent) -> None:
        """Apply config method dynamically using registry data."""
        config_update = agent.data.get("config_update")
        if not config_update:
            # Fallback for old opencode style if not in registry
            if agent.name == "opencode":
                config_update = {"path": "skills.paths", "action": "append"}
            else:
                raise ValueError(f"Agent {agent.name} has method 'config' but no config_update defined")

        config = agent.get_config() or {}
        path = config_update.get("path", "")
        action = config_update.get("action", "set")
        value = str(self.global_skills_dir)

        # Navigate and update nested dict
        parts = path.split(".")
        curr = config
        for part in parts[:-1]:
            if part not in curr or not isinstance(curr[part], dict):
                curr[part] = {}
            curr = curr[part]

        last_part = parts[-1]
        if action == "append":
            if last_part not in curr or not isinstance(curr[last_part], list):
                curr[last_part] = []
            if value not in curr[last_part]:
                curr[last_part].append(value)
        else:
            curr[last_part] = value

        agent.save_config(config)

    def _cleanup_agent_local_skills(self, agent: BaseAgent) -> int:
        """Remove all local skills from agent directory (centralized approach).

        After centralize(), all skills live in ~/.agents/skills/.
        Agent directories should only have symlinks or config pointing to it.

        Returns:
            Number of skills removed
        """
        if not agent.skills_path.exists():
            return 0

        removed_count = 0

        for item in agent.skills_path.iterdir():
            # Skip symlinks (like _global in claude-code)
            if item.is_symlink():
                continue

            # Remove skill directories
            if item.is_dir() and (item / "SKILL.md").exists():
                shutil.rmtree(item)
                removed_count += 1
            # Remove skill files
            elif item.is_file() and item.suffix in [".md", ".py", ".sh"]:
                item.unlink()
                removed_count += 1

        return removed_count

    def _copy_skills_to_agent(self, agent: BaseAgent) -> int:
        """Copy all skills from global dir to agent skills directory.

        This is used as a fallback for agents that don't support
        config-based paths (like qwen-code).

        Returns:
            Number of skills copied
        """
        if not self.global_skills_dir.exists():
            return 0

        agent.skills_path.mkdir(parents=True, exist_ok=True)
        copied = 0

        for skill_dir in self.global_skills_dir.iterdir():
            if skill_dir.name.startswith("."):
                continue

            dest = agent.skills_path / skill_dir.name

            # Skip if already exists (don't overwrite)
            if dest.exists():
                continue

            if skill_dir.is_dir():
                shutil.copytree(skill_dir, dest)
                copied += 1

        return copied

    def get_summary(self) -> dict:
        """Get summary of skills configuration."""
        skill_count = 0

        if self.global_skills_dir.exists():
            for item in self.global_skills_dir.iterdir():
                # Count only valid skills (directories with SKILL.md)
                if item.is_dir() and (item / "SKILL.md").exists():
                    skill_count += 1

        return {
            "global_skills_dir": str(self.global_skills_dir),
            "exists": self.global_skills_dir.exists(),
            "skill_count": skill_count,
        }

    def distribute_to_all_agents(self) -> dict:
        """Copy all skills from ~/.agents/skills/ to all agent directories.

        This is useful for:
        - Backup: local copies in each agent directory
        - Testing: verify agents read from local vs global
        - Debug: troubleshoot symlink/config issues

        Returns:
            dict with 'distributed' count and 'agents_configured' count
        """
        import hashlib

        stats = {
            "distributed": 0,
            "agents_configured": 0,
            "skipped": 0,
        }

        if not self.global_skills_dir.exists():
            console.print("[yellow]No skills found in ~/.agents/skills/[/yellow]\n")
            return stats

        console.print(f"Source: [cyan]{self.global_skills_dir}[/cyan]\n")

        for agent in get_all_agents():
            if agent.name == "global-skills":
                continue

            console.print(f"  Distributing to {agent.name}...")

            # Ensure agent skills directory exists
            agent.skills_path.mkdir(parents=True, exist_ok=True)

            agent_count = 0
            for skill_item in self.global_skills_dir.iterdir():
                if skill_item.name.startswith("."):
                    continue  # Skip .DS_Store, etc.

                dest = agent.skills_path / skill_item.name

                if not dest.exists():
                    # Copy if doesn't exist
                    if skill_item.is_dir():
                        shutil.copytree(skill_item, dest)
                    else:
                        shutil.copy2(skill_item, dest)
                    agent_count += 1
                    stats["distributed"] += 1
                else:
                    # Check if different (idempotent)
                    if skill_item.is_file() and dest.is_file():
                        src_hash = hashlib.md5(skill_item.read_bytes()).hexdigest()
                        dest_hash = hashlib.md5(dest.read_bytes()).hexdigest()

                        if src_hash != dest_hash:
                            # Files differ, skip to avoid overwriting local changes
                            console.print(
                                f"    [yellow]⚠ {skill_item.name} differs, skipping[/yellow]"
                            )
                        else:
                            stats["skipped"] += 1
                    else:
                        stats["skipped"] += 1

            if agent_count > 0:
                console.print(f"    [green]✓ {agent_count} skills copied[/green]")
                stats["agents_configured"] += 1
            else:
                console.print(f"    [dim]No new skills to copy[/dim]")

        console.print()
        return stats
