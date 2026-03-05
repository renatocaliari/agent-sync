"""Skills publishing to public GitHub repositories.

Publish selected skills to a PUBLIC repository for sharing with the community.
Separate from private agent-sync-configs repository.
"""

import shutil
import subprocess
import tempfile
import json
from pathlib import Path
from typing import Optional, List, Dict, Any, Set

import yaml
from rich.console import Console
from rich.live import Live
from rich.layout import Layout
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich.table import Table
from rich import box
from .config import Config

console = Console()

PUBLISH_CONFIG_PATH = Path.home() / ".config" / "agent-sync" / "publish.yaml"
SKILLS_DIR = Path.home() / ".agents" / "skills"


def get_available_skills() -> list[dict]:
    """Scan for available skills in ~/.agents/skills/."""
    skills_list = []
    if not SKILLS_DIR.exists():
        return []
        
    for item in SKILLS_DIR.iterdir():
        if item.name.startswith("."):
            continue
        
        if item.is_dir() and (item / "SKILL.md").exists():
            skills_list.append({
                "name": item.name,
                "path": item,
                "valid": True
            })
        elif item.is_file() and item.suffix in [".md", ".py", ".sh"]:
            skills_list.append({
                "name": item.name,
                "path": item,
                "valid": False
            })
    return sorted(skills_list, key=lambda x: x["name"])


def render_selection_table(skills: list, selected_names: set) -> Table:
    """Render the TUI selection table."""
    table = Table(box=box.ROUNDED, show_header=True, header_style="bold magenta", expand=True)
    table.add_column("ID", justify="right", style="dim", width=4)
    table.add_column("Pub", justify="center", width=5)
    table.add_column("Skill Name", style="cyan")
    table.add_column("Type", style="dim")

    for i, skill in enumerate(skills, 1):
        is_selected = skill["name"] in selected_names
        status = "[bold green]✓[/bold green]" if is_selected else "[red]○[/red]"
        skill_type = "Full Skill" if skill["valid"] else "Script/MD"
        table.add_row(str(i), status, skill["name"], skill_type)
    
    return table


def interactive_selection(skills: list, initial_selected: set) -> set:
    """TUI for selecting skills to publish."""
    selected = set(initial_selected)
    
    while True:
        console.clear()
        console.print("\n[bold magenta]📤 Select Skills to Publish[/bold magenta]\n")
        
        table = render_selection_table(skills, selected)
        console.print(table)
        
        console.print("\n[bold]Controls:[/]")
        console.print("  • Enter numbers to toggle (e.g. [green]'1,3,5'[/green])")
        console.print("  • Type [cyan]'all'[/cyan] or [cyan]'none'[/cyan]")
        console.print("  • Press [bold white]Enter[/] when done")
        
        choice = Prompt.ask("\nSelection", default="done")
        
        if choice.lower() in ["done", ""]:
            break
        elif choice.lower() == "all":
            selected = {s["name"] for s in skills}
        elif choice.lower() == "none":
            selected = set()
        else:
            try:
                indices = [int(x.strip()) - 1 for x in choice.split(",")]
                for idx in indices:
                    if 0 <= idx < len(skills):
                        name = skills[idx]["name"]
                        if name in selected:
                            selected.remove(name)
                        else:
                            selected.add(name)
            except ValueError:
                pass
                
    return selected


