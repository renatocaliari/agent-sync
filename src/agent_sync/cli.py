"""Main CLI entry point for agent-sync."""

import os
import threading
from pathlib import Path
from datetime import datetime, timedelta
import click
from rich.console import Console
from rich.table import Table
from typing import Optional

from . import __version__
from .sync import SyncManager
from .config import Config, DEFAULT_STATE_DIR

console = Console()

# Update check configuration
UPDATE_CHECK_FILE = DEFAULT_STATE_DIR / ".last_update_check"
UPDATE_PENDING_FILE = DEFAULT_STATE_DIR / ".pending_update"


def check_for_updates_async():
    """Check for updates once per week, asynchronously."""
    if not _should_check_for_updates():
        return
    
    # Run in background thread (doesn't block command)
    thread = threading.Thread(target=_check_and_notify, daemon=True)
    thread.start()


def _should_check_for_updates() -> bool:
    """Check if we should check for updates (once per week)."""
    if not UPDATE_CHECK_FILE.exists():
        return True
    
    try:
        last_check = datetime.fromisoformat(UPDATE_CHECK_FILE.read_text())
        return datetime.now() - last_check > timedelta(days=7)
    except Exception:
        return True


def _check_and_notify():
    """Check for updates and notify if available."""
    try:
        import requests
        
        # Try with GITHUB_TOKEN if available (for private repos)
        import os
        headers = {}
        token = os.environ.get("GITHUB_TOKEN")
        if token:
            headers["Authorization"] = f"token {token}"
        
        response = requests.get(
            "https://api.github.com/repos/renatocaliari/agent-sync/releases/latest",
            headers=headers,
            timeout=3,  # Fast timeout
        )
        
        # If 404, repo might be private or no releases yet
        if response.status_code == 404:
            return
        
        response.raise_for_status()
        
        latest = response.json()["tag_name"].lstrip("v")
        
        if latest > __version__:
            # Save notification so we can show it after command completes
            UPDATE_PENDING_FILE.parent.mkdir(parents=True, exist_ok=True)
            UPDATE_PENDING_FILE.write_text(f"{latest}|{datetime.now().isoformat()}")
        
        # Save last check time
        UPDATE_CHECK_FILE.parent.mkdir(parents=True, exist_ok=True)
        UPDATE_CHECK_FILE.write_text(datetime.now().isoformat())
        
    except Exception:
        pass  # Silently fail (don't annoy user)


def show_pending_update_notification():
    """Show update notification if one is pending."""
    if not UPDATE_PENDING_FILE.exists():
        return
    
    try:
        latest, timestamp = UPDATE_PENDING_FILE.read_text().split("|")
        console.print(f"\n[dim]✨ Update available: v{latest} (Run 'agent-sync update' to install)[/dim]\n")
        
        # Clear notification
        UPDATE_PENDING_FILE.unlink()
    except Exception:
        pass  # Silently fail


class ExtendedHelpGroup(click.Group):
    """Custom Click group to show subcommand options and sub-subcommands in the main help."""
    
    def format_commands(self, ctx, formatter):
        commands = []
        for subcommand in self.list_commands(ctx):
            cmd = self.get_command(ctx, subcommand)
            if cmd is None or cmd.hidden:
                continue
            
            help_text = cmd.get_short_help_str()
            
            if isinstance(cmd, click.Group):
                # For groups, list their subcommands and their options
                sub_items = []
                for sub_sub_name in cmd.list_commands(ctx):
                    sub_sub_cmd = cmd.get_command(ctx, sub_sub_name)
                    if sub_sub_cmd:
                        sub_opts = [p.opts[0] for p in sub_sub_cmd.params if isinstance(p, click.Option)]
                        if sub_opts:
                            sub_items.append(f"{sub_sub_name} [{', '.join(sub_opts)}]")
                        else:
                            sub_items.append(sub_sub_name)
                if sub_items:
                    help_text += f" ({', '.join(sub_items)})"
            else:
                # For regular commands, just list their options
                opts = [p.opts[0] for p in cmd.params if isinstance(p, click.Option)]
                if opts:
                    help_text += f" [{', '.join(opts)}]"
            
            commands.append((subcommand, help_text))

        if commands:
            with formatter.section("Commands"):
                formatter.write_dl(commands)


