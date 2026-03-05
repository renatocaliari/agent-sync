"""Agent-specific configurations and handlers."""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional


# Global skills directory (shared across all agents)
GLOBAL_SKILLS_DIR = Path.home() / ".agents" / "skills"


class BaseAgent(ABC):
    """Base class for agent integrations."""

    name: str = "base"
    config_dir: Path = Path.home() / ".config"
    config_filename: str = "config.json"
    skills_dir_name: str = "skills"
    enabled: bool = True  # Whether this agent sync is enabled

    @property
    def config_path(self) -> Path:
        """Path to agent configuration file."""
        return self.config_dir / self.name / self.config_filename

    @property
    def skills_path(self) -> Path:
        """Path to agent-specific skills directory."""
        return self.config_dir / self.name / self.skills_dir_name

    @property
    def tools_path(self) -> Path:
        """Path to agent-specific tools directory."""
        return self.config_dir / self.name / "tools"

    @property
    def commands_path(self) -> Path:
        """Path to agent-specific commands directory."""
        return self.config_dir / self.name / "commands"

    @property
    def global_skills_path(self) -> Path:
        """Path to global ~/.agents/skills directory."""
        return GLOBAL_SKILLS_DIR

    @abstractmethod
    def is_available(self) -> bool:
        """Check if this agent is installed/configured."""
        pass

    def get_config(self) -> Optional[dict]:
        """Load agent configuration."""
        import json

        if self.config_path.exists():
            with open(self.config_path) as f:
                return json.load(f)
        return None

    def save_config(self, config: dict) -> None:
        """Save agent configuration."""
        import json

        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.config_path, "w") as f:
            json.dump(config, f, indent=2)

    def enable(self) -> None:
        """Enable sync for this agent."""
        self.enabled = True

    def disable(self) -> None:
        """Disable sync for this agent."""
        self.enabled = False

    def is_enabled(self) -> bool:
        """Check if sync is enabled for this agent."""
        return self.enabled

    def supports_symlink(self) -> bool:
        """Check if this agent supports symlinks for skills.

        Returns:
            True if agent can use symlinks (Claude Code, Gemini CLI)
        """
        # Claude Code and Gemini CLI support symlinks in commands/tools directory
        return self.name in ["claude-code", "gemini-cli"]

    def supports_config(self) -> bool:
        """Check if this agent supports config-based skills paths.

        Returns:
            True if agent can be configured via config file
        """
        # Opencode supports skills.paths in config
        return self.name == "opencode"

    def supports_native(self) -> bool:
        """Check if this agent natively supports ~/.agents/skills/.

        Returns:
            True if agent already reads from global skills dir
        """
        # Only pi.dev natively supports ~/.agents/skills/
        # qwen-code only supports ~/.qwen/skills/ (not ~/.agents/skills/)
        return self.name == "pi.dev"

    def get_all_skills_paths(self) -> list[Path]:
        """Get all skills paths for this agent (some agents have multiple)."""
        paths = [self.skills_path]

        # Add agent-specific additional paths
        if hasattr(self, "_additional_skills_paths"):
            paths.extend(self._additional_skills_paths())

        # Filter to only existing paths
        return [p for p in paths if p.exists()]

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name={self.name}, enabled={self.enabled})"


class OpencodeAgent(BaseAgent):
    """Opencode agent integration.

    Docs: https://opencode.ai/docs/
    Paths:
      - Config: ~/.config/opencode/opencode.json
      - Skills: ~/.config/opencode/skills/
      - Tools: ~/.config/opencode/tools/
      - Commands: ~/.config/opencode/commands/
    """

    name = "opencode"
    config_filename = "opencode.json"
    skills_dir_name = "skills"  # Plural is standard (singular also works)

    @property
    def config_path(self) -> Path:
        """Path to Opencode config file."""
        return self.config_dir / self.name / self.config_filename

    @property
    def skills_path(self) -> Path:
        """Path to Opencode skills directory."""
        return self.config_dir / self.name / self.skills_dir_name

    def _additional_skills_paths(self) -> list[Path]:
        """Opencode can also use ~/.agents/skills/."""
        return [GLOBAL_SKILLS_DIR]

    def is_available(self) -> bool:
        """Check if opencode is installed."""
        import shutil

        return shutil.which("opencode") is not None or self.config_path.exists()


class ClaudeCodeAgent(BaseAgent):
    """Claude Code agent integration.

    Docs: https://code.claude.com/docs/
    Paths:
      - Config: ~/.claude/settings.json (or ~/.claude.json)
      - Commands: ~/.claude/commands/
      - Worktrees: <project>/.claude/worktrees/
    """

    name = "claude-code"
    config_dir = Path.home() / ".claude"
    config_filename = "settings.json"
    skills_dir_name = "commands"  # Claude Code uses 'commands' for custom skills

    @property
    def config_path(self) -> Path:
        """Path to Claude Code settings file."""
        return self.config_dir / self.config_filename

    @property
    def skills_path(self) -> Path:
        """Path to Claude Code commands directory."""
        return self.config_dir / "commands"

    def is_available(self) -> bool:
        """Check if Claude Code is installed."""
        import shutil

        return shutil.which("claude") is not None or self.config_path.exists()


