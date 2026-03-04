"""Sync management for agent-sync."""

import subprocess
import shutil
from pathlib import Path
from typing import Optional
from datetime import datetime
from platformdirs import user_data_dir


class SyncManager:
    """Manages synchronization with GitHub repository."""

    # Cross-platform data directory
    # Linux: ~/.local/share/agent-sync
    # macOS: ~/Library/Application Support/agent-sync
    # Windows: ~\AppData\Roaming\agent-sync
    DATA_DIR = Path(user_data_dir("agent-sync", "renatocaliari"))
    DEFAULT_REPO_DIR = DATA_DIR / "repo"
    STATE_FILE = DATA_DIR / "sync-state.json"
    
    # Config file patterns per agent (supports multiple extensions)
    CONFIG_PATTERNS = {
        "opencode": ["opencode.json", "opencode.jsonc"],
        "claude-code": ["settings.json", "claude.json"],
        "gemini-cli": ["settings.json"],
        "pi.dev": ["settings.json", "models.json", "lsp-settings.json"],
        "qwen-code": ["settings.json"],
    }
    
    # Files to NEVER sync (sensitive or local-only)
    EXCLUDE_PATTERNS = [
        "*auth*.json",
        "*accounts*.json",
        "*overrides*.json*",
        "*.lock",
        ".DS_Store",
        "package-lock.json",
        "bun.lock",
    ]
    
    def __init__(self, config):
        self.config = config
        self.repo_dir = self.DEFAULT_REPO_DIR
        self.state_file = self.STATE_FILE

        # Ensure directories exist BEFORE any operations
        try:
            self.repo_dir.mkdir(parents=True, exist_ok=True)  # Create repo dir itself
            self.repo_dir.parent.mkdir(parents=True, exist_ok=True)
            self.state_file.parent.mkdir(parents=True, exist_ok=True)
        except PermissionError as e:
            raise RuntimeError(
                f"Cannot create directory {self.repo_dir}. "
                f"Check permissions or set XDG_DATA_HOME environment variable."
            ) from e

        # Verify directory was created
        if not self.repo_dir.exists():
            raise RuntimeError(f"Failed to create directory {self.repo_dir}")
    
    def _run_git(self, *args, cwd: Optional[Path] = None) -> str:
        """Run a git command and return output."""
        cmd = ["git"] + list(args)
        result = subprocess.run(
            cmd,
            cwd=cwd or self.repo_dir,
            capture_output=True,
            text=True,
            check=True,
        )
        return result.stdout.strip()
    
    def _check_git_installed(self) -> bool:
        """Check if git is installed."""
        return shutil.which("git") is not None
    
    def _check_gh_installed(self) -> bool:
        """Check if GitHub CLI is installed."""
        return shutil.which("gh") is not None
    
    def init_repo(self, name: str, private: bool = True, agents: tuple[str, ...] = ()) -> str:
        """
        Initialize a new sync repository or link to existing one.

        Args:
            name: Repository name
            private: Whether repo should be private
            agents: List of agents to sync

        Returns:
            Repository URL
        """
        import json
        from rich.console import Console
        from rich.prompt import Confirm

        console = Console()

        if not self._check_gh_installed():
            raise RuntimeError("GitHub CLI (gh) is required. Install with: brew install gh")

        if not self._check_git_installed():
            raise RuntimeError("Git is required. Install with: brew install git")

        # Ensure repo directory exists
        self.repo_dir.mkdir(parents=True, exist_ok=True)

        # Check if repo already exists on GitHub
        repo_url = f"https://github.com/{self._get_github_user()}/{name}.git"
        repo_name = f"{self._get_github_user()}/{name}"

        result = subprocess.run(
            ["gh", "repo", "view", repo_name, "--json", "name,isPrivate"],
            capture_output=True,
            text=True,
            timeout=10,
        )

        if result.returncode == 0:
            # Repo exists - check visibility
            repo_info = json.loads(result.stdout)
            is_private = repo_info.get("isPrivate", False)

            if not is_private:
                # Public repo - warn about security
                console.print("\n[yellow]⚠️  WARNING: Repository is PUBLIC![/yellow]\n")
                console.print("Your configs may contain:")
                console.print("  • API keys")
                console.print("  • Auth tokens")
                console.print("  • MCP credentials\n")

                if not Confirm.ask(
                    "[bold red]Continue with public repository?[/bold red]\n"
                    "This is NOT recommended for config sync.",
                    default=False,
                ):
                    raise RuntimeError("User cancelled due to public repository warning")

            # Clone existing repo
            console.print(f"\n[bold]Linking to existing repository: {repo_name}[/bold]\n")

            if self.repo_dir.exists() and any(self.repo_dir.iterdir()):
                # Directory has content, use existing
                console.print("[dim]Using existing local directory[/dim]\n")
            else:
                # Empty directory, clone
                subprocess.run(
                    ["git", "clone", f"https://github.com/{repo_name}.git", str(self.repo_dir)],
                    check=True,
                    capture_output=True,
                )

            # Update config
            self.config.repo_url = repo_url
            if agents:
                self.config.agents = list(agents)
            self._save_state("linked", repo_url)

            return repo_url

        # Repo doesn't exist - create it
        visibility = "private" if private else "public"

        # Create repository on GitHub
        result = subprocess.run(
            ["gh", "repo", "create", name, f"--{visibility}", "--source", ".", "--remote", "origin"],
            cwd=self.repo_dir,
            capture_output=True,
            text=True,
        )

        if result.returncode != 0:
            # Try alternative approach
            subprocess.run(
                ["gh", "repo", "create", name, f"--{visibility}"],
                capture_output=True,
                text=True,
                check=True,
            )

            # Initialize local git
            self._run_git("init")
            self._run_git("remote", "add", "origin", f"https://github.com/{self._get_github_user()}/{name}.git")

        # Create initial structure
        self._create_repo_structure(agents)

        # Initial commit
        self._run_git("add", ".")
        self._run_git("commit", "-m", "chore: initial sync structure")
        self._run_git("push", "-u", "origin", "main")

        # Update config
        repo_url = f"https://github.com/{self._get_github_user()}/{name}.git"
        self.config.repo_url = repo_url

        if agents:
            self.config.agents = list(agents)

        self._save_state("initialized", repo_url)

        return repo_url
    
    def link_repo(self, repo_url: str) -> None:
        """
        Link to an existing sync repository.
        
        Args:
            repo_url: GitHub repository URL
        """
        if not self._check_git_installed():
            raise RuntimeError("Git is required")
        
        # Clone repository
        if self.repo_dir.exists():
            shutil.rmtree(self.repo_dir)
        
        subprocess.run(
            ["git", "clone", repo_url, str(self.repo_dir)],
            check=True,
        )
        
        # Update config
        self.config.repo_url = repo_url
        
        self._save_state("linked", repo_url)
    
    def pull(self, force: bool = False, skills_only: bool = False, configs_only: bool = False) -> list[str]:
        """
        Fetch and apply remote configuration.

        Args:
            force: Force pull even with local changes
            skills_only: Pull only skills (not configs)
            configs_only: Pull only configs (not skills)

        Returns:
            List of applied changes
        """
        from rich.console import Console
        console = Console()

        # If repo doesn't exist or is not a valid git repo, clone it automatically
        is_valid_git_repo = self.repo_dir.exists() and (self.repo_dir / ".git").exists()
        
        if not is_valid_git_repo:
            if not self.config.repo_url:
                raise RuntimeError("Not linked to a repository. Run 'agent-sync link <url>' or 'agent-sync config repo <url>' first")
            
            console.print(f"\n[bold]📥 Cloning repository...[/bold]\n")
            self.link_repo(self.config.repo_url)

        # Check for local changes
        if not force:
            status = self._run_git("status", "--porcelain")
            if status:
                raise RuntimeError(
                    "You have local changes. Commit them first or use --force"
                )

        # Fetch and pull
        self._run_git("fetch", "origin")
        self._run_git("pull", "origin", "main")

        changes = []

        # Apply configs (or skip based on flags)
        if not skills_only:
            changes.extend(self._apply_synced_configs())
        else:
            console.print("[dim]Skipping configs (skills-only mode)[/dim]")

        # Apply skills (or skip based on flags)
        if not configs_only:
            skill_changes = self._apply_synced_skills()
            changes.extend(skill_changes)
        else:
            console.print("[dim]Skipping skills (configs-only mode)[/dim]")

        self._save_state("pulled", self.config.repo_url)

        return changes
    
    def push(self, message: str = "chore: sync config updates", skills_only: bool = False, configs_only: bool = False) -> list[str]:
        """
        Commit and push local changes.

        Args:
            message: Commit message
            skills_only: Push only skills (not configs)
            configs_only: Push only configs (not skills)

        Returns:
            List of pushed files
        """
        if not self.repo_dir.exists():
            raise RuntimeError("Not linked to a repository. Run 'agent-sync init' or 'link' first")

        # Stage files based on flags
        if skills_only:
            # Stage only skills
            self._stage_skills()
        elif configs_only:
            # Stage only configs
            self._stage_agent_configs()
        else:
            # Stage everything (default)
            self._stage_agent_configs()
            self._stage_skills()

        # Check for changes
        status = self._run_git("status", "--porcelain")
        if not status:
            return []

        # Get list of changed files
        changed_files = []
        for line in status.split("\n"):
            if line.strip():
                parts = line.split()
                if len(parts) >= 2:
                    changed_files.append(parts[-1])

        # Commit and push
        self._run_git("add", ".")
        self._run_git("commit", "-m", message)
        self._run_git("push", "origin", "main")

        self._save_state("pushed", self.config.repo_url)

        return changed_files
    
    def get_status(self) -> dict:
        """
        Get sync status for all agents.

        Returns:
            Dictionary with status information per agent
        """
        from .agents import get_all_agents

        status = {}

        for agent in get_all_agents():
            # Check if agent sync is enabled
            if not self.config.is_agent_enabled(agent.name):
                status[agent.name] = {
                    "status": "disabled",
                    "last_sync": "-",
                    "changes": None,
                }
                continue
            
            agent_status = {
                "status": "not_configured",
                "last_sync": "-",
                "changes": None,
            }

            if agent.is_available():
                agent_status["status"] = "configured"

                # Check for uncommitted changes
                if self.repo_dir.exists():
                    try:
                        changes = self._run_git(
                            "diff", "--name-only",
                            cwd=agent.config_path.parent if agent.config_path.exists() else None
                        )
                        if changes:
                            agent_status["changes"] = f"{len(changes.split())} files"
                    except Exception:
                        pass
            
            # Get last sync time from state
            state = self._load_state()
            if state and state.get("last_sync"):
                agent_status["last_sync"] = state["last_sync"]
            
            status[agent.name] = agent_status
        
        return status
    
    def _create_repo_structure(self, agents: tuple[str, ...] = ()) -> None:
        """Create initial repository structure."""
        # Create directories
        (self.repo_dir / "configs").mkdir(parents=True, exist_ok=True)
        (self.repo_dir / "skills").mkdir(parents=True, exist_ok=True)
        (self.repo_dir / "prompts").mkdir(parents=True, exist_ok=True)
        
        # Create .gitignore
        gitignore = """# Secrets - NEVER sync these
.env
*.secret
*auth*.json
*credentials*.json
overrides.yaml

# OS files
.DS_Store
Thumbs.db

# Editor files
*.swp
*.swo
*~
"""
        (self.repo_dir / ".gitignore").write_text(gitignore)
        
        # Create README
        readme = """# Agent Sync Repository

This repository syncs configuration and skills across multiple AI agents.

## Managed by agent-sync

CLI tool: https://github.com/yourusername/agent-sync

## Structure

- `configs/` - Agent configurations
- `skills/` - Shared skills (source of truth: ~/.agents/skills/)
- `prompts/` - Shared prompts (optional)

## Usage

```bash
# First machine
agent-sync setup

# Additional machines
agent-sync link <repo-url>

# Sync
agent-sync pull
agent-sync push
```

## Skills

All skills are centralized in `~/.agents/skills/` and synced via `skills/`.
"""
        (self.repo_dir / "README.md").write_text(readme)
        
        # Create agent-specific directories
        from .agents import get_all_agents

        target_agents = agents if agents else [a.name for a in get_all_agents()]

        for agent_name in target_agents:
            (self.repo_dir / "configs" / agent_name).mkdir(parents=True, exist_ok=True)
        
        # Create skills directory (always)
        (self.repo_dir / "skills").mkdir(parents=True, exist_ok=True)
    
    def _stage_agent_configs(self) -> None:
        """Stage agent configurations for commit."""
        from .agents import get_all_agents

        for agent in get_all_agents():
            # Skip if agent sync is disabled
            if not self.config.is_agent_enabled(agent.name):
                continue

            if not agent.is_available() and agent.name != "global-skills":
                continue

            # Get sync options for this agent
            sync_options = self.config.get_sync_options(agent.name)
            sync_configs = sync_options.get("configs", True)

            # Copy configs to repo
            if sync_configs and agent.config_path.parent.exists():
                agent_config_dir = self.repo_dir / "configs" / agent.name
                agent_config_dir.mkdir(parents=True, exist_ok=True)

                # Get config file patterns for this agent
                patterns = self.CONFIG_PATTERNS.get(agent.name, ["*.json"])

                # Find all matching config files
                for pattern in patterns:
                    for config_file in agent.config_path.parent.glob(pattern):
                        if config_file.is_file():
                            # Skip excluded files
                            if self._should_exclude(config_file.name):
                                continue

                            # Copy config file as-is
                            dest = agent_config_dir / config_file.name
                            shutil.copy2(config_file, dest)

            # Copy Pi.dev extensions if agent is pi.dev
            if agent.name == "pi.dev" and hasattr(agent, 'extensions_paths'):
                for ext_path in agent.extensions_paths:
                    if ext_path.exists():
                        # Copy extensions to repo
                        repo_ext_dir = self.repo_dir / "configs" / agent.name / "extensions"
                        repo_ext_dir.mkdir(parents=True, exist_ok=True)

                        for ext_item in ext_path.iterdir():
                            dest = repo_ext_dir / ext_item.name
                            if ext_item.is_dir():
                                shutil.copytree(ext_item, dest, dirs_exist_ok=True)
                            else:
                                shutil.copy2(ext_item, dest)

    def _stage_skills(self) -> None:
        """Stage skills for commit."""
        from pathlib import Path

        global_skills_dir = Path.home() / ".agents" / "skills"
        repo_skills_dir = self.repo_dir / "skills"

        if not global_skills_dir.exists():
            return

        repo_skills_dir.mkdir(parents=True, exist_ok=True)

        # Copy all skills to repo
        for skill_item in global_skills_dir.iterdir():
            if skill_item.name.startswith("."):
                continue

            dest = repo_skills_dir / skill_item.name

            if skill_item.is_dir():
                if dest.exists():
                    shutil.rmtree(dest)
                shutil.copytree(skill_item, dest)
            else:
                shutil.copy2(skill_item, dest)
        
        # Always sync global skills
        global_skills_dir = Path.home() / ".agents" / "skills"
        if global_skills_dir.exists():
            repo_skills_dir = self.repo_dir / "skills"
            repo_skills_dir.mkdir(parents=True, exist_ok=True)
            
            for skill_item in global_skills_dir.iterdir():
                if skill_item.is_dir() or (skill_item.is_file() and skill_item.suffix in [".md", ".py", ".sh", ".json"]):
                    dest = repo_skills_dir / skill_item.name
                    if skill_item.is_dir():
                        shutil.copytree(skill_item, dest, dirs_exist_ok=True)
                    else:
                        shutil.copy2(skill_item, dest)
    
    def _should_exclude(self, filename: str) -> bool:
        """Check if a file should be excluded from sync."""
        import fnmatch
        
        for pattern in self.EXCLUDE_PATTERNS:
            if fnmatch.fnmatch(filename, pattern):
                return True
        
        return False
    
    def _apply_synced_configs(self) -> list[str]:
        """Apply synced configurations to local agent directories."""
        from .agents import get_all_agents

        changes = []

        for agent in get_all_agents():
            # Skip if agent sync is disabled
            if not self.config.is_agent_enabled(agent.name):
                continue
            
            synced_config_dir = self.repo_dir / "configs" / agent.name

            # Get sync options for this agent
            sync_options = self.config.get_sync_options(agent.name)
            sync_configs = sync_options.get("configs", True)

            # Apply configs
            if sync_configs and synced_config_dir.exists() and agent.config_path.parent.exists():
                for config_file in synced_config_dir.glob("*"):
                    if config_file.is_file():
                        dest = agent.config_path.parent / config_file.name
                        if not dest.exists() or dest.read_text() != config_file.read_text():
                            shutil.copy2(config_file, dest)
                            changes.append(f"{agent.name}: {config_file.name}")
            
            # Apply Pi.dev extensions if agent is pi.dev
            if agent.name == "pi.dev":
                synced_ext_dir = synced_config_dir / "extensions"
                if synced_ext_dir.exists():
                    # Apply to both extension paths
                    for ext_path in agent.extensions_paths:
                        ext_path.mkdir(parents=True, exist_ok=True)
                        
                        for ext_item in synced_ext_dir.iterdir():
                            dest = ext_path / ext_item.name
                            if not dest.exists() or (ext_item.is_file() and dest.read_text() != ext_item.read_text()):
                                if ext_item.is_dir():
                                    shutil.copytree(ext_item, dest, dirs_exist_ok=True)
                                else:
                                    shutil.copy2(ext_item, dest)
                                changes.append(f"{agent.name}/extensions: {ext_item.name}")
            
            # Apply Pi.dev prompts if agent is pi.dev
            if agent.name == "pi.dev":
                synced_prompts_dir = synced_config_dir / "prompts"
                if synced_prompts_dir.exists():
                    # Apply to both prompts paths
                    for prompts_path in agent.prompts_paths:
                        prompts_path.mkdir(parents=True, exist_ok=True)
                        
                        for prompt_item in synced_prompts_dir.iterdir():
                            dest = prompts_path / prompt_item.name
                            if not dest.exists() or (prompt_item.is_file() and dest.read_text() != prompt_item.read_text()):
                                if prompt_item.is_dir():
                                    shutil.copytree(prompt_item, dest, dirs_exist_ok=True)
                                else:
                                    shutil.copy2(prompt_item, dest)
                                changes.append(f"{agent.name}/prompts: {prompt_item.name}")
            
            # Apply Pi.dev themes if agent is pi.dev
            if agent.name == "pi.dev":
                synced_themes_dir = synced_config_dir / "themes"
                if synced_themes_dir.exists():
                    # Apply to both themes paths
                    for themes_path in agent.themes_paths:
                        themes_path.mkdir(parents=True, exist_ok=True)
                        
                        for theme_item in synced_themes_dir.iterdir():
                            dest = themes_path / theme_item.name
                            if not dest.exists() or (theme_item.is_file() and dest.read_text() != theme_item.read_text()):
                                if theme_item.is_dir():
                                    shutil.copytree(theme_item, dest, dirs_exist_ok=True)
                                else:
                                    shutil.copy2(theme_item, dest)
                                changes.append(f"{agent.name}/themes: {theme_item.name}")

        return changes

    def _apply_synced_skills(self) -> list[str]:
        """Apply synced skills to local ~/.agents/skills/ directory."""
        from pathlib import Path

        changes = []
        synced_skills_dir = self.repo_dir / "skills"
        global_skills_dir = Path.home() / ".agents" / "skills"

        if synced_skills_dir.exists():
            global_skills_dir.mkdir(parents=True, exist_ok=True)

            for skill_item in synced_skills_dir.glob("*"):
                if skill_item.name.startswith("."):
                    continue
                    
                dest = global_skills_dir / skill_item.name
                if not dest.exists() or (skill_item.is_file() and dest.read_text() != skill_item.read_text()):
                    if skill_item.is_dir():
                        shutil.copytree(skill_item, dest, dirs_exist_ok=True)
                    else:
                        shutil.copy2(skill_item, dest)
                    changes.append(f"global-skills: {skill_item.name}")

        return changes
    
    def _get_github_user(self) -> str:
        """Get current GitHub username."""
        result = subprocess.run(
            ["gh", "api", "user", "--jq", ".login"],
            capture_output=True,
            text=True,
            check=True,
        )
        return result.stdout.strip()
    
    def _save_state(self, action: str, repo_url: Optional[str] = None) -> None:
        """Save sync state."""
        import json
        
        state = {
            "last_sync": datetime.now().isoformat(),
            "last_action": action,
            "repo_url": repo_url or self.config.repo_url,
        }
        
        with open(self.state_file, "w") as f:
            json.dump(state, f, indent=2)
    
    def _load_state(self) -> Optional[dict]:
        """Load sync state."""
        import json
        
        if self.state_file.exists():
            with open(self.state_file) as f:
                return json.load(f)
        
        return None