@click.group(cls=ExtendedHelpGroup)
@click.version_option(version=__version__, prog_name="agent-sync")
def main():
    """
    🔄 agent-sync - Sync configs and skills across multiple AI agents.
    
    Supported agents: opencode, claude-code, gemini-cli, pi.dev, qwen-code
    """
    pass


@main.command()
@click.option("--name", help="Repository name (skips wizard if provided)")
@click.option("--private/--public", default=True, help="Make repository private")
@click.option("--agents", multiple=True, help="Agents to sync (skips wizard if provided)")
@click.option("--no-wizard", is_flag=True, help="Skip interactive wizard")
@click.option("--force", is_flag=True, help="Force initialization even if already configured")
def init(name: Optional[str], private: bool, agents: tuple[str, ...], no_wizard: bool, force: bool):
    """Initialize a new sync repository (first machine).
    
    Runs the setup wizard and creates a new GitHub repository.
    
    \b
    Examples:
      # Interactive wizard (creates new repo)
      agent-sync init
      
      # Create specific repo name (non-interactive)
      agent-sync init --name my-configs --private
      
      # Force re-initialize (overwrites existing config)
      agent-sync init --name new-configs --force
    
    \b
    ⚠️ SECURITY:
      - Always use PRIVATE repositories for configs
      - Configs may contain API keys and tokens
      - GitHub private repos are FREE for personal use
    """
    from .setup import run_setup_wizard

    # Check if config already exists
    config = Config()
    if config.repo_url and not force:
        console.print("\n[yellow]⚠ Already configured![/yellow]")
        console.print(f"   Repository: {config.repo_url}")
        console.print("\n💡 Options:")
        console.print("   - Use [green]agent-sync config repo[/green] to view/change repository")
        console.print("   - Use [green]agent-sync setup[/green] to reconfigure agents")
        console.print("   - Use [green]agent-sync init --force[/green] to overwrite existing config\n")
        return

    if config.repo_url and force:
        console.print("\n[yellow]⚠ Forcing re-initialization![/yellow]")
        console.print(f"   Existing repository: {config.repo_url}")
        console.print("   This will overwrite your local configuration.\n")

    # Run wizard if not provided via CLI args
    if not name and not no_wizard:
        console.print("\n[bold]Running setup wizard...[/bold]\n")
        repo_config = run_setup_wizard()

        if not repo_config:
            console.print("\n[yellow]Setup cancelled[/yellow]")
            raise click.Abort()

        name = repo_config["name"]
        private = repo_config["private"]
        agents = repo_config["agents"]

    if not name:
        console.print("[red]✗ Repository name is required[/red]")
        console.print("\n💡 Provide a name with --name or use the wizard")
        console.print("   Example: [green]agent-sync init --name my-configs[/green]\n")
        raise click.Abort()

    console.print(f"\n🚀 Initializing sync repository: {name}")

    sync_manager = SyncManager(config)

    try:
        repo_url = sync_manager.init_repo(name=name, private=private, agents=agents)
        console.print(f"\n✅ Repository created: {repo_url}")
        console.print("\n📝 Next steps:")
        console.print("  1. Run 'agent-sync push' to upload your configs")
        console.print("  2. On other machines, run 'agent-sync link <repo-url>'")
    except Exception as e:
        console.print(f"\n❌ Error: {e}", style="red")
        raise click.Abort()