def publish_skills(repo_url: Optional[str] = None, dry_run: bool = False, interactive: bool = False) -> bool:
    """Publish selected skills to a public GitHub repository."""
    config = Config()
    
    # 1. Scan for skills on disk
    available_skills = get_available_skills()
    if not available_skills:
        console.print("\n[yellow]⚠ No skills found in ~/.agents/skills/[/yellow]")
        console.print("Run [green]agent-sync skills centralize[/green] first.\n")
        return False

    available_names = {s["name"] for s in available_skills}

    # 2. Determine initial selection and handle missing skills
    saved_selection = config.published_skills
    
    # Filter out skills that no longer exist on disk
    valid_saved = [name for name in saved_selection if name in available_names]
    if len(valid_saved) != len(saved_selection):
        # Auto-update config if some skills are missing
        config.published_skills = valid_saved
        saved_selection = valid_saved

    # 3. Interactive flow with confirmation of saved config
    selected_names = set()
    
    if interactive:
        if saved_selection:
            # 1. SHOW SUMMARY FIRST (User Request)
            console.print("\n[bold blue]📋 Current Saved Selection[/bold blue]")
            summary_table = Table(box=box.SIMPLE, show_header=False)
            summary_table.add_column("Skill", style="cyan")
            for name in sorted(saved_selection):
                summary_table.add_row(f"  • {name}")
            console.print(summary_table)

            # 2. INTUITIVE MENU (Numbered/Shortcut)
            console.print("\n[bold]What would you like to do?[/]")
            console.print("  [bold green]1[/]. Use this selection [dim](u)[/dim]")
            console.print("  [bold cyan]2[/]. Edit selection [dim](e)[/dim]")
            console.print("  [bold magenta]3[/]. Select ALL available [dim](a)[/dim]")
            
            choice = Prompt.ask("\nChoice", choices=["1", "2", "3", "u", "e", "a"], default="1")
            
            if choice in ["1", "u"]:
                selected_names = set(saved_selection)
            elif choice in ["3", "a"]:
                selected_names = available_names
            else: # 2 or e (edit)
                selected_names = set(saved_selection)
                # This will fall through to the selection loop below
        else:
            # No saved config, ask if publish all or select
            console.print("\n[bold]Publishing Mode[/]")
            console.print("  [bold green]1[/]. Publish ALL available [dim](a)[/dim]")
            console.print("  [bold cyan]2[/]. Select specific skills [dim](s)[/dim]")
            
            mode = Prompt.ask("\nChoice", choices=["1", "2", "a", "s"], default="1")
            if mode in ["1", "a"]:
                selected_names = available_names
            # If select (2/s), selected_names remains empty and loop starts

        # Selection Loop (if edit mode or manual select)
        if not selected_names or (saved_selection and choice in ["2", "e"]):
            while True:
                selected_names = interactive_selection(available_skills, selected_names)
                
                if not selected_names:
                    if Confirm.ask("\n[yellow]No skills selected. Cancel publishing?[/yellow]", default=True):
                        return False
                    continue
                
                # Show summary for confirmation
                console.clear()
                console.print("\n[bold green]📋 Selection Summary[/bold green]\n")
                summary_table = Table(box=box.SIMPLE)
                summary_table.add_column("Skill Name", style="cyan")
                for name in sorted(list(selected_names)):
                    summary_table.add_row(name)
                console.print(summary_table)
                
                if Confirm.ask("\n[bold]Confirm this selection?[/]", default=True):
                    # Save selection to config
                    config.published_skills = list(selected_names)
                    break
    else:
        # Non-interactive: use saved selection or all valid skills
        selected_names = set(saved_selection) if saved_selection else {s["name"] for s in available_skills if s["valid"]}
    
    # Final list of skill objects to publish
    selected_skills = [s for s in available_skills if s["name"] in selected_names]
    
    if not selected_skills:
        console.print("\n[yellow]⚠ No skills selected for publishing[/yellow]\n")
        return False

    # 4. Security & Repo Logic (Existing flow)
    console.print(Panel(
        "[bold yellow]⚠️  SECURITY WARNING[/bold yellow]\n\n"
        "You are about to publish skills to a [bold]PUBLIC[/] repository.\n\n"
        "What WILL be published:\n"
        "  ✓ SKILL.md files (skill definitions)\n"
        "  ✓ .md, .py, .sh files (skill scripts)\n"
        "  ✓ references/, templates/, scripts/ directories\n\n"
        "What will [bold red]NEVER[/bold red] be published:\n"
        "  ✗ Any config files (settings.json, config.yaml, etc.)\n"
        "  ✗ Any files containing 'auth', 'token', 'key', 'secret' in name\n"
        "  ✗ .env files\n"
        "  ✗ Your private agent-sync-configs repository",
        border_style="yellow",
    ))

    # Load or create publish config (for repo_url)
    publish_config = {}
    if PUBLISH_CONFIG_PATH.exists():
        try:
            publish_config = yaml.safe_load(PUBLISH_CONFIG_PATH.read_text()) or {}
        except Exception: pass
    
    repo_url = repo_url or publish_config.get("repo_url")
    if not repo_url:
        repo_url = Prompt.ask("\n[bold]Enter GitHub repository URL for publishing[/]")
        if not repo_url or not repo_url.startswith("https://github.com/"):
            console.print("\n[red]✗ Invalid repository URL[/red]\n")
            return False
        
        PUBLISH_CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
        publish_config["repo_url"] = repo_url
        PUBLISH_CONFIG_PATH.write_text(yaml.dump(publish_config))

    # Repo validation via gh CLI
    repo_name = repo_url.replace("https://github.com/", "").replace(".git", "")
    try:
        res = subprocess.run(["gh", "api", f"repos/{repo_name}"], capture_output=True, text=True, timeout=5)
        if res.returncode == 0:
            is_private = json.loads(res.stdout).get("private", False)
            if is_private:
                console.print(f"\n[yellow]⚠️  Warning: Repository {repo_name} is PRIVATE.[/yellow]")
            else:
                console.print(f"\n[green]✓ Repository {repo_name} is PUBLIC.[/green]")
    except Exception: pass

    if dry_run:
        console.print(f"\n[blue]🔍 DRY RUN: Would publish {len(selected_skills)} skills to {repo_url}[/blue]\n")
        return True

    if not Confirm.ask("\n[bold red]Confirm publishing to GitHub?[/bold red]", default=True):
        console.print("\n[yellow]Publish cancelled[/yellow]\n")
        return False

    # 5. Execute Publishing
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        skills_tmp_dir = tmp_path / "skills"
        skills_tmp_dir.mkdir(parents=True, exist_ok=True)
        
        for skill in selected_skills:
            src, dst = skill["path"], skills_tmp_dir / skill["name"]
            if src.is_dir(): shutil.copytree(src, dst)
            else: shutil.copy2(src, dst)
        
        (tmp_path / "README.md").write_text(generate_readme(selected_skills, repo_url))
        (tmp_path / ".gitignore").write_text("*.json\n*.yaml\n*.yml\n.env\n*auth*\n*token*\n*key*\n*secret*\n*credentials*\n")
        
        console.print(f"\n[bold]📤 Publishing {len(selected_skills)} skills...[/]")
        
        try:
            # Ensure repo exists
            subprocess.run(["gh", "api", f"repos/{repo_name}"], capture_output=True, check=False)
            # Git ops
            subprocess.run(["git", "init"], cwd=tmp_path, capture_output=True, check=True)
            subprocess.run(["git", "add", "."], cwd=tmp_path, capture_output=True, check=True)
            subprocess.run(["git", "commit", "-m", f"feat: publish {len(selected_skills)} skills"], cwd=tmp_path, capture_output=True, check=True)
            subprocess.run(["git", "branch", "-M", "main"], cwd=tmp_path, capture_output=True, check=True)
            subprocess.run(["git", "remote", "add", "origin", repo_url], cwd=tmp_path, capture_output=True, check=True)
            subprocess.run(["git", "push", "-u", "origin", "main", "--force"], cwd=tmp_path, capture_output=True, check=True)
            
            console.print(f"\n[green]✓ Successfully published to {repo_url}![/green]")
            console.print(f"💡 Others can install with: [bold]npx skills add {repo_name}[/]\n")
            return True
        except Exception as e:
            console.print(f"\n[red]✗ Failed to publish: {e}[/red]\n")
            return False


