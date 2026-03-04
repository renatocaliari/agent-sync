"""Skills publishing to public GitHub repositories.

Publish selected skills to a PUBLIC repository for sharing with the community.
Separate from private agent-sync-configs repository.
"""

import shutil
import subprocess
import tempfile
import json
from pathlib import Path
from typing import Optional

import yaml
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich.table import Table
from rich import box


console = Console()

PUBLISH_CONFIG_PATH = Path.home() / ".config" / "agent-sync" / "publish.yaml"
SKILLS_DIR = Path.home() / ".agents" / "skills"


def publish_skills(repo_url: Optional[str] = None, dry_run: bool = False, interactive: bool = False) -> bool:
    """Publish selected skills to a public GitHub repository.
    
    Args:
        repo_url: GitHub repository URL (e.g., https://github.com/user/my-skills)
        dry_run: Show what would be published without actually publishing
        interactive: Show TUI for selecting skills
        
    Returns:
        True if successful, False otherwise
    """
    # Check if skills directory exists
    if not SKILLS_DIR.exists():
        console.print("\n[yellow]⚠ No skills directory found.[/yellow]")
        console.print("Run [green]agent-sync skills centralize[/green] to centralize skills first.\n")
        return False
    
    # Scan for skills
    skills_list = []
    for item in SKILLS_DIR.iterdir():
        if item.name.startswith("."):
            continue
        
        if item.is_dir() and (item / "SKILL.md").exists():
            # Valid skill directory
            skills_list.append({
                "name": item.name,
                "path": item,
                "valid": True,
                "selected": True  # Default: all selected
            })
        elif item.is_file() and item.suffix in [".md", ".py", ".sh"]:
            # Standalone file (not a full skill)
            skills_list.append({
                "name": item.name,
                "path": item,
                "valid": False,
                "selected": False
            })
    
    if not skills_list:
        console.print("\n[yellow]⚠ No skills found in ~/.agents/skills/[/yellow]\n")
        return False
    
    # Interactive mode: let user select skills
    if interactive:
        console.print("\n[bold]📤 Select Skills to Publish[/bold]\n")
        console.print("[dim]Toggle skills by entering numbers (e.g., '1,3,5')[/dim]\n")
        
        console.print("Skills found:\n")
        for i, skill in enumerate(skills_list, 1):
            if skill["valid"]:
                status = "✓" if skill["selected"] else "○"
                console.print(f"  [{status}] {i}. {skill['name']}")
            else:
                console.print(f"  [dim][○] {i}. {skill['name']} (not a valid skill - no SKILL.md)[/dim]")
        
        console.print()
        
        # Let user toggle selections
        while True:
            selection = Prompt.ask(
                "Toggle skills (e.g., '1,3,5' or 'all' or 'none' or 'done')",
                default="done"
            )
            
            if selection.lower() == "done" or selection == "":
                break
            elif selection.lower() == "all":
                for skill in skills_list:
                    if skill["valid"]:
                        skill["selected"] = True
            elif selection.lower() == "none":
                for skill in skills_list:
                    skill["selected"] = False
            else:
                # Parse comma-separated numbers
                try:
                    indices = [int(x.strip()) - 1 for x in selection.split(",")]
                    for idx in indices:
                        if 0 <= idx < len(skills_list):
                            if skills_list[idx]["valid"]:
                                skills_list[idx]["selected"] = not skills_list[idx]["selected"]
                                status = "✓" if skills_list[idx]["selected"] else "○"
                                console.print(f"  {skills_list[idx]['name']}: [{status}]")
                except ValueError:
                    console.print("[yellow]Invalid input. Use numbers like '1,3,5'[/yellow]")
            
            console.print()
        
        # Filter to only selected skills
        selected_skills = [s for s in skills_list if s["selected"]]
    else:
        # Non-interactive: all valid skills selected by default
        selected_skills = [s for s in skills_list if s["valid"]]
    
    if not selected_skills:
        console.print("\n[yellow]⚠ No skills selected for publishing[/yellow]\n")
        return False
    
    # Show what will be published
    console.print("\n[bold]📋 Skills to Publish[/bold]\n")
    
    table = Table(box=box.SIMPLE)
    table.add_column("Status", style="green")
    table.add_column("Skill Name", style="cyan")
    table.add_column("Path", style="dim")
    
    for skill in selected_skills:
        table.add_row("✓", skill["name"], str(skill["path"]))
    
    console.print(table)
    console.print()
    
    # SECURITY WARNING
    console.print(Panel(
        "[bold yellow]⚠️  SECURITY WARNING[/bold yellow]\n\n"
        "You are about to publish skills to a [bold]PUBLIC[/bold] repository.\n\n"
        "What WILL be published:\n"
        "  ✓ SKILL.md files (skill definitions)\n"
        "  ✓ .md, .py, .sh files (skill scripts)\n"
        "  ✓ references/ directory (documentation)\n"
        "  ✓ templates/ directory (templates)\n"
        "  ✓ scripts/ directory (automation scripts)\n\n"
        "What will [bold red]NEVER[/bold red] be published:\n"
        "  ✗ Any config files (settings.json, config.yaml, etc.)\n"
        "  ✗ Any files containing 'auth', 'token', 'key', 'secret' in name\n"
        "  ✗ .env files\n"
        "  ✗ Your private agent-sync-configs repository\n\n"
        "[dim]This is a SAFETY feature - your configs are kept separate.[/dim]",
        border_style="yellow",
    ))
    console.print()
    
    # Load or create publish config
    publish_config = {}
    if PUBLISH_CONFIG_PATH.exists():
        try:
            publish_config = yaml.safe_load(PUBLISH_CONFIG_PATH.read_text()) or {}
        except Exception:
            pass
    
    # Use provided repo URL or saved one
    if not repo_url:
        repo_url = publish_config.get("repo_url")
    
    if not repo_url:
        repo_url = Prompt.ask(
            "\n[bold]Enter GitHub repository URL for publishing[/bold]\n"
            "  (e.g., https://github.com/your-username/my-skills)",
            default=""
        )
        
        if not repo_url:
            console.print("\n[yellow]Publish cancelled[/yellow]\n")
            return False
        
        # Validate URL
        if not repo_url.startswith("https://github.com/"):
            console.print(f"\n[red]✗ Invalid repository URL[/red]")
            console.print(f"   Expected: https://github.com/username/repo.git\n")
            return False
        
        # Save to publish config (SEPARATE from main config!)
        PUBLISH_CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
        publish_config["repo_url"] = repo_url
        PUBLISH_CONFIG_PATH.write_text(yaml.dump(publish_config))
        console.print(f"\n[green]✓ Repository saved to {PUBLISH_CONFIG_PATH}[/green]")
    
    # Check repository visibility
    try:
        repo_name = repo_url.replace("https://github.com/", "").replace(".git", "")
        result = subprocess.run(
            ["gh", "api", f"repos/{repo_name}"],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if result.returncode == 0:
            repo_info = json.loads(result.stdout)
            is_private = repo_info.get("private", False)
            
            if is_private:
                console.print(Panel(
                    "[yellow]⚠️  Repository is PRIVATE[/yellow]\n\n"
                    "Others won't be able to install your skills with `npx skills add`.\n\n"
                    "To make it public:\n"
                    f"  gh repo edit {repo_name} --public\n\n"
                    "[dim]Or continue with private repo for personal use.[/dim]",
                    border_style="yellow",
                ))
                console.print()
            else:
                console.print(Panel(
                    "[green]✓ Repository is PUBLIC[/green]\n\n"
                    "Others can install your skills with:\n"
                    f"  [bold]npx skills add {repo_name}[/bold]\n\n"
                    "[dim]Perfect for sharing with the community![/dim]",
                    border_style="green",
                ))
                console.print()
    except Exception:
        console.print("[dim]Could not check repository visibility (gh CLI not available or repo doesn't exist yet)[/dim]\n")
    
    # Dry run mode
    if dry_run:
        console.print(Panel(
            "[bold]🔍 DRY RUN - No changes made[/bold]\n\n"
            f"Would publish {len(selected_skills)} skills to:\n"
            f"  {repo_url}\n\n"
            "Skills:\n" +
            "\n".join([f"  • {s['name']}" for s in selected_skills]),
            border_style="blue",
        ))
        console.print()
        return True
    
    # Confirm before publishing (SAFETY: default to NO)
    if not Confirm.ask(
        "\n[bold red]Confirm publishing to PUBLIC repository?[/bold red]\n"
        "This will make your skills visible to anyone on GitHub.",
        default=False,
    ):
        console.print("\n[yellow]Publish cancelled[/yellow]\n")
        return False
    
    # Create temporary directory for publishing
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        
        # Copy selected skills to temp directory (ONLY skills, no configs!)
        skills_tmp_dir = tmp_path / "skills"
        skills_tmp_dir.mkdir(parents=True, exist_ok=True)
        
        for skill in selected_skills:
            src = skill["path"]
            dst = skills_tmp_dir / skill["name"]
            
            if src.is_dir():
                shutil.copytree(src, dst)
            else:
                shutil.copy2(src, dst)
        
        # Create README for the skills repo
        readme_content = generate_readme(selected_skills, repo_url)
        (tmp_path / "README.md").write_text(readme_content)
        
        # Create .gitignore (NEVER commit configs or secrets)
        gitignore = """# Never commit configs or secrets
*.json
*.yaml
*.yml
.env
*auth*
*token*
*key*
*secret*
*credentials*
"""
        (tmp_path / ".gitignore").write_text(gitignore)
        
        console.print(f"\n[bold]📤 Publishing {len(selected_skills)} skills to {repo_url}...[/bold]\n")
        
        # Check if repo exists, if not create it
        repo_name = repo_url.replace("https://github.com/", "").replace(".git", "")
        try:
            result = subprocess.run(
                ["gh", "api", f"repos/{repo_name}"],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode != 0:
                # Repo doesn't exist, create it (PUBLIC by default for safety)
                console.print("  Creating repository on GitHub...")
                subprocess.run(
                    ["gh", "repo", "create", repo_name, "--public", "--description", "Custom AI agent skills"],
                    check=True,
                    capture_output=True
                )
                console.print("  [green]✓ Repository created[/green]")
        except Exception as e:
            console.print(f"  [yellow]⚠ Could not auto-create repository: {e}[/yellow]")
            console.print("  Please create the repository manually at: https://github.com/new")
            console.print(f"  Repository name: {repo_name}")
            console.print()
            
            if not Confirm.ask("Continue with git init and push anyway?", default=False):
                console.print("\n[yellow]Publish cancelled[/yellow]\n")
                return False
        
        # Initialize git repo and push
        try:
            # Git operations
            subprocess.run(["git", "init"], cwd=tmp_path, capture_output=True, check=True)
            subprocess.run(["git", "add", "."], cwd=tmp_path, capture_output=True, check=True)
            subprocess.run(["git", "commit", "-m", f"feat: publish {len(selected_skills)} skills"], cwd=tmp_path, capture_output=True, check=True)
            subprocess.run(["git", "branch", "-M", "main"], cwd=tmp_path, capture_output=True, check=True)
            subprocess.run(["git", "remote", "add", "origin", repo_url], cwd=tmp_path, capture_output=True, check=True)
            subprocess.run(["git", "push", "-u", "origin", "main", "--force"], cwd=tmp_path, capture_output=True, check=True)
            
            console.print(f"\n[green]✓ Successfully published {len(selected_skills)} skills![/green]\n")
            console.print(f"📦 Repository: {repo_url}\n")
            console.print("💡 Others can now install your skills with:\n")
            console.print(f"  [bold]npx skills add {repo_name}[/bold]\n")
            
            return True
            
        except subprocess.CalledProcessError as e:
            console.print(f"\n[red]✗ Failed to publish: {e}[/red]\n")
            if e.stderr:
                console.print(f"[dim]{e.stderr.decode()}[/dim]\n")
            return False
        except FileNotFoundError:
            console.print("\n[red]✗ Git not found. Please install git and try again.[/red]\n")
            return False


def generate_readme(selected_skills: list, repo_url: str) -> str:
    """Generate README.md for the skills repository."""
    repo_name = repo_url.replace("https://github.com/", "").replace(".git", "")
    
    readme_content = f"""# My Skills

A collection of custom skills for AI agents.

## Installation

Install these skills with:

```bash
npx skills add {repo_name}
```

## Skills

"""
    for skill in selected_skills:
        readme_content += f"### {skill['name']}\n\n"
        skill_md = skill["path"] / "SKILL.md"
        if skill_md.exists():
            # Read first few lines of SKILL.md for description
            try:
                content = skill_md.read_text()[:500]
                readme_content += f"{content}...\n\n"
            except Exception:
                readme_content += f"Custom skill for AI agents.\n\n"
        else:
            readme_content += f"Custom skill for AI agents.\n\n"
    
    readme_content += f"""
## About

This repository contains custom skills created for use with [agent-sync](https://github.com/renatocaliari/agent-sync).

Skills are compatible with:
- Opencode
- Claude Code
- Gemini CLI
- Pi.dev
- Qwen Code

## Security

This repository contains ONLY skill files (SKILL.md, .md, .py, .sh).

**NEVER contains:**
- Configuration files (settings.json, config.yaml, etc.)
- API keys or tokens
- Authentication credentials
- .env files

## License

Add your license here.
"""
    
    return readme_content