@main.command()
def setup():
    """Run the interactive setup wizard to configure or reconfigure.
    
    This can be used:
    - On first time setup
    - To add/remove agents
    - To change sync options
    - To reconfigure repository settings
    """
    from .setup import run_setup_wizard
    
    config = Config()
    
    if config.repo_url:
        console.print("\n[yellow]⚠ You already have an existing configuration![/yellow]")
        console.print(f"   Repository: {config.repo_url}")
        console.print("\nThis will [bold]overwrite[/bold] your current configuration.")
        console.print()
        
        if not Confirm.ask("Continue?", default=False):
            console.print("\n[yellow]Setup cancelled[/yellow]")
            return
        
        console.print("\n[bold]🔄 Reconfiguring Agent Sync[/bold]\n")
    else:
        console.print("\n[bold]🔄 Agent Sync Setup Wizard[/bold]\n")
    
    repo_config = run_setup_wizard()
    
    if repo_config:
        console.print("\n[green]✓ Setup complete![/green]")
        
        if config.repo_url:
            console.print("\n💡 Your repository URL is still the same.")
            console.print("   Run 'agent-sync push' to sync new configuration")
        else:
            console.print("\n💡 Run 'agent-sync init' to create a new repository")
            console.print("   Or 'agent-sync link <url>' to connect to existing one")
    else:
        console.print("\n[yellow]Setup cancelled[/yellow]")


@main.group(cls=ExtendedHelpGroup)
def config():
    """Manage configuration (view, edit, reset)."""
    pass


@config.command()
def show():
    """Show current configuration."""
    from rich.panel import Panel
    
    config = Config()
    
    console.print("\n[bold]📋 Current Configuration[/bold]\n")
    
    if not config.repo_url:
        console.print("[yellow]⚠ Not configured yet. Run 'agent-sync setup'[/yellow]\n")
        return
    
    # Show repo info
    console.print(Panel(f"[cyan]Repository:[/cyan] {config.repo_url}", border_style="blue"))
    console.print()
    
    # Show agents
    console.print("[bold]Enabled Agents:[/bold]")
    for agent_name in config.agents:
        if config.is_agent_enabled(agent_name):
            sync_opts = config.get_sync_options(agent_name)
            configs = "configs" if sync_opts.get("configs") else ""
            sync_str = ", ".join(filter(None, [configs])) or "skills only"
            console.print(f"  ✓ {agent_name}: {sync_str}")
        else:
            console.print(f"  ✗ {agent_name} [dim](disabled)[/dim]")
    console.print()

    # Show config file path
    console.print(f"[dim]Config file: {config.config_path}[/dim]\n")


@config.command()
@click.argument("repo_url", required=False)
@click.option("--remove", is_flag=True, help="Remove repository configuration")
def repo(repo_url: Optional[str], remove: bool):
    """View or set the GitHub repository URL.
    
    \b
    Examples:
      # View current repository
      agent-sync config repo
      
      # Set repository URL
      agent-sync config repo https://github.com/user/repo.git
      
      # Remove repository configuration
      agent-sync config repo --remove
    """
    config = Config()

    if remove:
        if not config.repo_url:
            console.print("\n[yellow]No repository configured[/yellow]\n")
            return
        
        old_url = config.repo_url
        config.repo_url = None
        console.print(f"\n[green]✓ Repository configuration removed[/green]")
        console.print(f"  Was: {old_url}")
        console.print("\n[dim]Your local files are still intact.[/dim]")
        console.print("[dim]Run 'agent-sync config repo <url>' to configure again.[/dim]\n")
        return

    if repo_url:
        # Set repository URL
        if not repo_url.startswith("https://github.com/"):
            console.print(f"\n[red]✗ Invalid repository URL[/red]")
            console.print(f"   Expected: https://github.com/user/repo.git")
            console.print(f"   Got: {repo_url}\n")
            return
        
        config.repo_url = repo_url
        console.print(f"\n[green]✓ Repository configured[/green]")
        console.print(f"  URL: {repo_url}")
        console.print("\n💡 Run 'agent-sync pull' to download configs")
        console.print("   Run 'agent-sync push' to upload configs\n")
        return

    # View current repository
    if not config.repo_url:
        console.print("\n[yellow]⚠ Not configured yet[/yellow]\n")
        console.print("Configure a repository with:")
        console.print("  [green]agent-sync config repo https://github.com/user/repo.git[/green]\n")
        console.print("Or create a new one with:")
        console.print("  [green]agent-sync init --name my-configs[/green]\n")
        return

    console.print(f"\n[cyan]📦 Repository:[/cyan] {config.repo_url}\n")
    console.print("[dim]Use 'agent-sync config repo --remove' to disconnect.[/dim]\n")