def strip_frontmatter(content: str) -> str:
    """Remove YAML frontmatter, tags, and excessive titles from markdown content."""
    import re
    
    # 1. Remove YAML frontmatter (--- ... ---) including variations with different spacing
    content = re.sub(r'^---\s*\n.*?\n---\s*\n', '', content, flags=re.DOTALL)
    
    # 2. Specifically remove common frontmatter-like fields if they appear at the top
    # (Sometimes LLMs or users might write them without the --- markers)
    content = re.sub(r'^(name|description|tags|version|author):.*?\n', '', content, flags=re.MULTILINE | re.IGNORECASE)
    
    # 3. Convert titles to plain text or smaller headers to avoid huge titles
    lines = content.split('\n')
    cleaned_lines = []
    
    for line in lines:
        # Strip leading # headers and keep text
        if line.startswith('#'):
            clean_line = line.lstrip('#').strip()
            if clean_line:
                cleaned_lines.append(f"**{clean_line}**")
        else:
            cleaned_lines.append(line)
            
    return '\n'.join(cleaned_lines).strip()


def generate_readme(selected_skills: list, repo_url: str) -> str:
    """Generate README.md for the skills repository."""
    repo_name = repo_url.replace("https://github.com/", "").replace(".git", "")
    
    # 1. Header & Installation
    readme_content = f"""# My Agent Skills

A collection of custom skills for AI agents.

## Installation

Install these skills with:

```bash
npx skills add {repo_name}
```

## About

This repository contains custom skills created for use with [agent-sync](https://github.com/renatocaliari/agent-sync).

Skills are compatible with:
- Opencode
- Claude Code
- Gemini CLI
- Pi.dev
- Qwen Code

## Skills

"""
    # 2. Skills list (at the end)
    for skill in selected_skills:
        readme_content += f"### {skill['name']}\n\n"
        skill_md = skill["path"] / "SKILL.md"
        
        if skill_md.exists():
            try:
                raw_content = skill_md.read_text()
                # Take first 500 chars after stripping junk
                clean_content = strip_frontmatter(raw_content)
                
                # Limit length
                summary = clean_content[:500]
                if len(clean_content) > 500:
                    summary += "..."
                
                readme_content += f"{summary}\n\n---\n\n"
            except Exception:
                readme_content += f"Custom skill for AI agents.\n\n---\n\n"
        else:
            readme_content += f"Custom skill for AI agents.\n\n---\n\n"
    
    return readme_content
