"""Main CLI entry point for agent-sync."""

import os
import click
from rich.console import Console
from rich.table import Table
from typing import Optional

from . import __version__
from .sync import SyncManager
from .config import Config
from .secrets import SecretsManager

console = Console()


@click.group()
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
def init(name: Optional[str], private: bool, agents: tuple[str, ...], no_wizard: bool):
    """Initialize a new sync repository (first machine)."""
    from .setup import run_setup_wizard
    
    # Check if config already exists
    config = Config()
    if config.repo_url:
        console.print("\n[yellow]⚠ Already configured![/yellow]")
        console.print(f"   Repository: {config.repo_url}")
        console.print("\n💡 Use 'agent-sync setup' to reconfigure")
        return
    
    # Run wizard if not provided via CLI args
    if not name and not no_wizard:
        console.print("\n[bold]No configuration found. Running setup wizard...[/bold]\n")
        repo_config = run_setup_wizard()
        
        if not repo_config:
            console.print("\n[yellow]Setup cancelled[/yellow]")
            raise click.Abort()
        
        name = repo_config["name"]
        private = repo_config["private"]
        agents = repo_config["agents"]
    
    if not name:
        console.print("[red]✗ Repository name is required[/red]")
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


@main.group()
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
    
    # Show secrets
    console.print("[bold]Secrets:[/bold]")
    console.print(f"  Include secrets: {'⚠ Yes' if config.include_secrets else 'No'}")
    console.print(f"  Include MCP: {'⚠ Yes' if config.include_mcp_secrets else 'No'}")
    console.print()
    
    # Show config file path
    console.print(f"[dim]Config file: {config.config_path}[/dim]\n")


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


@main.group()
def skills():
    """Manage global skills."""
    pass


@skills.command()
def centralize():
    """Centralize skills from all agents to ~/.agents/skills/."""
    from .skills import SkillsManager
    
    console.print("\n[bold]📁 Centralizing Skills[/bold]\n")
    
    skills_mgr = SkillsManager()
    skills_mgr.centralize()
    
    console.print("\n[green]✓ Skills centralized to ~/.agents/skills/[/green]\n")
    console.print("💡 Run 'agent-sync push' to sync to GitHub\n")


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
def pull(force: bool):
    """Fetch and apply remote configuration."""
    console.print("\n📥 Pulling remote configuration...")
    
    config = Config()
    sync_manager = SyncManager(config)
    
    try:
        changes = sync_manager.pull(force=force)
        if changes:
            console.print(f"\n✅ Applied {len(changes)} changes:")
            for change in changes:
                console.print(f"  • {change}", style="green")
        else:
            console.print("\n✓ Already up to date", style="yellow")
    except Exception as e:
        console.print(f"\n❌ Error: {e}", style="red")
        raise click.Abort()


@main.command()
@click.option("-m", "--message", default="chore: sync config updates", help="Commit message")
def push(message: str):
    """Commit and push local changes."""
    console.print("\n📤 Pushing local changes...")
    
    config = Config()
    sync_manager = SyncManager(config)
    
    try:
        pushed = sync_manager.push(message=message)
        if pushed:
            console.print(f"\n✅ Pushed {len(pushed)} files:")
            for file in pushed:
                console.print(f"  • {file}", style="green")
        else:
            console.print("\n✓ Nothing to push", style="yellow")
    except Exception as e:
        console.print(f"\n❌ Error: {e}", style="red")
        raise click.Abort()


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


@main.group()
def secrets():
    """Manage secrets and environment variables."""
    pass


@secrets.command()
@click.option("--include-mcp", is_flag=True, help="Include MCP secrets")
def enable(include_mcp: bool):
    """Enable secrets synchronization."""
    console.print("\n🔐 Enabling secrets sync...")
    
    secrets_mgr = SecretsManager()
    try:
        secrets_mgr.enable(include_mcp=include_mcp)
        console.print("\n✅ Secrets sync enabled")
        console.print("\n⚠️  Make sure your repository is PRIVATE!", style="yellow bold")
    except Exception as e:
        console.print(f"\n❌ Error: {e}", style="red")
        raise click.Abort()


@secrets.command()
def disable():
    """Disable secrets synchronization."""
    console.print("\n🔓 Disabling secrets sync...")
    
    secrets_mgr = SecretsManager()
    try:
        secrets_mgr.disable()
        console.print("\n✅ Secrets sync disabled")
    except Exception as e:
        console.print(f"\n❌ Error: {e}", style="red")
        raise click.Abort()


@main.command()
def agents():
    """List supported agents and their status."""
    console.print("\n🤖 Supported Agents\n")
    
    from .agents import get_all_agents
    
    agents = get_all_agents()
    
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Agent", style="cyan")
    table.add_column("Config Path", style="green")
    table.add_column("Skills Path", style="blue")
    table.add_column("Status", style="yellow")
    table.add_column("Sync", style="magenta")
    
    config = Config()
    
    for agent in agents:
        enabled = config.is_agent_enabled(agent.name)
        status = "✓" if agent.is_available() else "✗"
        sync_status = "🟢 ON" if enabled else "🔴 OFF"
        
        config_path_str = str(agent.config_path) if agent.config_path else "-"
        skills_path_str = str(agent.skills_path)
        
        table.add_row(
            agent.name,
            config_path_str,
            skills_path_str,
            status,
            sync_status,
        )
    
    console.print(table)
    console.print("\n💡 Use 'agent-sync enable <agent>' or 'agent-sync disable <agent>' to toggle sync")


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