@config.command()
@click.option("--agent", help="Specific agent to configure")
def edit(agent: Optional[str]):
    """Open configuration file in editor."""
    import subprocess
    
    config = Config()
    
    if not config.config_path.exists():
        config.generate_default()
    
    # Try to open with default editor
    editor = os.environ.get("EDITOR", "nano")
    
    try:
        subprocess.run([editor, str(config.config_path)])
        console.print("\n[green]✓ Configuration saved[/green]\n")
    except FileNotFoundError:
        console.print(f"\n[yellow]Editor '{editor}' not found[/yellow]")
        console.print(f"Edit manually: {config.config_path}\n")


@config.command()
@click.confirmation_option(prompt="Are you sure you want to reset configuration?")
def reset():
    """Reset configuration to defaults (keeps repo linked)."""
    from rich.prompt import Confirm
    
    config = Config()
    
    if not config.repo_url:
        console.print("\n[yellow]No configuration to reset[/yellow]\n")
        return
    
    repo_url = config.repo_url
    
    # Generate fresh default config
    config.generate_default()
    config.repo_url = repo_url
    
    console.print("\n[green]✓ Configuration reset to defaults[/green]")
    console.print(f"  Repository: {repo_url}")
    console.print("\n💡 Run 'agent-sync setup' to reconfigure\n")


@main.group(cls=ExtendedHelpGroup)
def skills():
    """Manage global skills."""
    pass


@skills.command("list")
def list_skills():
    """List all centralized skills."""
    from rich.table import Table
    from rich import box
    
    skills_dir = Path.home() / ".agents" / "skills"
    
    if not skills_dir.exists():
        console.print("\n[yellow]No skills directory found.[/yellow]")
        console.print("Run [green]`agent-sync skills centralize`[/green] to centralize skills.\n")
        return
    
    skills = []
    for item in skills_dir.iterdir():
        if item.is_dir() and (item / "SKILL.md").exists():
            skills.append({
                "name": item.name,
                "path": str(item),
                "valid": True
            })
        elif item.is_file() and item.suffix in [".md", ".py", ".sh"]:
            skills.append({
                "name": item.name,
                "path": str(item),
                "valid": False
            })
    
    if not skills:
        console.print("\n[yellow]No skills found in ~/.agents/skills/[/yellow]\n")
        return
    
    console.print(f"\n[bold]📚 Centralized Skills ({len(skills)})[/bold]\n")
    
    table = Table(box=box.SIMPLE)
    table.add_column("Status", style="green")
    table.add_column("Skill Name", style="cyan")
    table.add_column("Path", style="dim")
    
    for skill in sorted(skills, key=lambda s: s["name"]):
        icon = "✓" if skill["valid"] else "⚠"
        status = "Valid" if skill["valid"] else "File (no SKILL.md)"
        table.add_row(icon, skill["name"], skill["path"])
    
    console.print(table)
    console.print()