class GeminiCliAgent(BaseAgent):
    """Gemini CLI agent integration.

    Docs: https://gemini-cli-docs.pages.dev/
    Paths:
      - Config: ~/.gemini/settings.json
      - Project config: .gemini/settings.json
      - Tools: .gemini/ (custom tool scripts)
    """

    name = "gemini-cli"
    config_dir = Path.home() / ".gemini"
    config_filename = "settings.json"
    skills_dir_name = "tools"

    @property
    def config_path(self) -> Path:
        """Path to Gemini CLI settings file."""
        return self.config_dir / self.config_filename

    @property
    def skills_path(self) -> Path:
        """Path to Gemini CLI tools directory."""
        return self.config_dir / "tools"

    @property
    def commands_path(self) -> Path:
        """Path to Gemini CLI commands directory (for symlink)."""
        return self.config_dir / "tools"

    def is_available(self) -> bool:
        """Check if Gemini CLI is installed."""
        import shutil

        return shutil.which("gemini") is not None or self.config_path.exists()


class PiDevAgent(BaseAgent):
    """Pi.dev agent integration.

    Docs: https://github.com/badlogic/pi-mono
    Paths:
      - Config: ~/.pi/agent/settings.json
      - Extensions: ~/.pi/agent/extensions/, ~/.pi/extensions/
      - Prompts: ~/.pi/agent/prompts/, ~/.pi/prompts/
      - Themes: ~/.pi/agent/themes/, ~/.pi/themes/
      - Skills: ~/.pi/agent/skills/, ~/.pi/skills/, ~/.agents/skills/
    """

    name = "pi.dev"
    config_dir = Path.home() / ".pi" / "agent"  # ← Configs are in ~/.pi/agent/
    config_filename = "settings.json"
    skills_dir_name = "skills"

    @property
    def config_path(self) -> Path:
        """Path to Pi.dev settings file."""
        return self.config_dir / self.config_filename

    @property
    def skills_path(self) -> Path:
        """Path to Pi.dev global skills directory."""
        # Pi.dev uses multiple paths, we use the global one
        return Path.home() / ".pi" / "agent" / "skills"

    @property
    def extensions_paths(self) -> list[Path]:
        """Pi.dev extensions directories."""
        return [
            Path.home() / ".pi" / "agent" / "extensions",
            Path.home() / ".pi" / "extensions",
        ]

    @property
    def prompts_paths(self) -> list[Path]:
        """Pi.dev prompts directories."""
        return [
            Path.home() / ".pi" / "agent" / "prompts",
            Path.home() / ".pi" / "prompts",
        ]

    @property
    def themes_paths(self) -> list[Path]:
        """Pi.dev themes directories."""
        return [
            Path.home() / ".pi" / "agent" / "themes",
            Path.home() / ".pi" / "themes",
        ]

    @property
    def global_skills_path(self) -> Path:
        """Path to global ~/.agents/skills directory (also used by Pi)."""
        return GLOBAL_SKILLS_DIR

    def _additional_skills_paths(self) -> list[Path]:
        """Pi.dev also uses ~/.agents/skills/."""
        return [GLOBAL_SKILLS_DIR]

    def is_available(self) -> bool:
        """Check if Pi.dev is configured."""
        return self.config_path.exists()


class QwenCodeAgent(BaseAgent):
    """Qwen Code agent integration.

    Docs: https://qwenlm.github.io/qwen-code-docs/
    Paths:
      - Config: ~/.qwen/settings.json
      - Skills: ~/.qwen/skills/ (global), .qwen/skills/ (project)
      - Agents: ~/.qwen/agents/
    """

    name = "qwen-code"
    config_dir = Path.home() / ".qwen"
    config_filename = "settings.json"
    skills_dir_name = "skills"

    @property
    def config_path(self) -> Path:
        """Path to Qwen Code settings file."""
        return self.config_dir / self.config_filename

    @property
    def skills_path(self) -> Path:
        """Path to Qwen Code global skills directory."""
        return self.config_dir / "skills"

    def is_available(self) -> bool:
        """Check if Qwen Code is installed."""
        import shutil

        return shutil.which("qwen") is not None or self.config_path.exists()


class GlobalSkillsAgent(BaseAgent):
    """Global ~/.agents/skills directory."""

    name = "global-skills"
    config_filename = ""  # No config file, just skills

    @property
    def config_path(self) -> Path:
        """No config path for global skills."""
        return Path("")

    @property
    def skills_path(self) -> Path:
        """Path to global skills directory."""
        return GLOBAL_SKILLS_DIR

    def is_available(self) -> bool:
        """Global skills always available."""
        return True


def get_all_agents() -> list[BaseAgent]:
    """Get all available agent integrations."""
    return [
        OpencodeAgent(),
        ClaudeCodeAgent(),
        GeminiCliAgent(),
        PiDevAgent(),
        QwenCodeAgent(),
        GlobalSkillsAgent(),
    ]


def get_agent(name: str) -> Optional[BaseAgent]:
    """Get a specific agent by name."""
    agents = get_all_agents()
    for agent in agents:
        if agent.name == name:
            return agent
    return None


def get_enabled_agents() -> list[BaseAgent]:
    """Get only enabled agent integrations."""
    return [agent for agent in get_all_agents() if agent.is_enabled()]
