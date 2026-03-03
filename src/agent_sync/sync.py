"""Sync management for agent-sync."""

import subprocess
import shutil
from pathlib import Path
from typing import Optional
from datetime import datetime


class SyncManager:
    """Manages synchronization with GitHub repository."""
    
    DEFAULT_REPO_DIR = Path.home() / ".local" / "share" / "agent-sync" / "repo"
    STATE_FILE = Path.home() / ".local" / "state" / "agent-sync" / "sync-state.json"
    
    def __init__(self, config):
        self.config = config
        self.repo_dir = self.DEFAULT_REPO_DIR
        self.state_file = self.STATE_FILE
        
        # Ensure directories exist
        self.repo_dir.parent.mkdir(parents=True, exist_ok=True)
        self.state_file.parent.mkdir(parents=True, exist_ok=True)
    
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
        Initialize a new sync repository.
        
        Args:
            name: Repository name
            private: Whether repo should be private
            agents: List of agents to sync
        
        Returns:
            Repository URL
        """
        if not self._check_gh_installed():
            raise RuntimeError("GitHub CLI (gh) is required. Install with: brew install gh")
        
        if not self._check_git_installed():
            raise RuntimeError("Git is required. Install with: brew install git")
        
        # Create repository on GitHub
        visibility = "private" if private else "public"
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
    
    def pull(self, force: bool = False) -> list[str]:
        """
        Fetch and apply remote configuration.
        
        Args:
            force: Force pull even with local changes
        
        Returns:
            List of applied changes
        """
        if not self.repo_dir.exists():
            raise RuntimeError("Not linked to a repository. Run 'agent-sync link' first")
        
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
        
        # Apply configs
        changes = self._apply_synced_configs()
        
        self._save_state("pulled", self.config.repo_url)
        
        return changes
    
    def push(self, message: str = "chore: sync config updates") -> list[str]:
        """
        Commit and push local changes.
        
        Args:
            message: Commit message
        
        Returns:
            List of pushed files
        """
        if not self.repo_dir.exists():
            raise RuntimeError("Not linked to a repository. Run 'agent-sync init' or 'link' first")
        
        # Stage agent configs
        self._stage_agent_configs()
        
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
            if sync_configs and agent.config_path and agent.config_path.exists():
                agent_config_dir = self.repo_dir / "configs" / agent.name
                agent_config_dir.mkdir(parents=True, exist_ok=True)
                shutil.copy2(agent.config_path, agent_config_dir)
        
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
            if sync_configs and synced_config_dir.exists() and agent.config_path:
                for config_file in synced_config_dir.glob("*"):
                    if config_file.is_file():
                        dest = agent.config_path.parent / config_file.name
                        if not dest.exists() or dest.read_text() != config_file.read_text():
                            shutil.copy2(config_file, dest)
                            changes.append(f"{agent.name}: {config_file.name}")
        
        # Apply global skills
        synced_skills_dir = self.repo_dir / "skills"
        global_skills_dir = Path.home() / ".agents" / "skills"
        
        if synced_skills_dir.exists():
            global_skills_dir.mkdir(parents=True, exist_ok=True)
            
            for skill_item in synced_skills_dir.glob("*"):
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