@skills.command()
@click.option("--copy", is_flag=True, help="Copy instead of moving skills")
@click.option("--push", is_flag=True, help="Automatically push to GitHub after centralizing")
@click.option("--distribute", is_flag=True, help="After centralizing, copy all skills to all agent directories (for backup or testing)")
def centralize(copy: bool, push: bool, distribute: bool):
    """Centralize skills from all agents to ~/.agents/skills/.
    
    This command scans all agent directories for existing skills and centralizes
    them to the global ~/.agents/skills/ directory (single source of truth).
    
    \b
    Examples:
      # Move skills (default - removes from agent directories)
      agent-sync skills centralize
      
      # Copy skills (keeps originals in agent directories)
      agent-sync skills centralize --copy
      
      # Move skills and push to GitHub automatically
      agent-sync skills centralize --push
      
      # Copy skills and push to GitHub
      agent-sync skills centralize --copy --push
      
      # Centralize AND copy to all agent directories (backup/testing)
      agent-sync skills centralize --distribute
    
    \b
    What happens:
      1. Scans all agent directories for skills
      2. Detects conflicts (same skill name in multiple agents)
      3. Resolves conflicts by renaming with agent prefix
      4. Moves/copies skills to ~/.agents/skills/
      5. Optionally pushes to GitHub
      6. With --distribute: copies all skills to all agent directories
    
    \b
    After centralizing:
      - Skills live in ~/.agents/skills/ (source of truth)
      - Agents use symlinks or config to access global skills
      - Original skill directories may be removed (if --copy not used)
      - With --distribute: all agents have local copies for backup/testing
    """
    from .skills import SkillsManager
    from rich.prompt import Confirm
    
    move = not copy
    action = "Copying" if copy else "Moving"
    
    console.print(f"\n[bold]📁 {action} Skills[/bold]\n")
    
    skills_mgr = SkillsManager()
    stats = skills_mgr.centralize(move=move)
    
    # Show final reassurance
    console.print("[bold green]🎉 Centralization Complete![/bold green]\n")
    console.print("What happened:\n")
    
    if move:
        console.print(f"  ✓ [green]{stats['moved']} skills moved[/green] to ~/.agents/skills/")
        console.print("    [dim]Original files removed from agent directories[/dim]\n")
    else:
        console.print(f"  ✓ [green]{stats['copied']} skills copied[/green] to ~/.agents/skills/")
        console.print("    [dim]Original files kept in agent directories[/dim]\n")
    
    if stats['symlinks_removed'] > 0:
        console.print(f"  ✓ [yellow]{stats['symlinks_removed']} user symlinks removed[/yellow]")
        console.print("    [dim]Cleaning up manual symlinks from agent directories[/dim]\n")
    
    if stats['conflicts_resolved'] > 0:
        console.print(f"  ✓ [yellow]{stats['conflicts_resolved']} conflicts resolved[/yellow]")
        console.print("    [dim]Duplicate skill names renamed with agent prefix[/dim]\n")
    
    console.print("Where are my skills now?\n")
    console.print(f"  [bold cyan]~/.agents/skills/[/bold cyan] [dim]← Single source of truth[/dim]\n")
    console.print("All your skills are now in one place and will be synced to GitHub.\n")

    if move:
        console.print("[dim]Note: Agent directories now use symlinks or config to read from ~/.agents/skills/[/dim]\n")

    # Optional: distribute skills to all agent directories
    if distribute:
        console.print("\n[bold]📤 Distributing Skills to All Agents[/bold]\n")
        console.print("[yellow]⚠ This will copy ALL skills to ALL agent directories.[/yellow]\n")
        console.print("Use this for:")
        console.print("  • Backup: local copies in each agent directory")
        console.print("  • Testing: verify agents read from local vs global")
        console.print("  • Debug: troubleshoot symlink/config issues\n")

        if Confirm.ask("Continue with distribution?", default=True):
            dist_stats = skills_mgr.distribute_to_all_agents()
            console.print(f"\n[green]✓ Distributed {dist_stats['distributed']} skills to {dist_stats['agents_configured']} agents[/green]\n")
            console.print("[dim]Note: Native agents (pi.dev, qwen-code) will still prefer ~/.agents/skills/[/dim]\n")
        else:
            console.print("\n[yellow]⚠ Distribution skipped[/yellow]\n")

    # Ask if user wants to push
    should_push = push

    if not should_push:
        should_push = Confirm.ask(
            "\n[bold]Would you like to push these changes to GitHub now?[/bold]",
            default=True,
        )
    
    if should_push:
        console.print("\n[bold]📤 Pushing to GitHub...[/bold]\n")
        
        from .sync import SyncManager
        from .config import Config
        
        config = Config()
        
        if not config.repo_url:
            console.print("[yellow]⚠ No repository configured yet.[/yellow]")
            console.print("Run [green]agent-sync init[/green] to create a repository first.\n")
        else:
            try:
                sync_manager = SyncManager(config)
                pushed = sync_manager.push(message="chore: centralize skills")
                
                if pushed:
                    console.print(f"\n[green]✓ Pushed {len(pushed)} files to GitHub[/green]\n")
                    console.print("💡 On other machines, run [green]agent-sync pull[/green]\n")
                else:
                    console.print("\n[yellow]✓ Nothing to push (already up to date)[/yellow]\n")
            except Exception as e:
                console.print(f"\n[red]✗ Push failed: {e}[/red]\n")
                console.print("[dim]You can run [green]agent-sync push[/green] manually later.[/dim]\n")
    else:
        console.print("💡 Run [green]agent-sync push[/green] to sync to GitHub\n")


@skills.command()
@click.option("--repo", "repo_url", help="GitHub repository URL for publishing skills (e.g., https://github.com/user/my-skills)")
@click.option("--dry-run", is_flag=True, help="Show what would be published without actually publishing")
@click.option("--interactive", "-i", is_flag=True, help="Interactive TUI to select which skills to publish")
def publish(repo_url: Optional[str], dry_run: bool, interactive: bool):
    """Publish selected skills to a public GitHub repository.
    
    Use --interactive to select which skills to publish via TUI.
    """
    from .publish import publish_skills
    success = publish_skills(repo_url=repo_url, dry_run=dry_run, interactive=interactive)
    if not success:
        raise click.Abort()


@main.command()
@click.argument("repo_url")
def link(repo_url: str):
    """Link to an existing sync repository (additional machines)."""
    console.print(f"\n🔗 Linking to repository: {repo_url}")
    
    config = Config()
    sync_manager = SyncManager(config)
    
    try:
        sync_manager.link_repo(repo_url)
        console.print(f"\n✅ Successfully linked to repository")
        console.print("\n📥 Run 'agent-sync pull' to download configs")
    except Exception as e:
        console.print(f"\n❌ Error: {e}", style="red")
        raise click.Abort()


@main.command()
@click.option("--force", is_flag=True, help="Force pull even with local changes")
@click.option("--skills-only", is_flag=True, help="Pull only skills (not configs)")
@click.option("--configs-only", is_flag=True, help="Pull only configs (not skills)")
def pull(force: bool, skills_only: bool, configs_only: bool):
    """Fetch and apply remote configuration.
    
    \b
    Examples:
      # Pull everything (default)
      agent-sync pull
      
      # Pull only skills
      agent-sync pull --skills-only
      
      # Pull only configs
      agent-sync pull --configs-only
      
      # Force pull (overwrite local changes)
      agent-sync pull --force
    """
    console.print("\n📥 Pulling remote configuration...")

    # Check for updates asynchronously (once per week)
    check_for_updates_async()

    config = Config()
    sync_manager = SyncManager(config)

    try:
        changes = sync_manager.pull(force=force, skills_only=skills_only, configs_only=configs_only)
        if changes:
            console.print(f"\n✅ Applied {len(changes)} changes:")
            for change in changes:
                console.print(f"  • {change}", style="green")
        else:
            console.print("\n✓ Already up to date", style="yellow")
    except Exception as e:
        console.print(f"\n❌ Error: {e}", style="red")
        raise click.Abort()

    # Show update notification if available
    show_pending_update_notification()


@main.command()
@click.option("-m", "--message", default="chore: sync config updates", help="Commit message")
@click.option("--skills-only", is_flag=True, help="Push only skills (not configs)")
@click.option("--configs-only", is_flag=True, help="Push only configs (not skills)")
def push(message: str, skills_only: bool, configs_only: bool):
    """Commit and push local changes.
    
    \b
    Examples:
      # Push everything (default)
      agent-sync push
      
      # Push only skills
      agent-sync push --skills-only
      
      # Push only configs
      agent-sync push --configs-only
      
      # Push with custom message
      agent-sync push -m "feat: add new skill"
    """
    console.print("\n📤 Pushing local changes...")

    # Check for updates asynchronously (once per week)
    check_for_updates_async()

    config = Config()
    sync_manager = SyncManager(config)

    try:
        pushed = sync_manager.push(message=message, skills_only=skills_only, configs_only=configs_only)
        if pushed:
            console.print(f"\n✅ Pushed {len(pushed)} files:")
            for file in pushed:
                console.print(f"  • {file}", style="green")
        else:
            console.print("\n✓ Nothing to push", style="yellow")
    except Exception as e:
        console.print(f"\n❌ Error: {e}", style="red")
        raise click.Abort()

    # Show update notification if available
    show_pending_update_notification()


@main.command()
def status():
    """Show sync status and last sync times."""
    console.print("\n📊 Sync Status\n")
    
    config = Config()
    sync_manager = SyncManager(config)
    
    try:
        status_info = sync_manager.get_status()
        
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Agent", style="cyan")
        table.add_column("Status", style="green")
        table.add_column("Last Sync", style="yellow")
        table.add_column("Changes", style="red")
        
        for agent, info in status_info.items():
            table.add_row(
                agent,
                info["status"],
                info["last_sync"],
                info["changes"] or "-",
            )
        
        console.print(table)
        
        if config.repo_url:
            console.print(f"\n🔗 Repository: {config.repo_url}")
    except Exception as e:
        console.print(f"\n❌ Error: {e}", style="red")
        raise click.Abort()


@main.group(cls=ExtendedHelpGroup)
def secrets():
    """Manage secrets and environment variables.
    
    Note: agent-sync does not scrub secrets. Config files are synced as-is.
    ALWAYS use a private repository.
    """
    pass


@main.command()
def update():
    """Check for available updates and install them."""
    import requests
    import os
    import subprocess
    from rich.prompt import Confirm
    
    console.print("[bold]🔍 Checking for updates...[/bold]\n")
    
    current = __version__
    
    try:
        # Try with GITHUB_TOKEN if available (for private repos)
        headers = {}
        token = os.environ.get("GITHUB_TOKEN")
        if token:
            headers["Authorization"] = f"token {token}"
        
        response = requests.get(
            "https://api.github.com/repos/renatocaliari/agent-sync/releases/latest",
            headers=headers,
            timeout=5,
        )
        
        # If 404, repo is private or no releases yet
        if response.status_code == 404:
            console.print(f"[dim]Current version: v{current}[/dim]")
            console.print("[yellow]⚠ No official releases found on GitHub[/yellow]\n")
            return
        
        response.raise_for_status()
        
        latest_data = response.json()
        latest = latest_data["tag_name"].lstrip("v")
        
        if latest > current:
            console.print(f"✨ [green]Update available:[/green] [bold]v{latest}[/bold] (Current: v{current})")
            
            if Confirm.ask("\nDo you want to update now?", default=True):
                console.print("\n🚀 [bold]Updating agent-sync...[/bold]")
                
                # Check if installed via pipx or pip
                is_pipx = "pipx" in subprocess.check_output(["which", "agent-sync"]).decode()
                
                cmd = []
                if is_pipx:
                    cmd = ["pipx", "upgrade", "agent-sync"]
                else:
                    cmd = ["python3", "-m", "pip", "install", "--upgrade", "git+https://github.com/renatocaliari/agent-sync.git"]
                
                try:
                    subprocess.run(cmd, check=True)
                    console.print("\n[bold green]✅ agent-sync updated successfully![/bold green]")
                except subprocess.CalledProcessError:
                    console.print("\n[red]✗ Update failed.[/red] Please try manually:")
                    console.print(f"   {' '.join(cmd)}")
        else:
            console.print(f"✓ [green]Up to date:[/green] [bold]v{current}[/bold]\n")
            
    except requests.exceptions.RequestException:
        console.print(f"[dim]Current version: v{current}[/dim]")
        console.print("[yellow]⚠ Could not check for updates (offline?)\n[/yellow]")
    except Exception as e:
        console.print(f"[dim]Current version: v{current}[/dim]")
        console.print(f"[yellow]⚠ Error checking updates: {e}\n[/yellow]")


@main.command()
def version():
    """Show version information."""
    console.print(f"\n[bold]agent-sync[/bold] v{__version__}\n")


@main.command()
def agents():
    """List supported agents and their status."""
    console.print("\n🤖 Supported Agents\n")
    
    from .agents import get_all_agents
    
    agents = get_all_agents()
    
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Agent", style="cyan")
    table.add_column("Status", style="yellow")
    table.add_column("Sync", style="magenta")
    table.add_column("Skills Method", style="blue")
    table.add_column("Config Path", style="green")
    
    config = Config()
    
    for agent in agents:
        enabled = config.is_agent_enabled(agent.name)
        status = "✓" if agent.is_available() else "✗"
        sync_status = "🟢 ON" if enabled else "🔴 OFF"
        
        # Get actual method from user config or default to agent's registry method
        method = config.get_skills_method(agent.name) or agent.method
        
        config_path_str = str(agent.config_path) if agent.config_path else "-"
        
        table.add_row(
            agent.name,
            status,
            sync_status,
            method,
            config_path_str,
        )
    
    console.print(table)
    console.print("\n💡 Use 'agent-sync enable <agent>' or 'agent-sync disable <agent>' to toggle sync")
    console.print("\n🔧 [bold]How to customize skills method:[/bold]")
    console.print("  Edit your config with [green]agent-sync config edit[/green] and add:")
    console.print("  [dim]agents_config:[/dim]")
    console.print("  [dim]  claude-code:[/dim]")
    console.print("  [dim]    skills_method: copy  # Options: native, config, copy[/dim]\n")


@main.command()
@click.option("--agent", multiple=True, help="Specific agents to include")
def generate_config(agent: tuple[str, ...]):
    """Generate initial configuration file."""
    console.print("\n⚙️  Generating configuration...\n")

    config = Config()
    target_agents = agent if agent else None

    try:
        config_path = config.generate_default(target_agents)
        console.print(f"✅ Config generated: {config_path}", style="green")
        console.print("\n📝 Edit ~/.config/agent-sync/config.yaml to customize")
    except Exception as e:
        console.print(f"\n❌ Error: {e}", style="red")
        raise click.Abort()


@main.command()
@click.argument("agent_name")
def enable(agent_name: str):
    """Enable sync for a specific agent."""
    console.print(f"\n✅ Enabling sync for: {agent_name}")
    
    from .agents import get_agent
    
    agent = get_agent(agent_name)
    if not agent:
        console.print(f"❌ Unknown agent: {agent_name}", style="red")
        console.print("\nAvailable agents:", style="yellow")
        from .agents import get_all_agents
        for a in get_all_agents():
            console.print(f"  • {a.name}")
        raise click.Abort()
    
    try:
        config = Config()
        config.enable_agent(agent_name)
        agent.enable()
        console.print(f"✅ Sync enabled for {agent_name}", style="green")
        console.print("\n💡 Run 'agent-sync push' to sync this agent's configs")
    except Exception as e:
        console.print(f"\n❌ Error: {e}", style="red")
        raise click.Abort()


@main.command()
@click.argument("agent_name")
def disable(agent_name: str):
    """Disable sync for a specific agent."""
    console.print(f"\n🚫 Disabling sync for: {agent_name}")
    
    from .agents import get_agent
    
    agent = get_agent(agent_name)
    if not agent:
        console.print(f"❌ Unknown agent: {agent_name}", style="red")
        console.print("\nAvailable agents:", style="yellow")
        from .agents import get_all_agents
        for a in get_all_agents():
            console.print(f"  • {a.name}")
        raise click.Abort()
    
    try:
        config = Config()
        config.disable_agent(agent_name)
        agent.disable()
        console.print(f"✅ Sync disabled for {agent_name}", style="green")
        console.print("\n💡 This agent's configs will no longer be synced")
    except Exception as e:
        console.print(f"\n❌ Error: {e}", style="red")
        raise click.Abort()


if __name__ == "__main__":
    main()
