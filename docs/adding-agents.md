# Adding New Agents to agent-sync

`agent-sync` uses a YAML-driven registry to manage agent integrations. This means adding support for a new agent usually only requires updating the YAML registry.

## Registry Location
The registry is located at `src/agent_sync/agent_registry.yaml`.

## Agent Definition Schema

Each agent entry in the YAML registry supports the following fields:

### Required Fields
- `method`: The synchronization method for skills.
    - `native`: Agent natively reads from `~/.agents/skills/`.
    - `config`: Agent supports a custom path for skills in its configuration file.
    - `copy`: Fallback method that copies skills to the agent's local directory.
- `skills_dir_name`: The name of the directory where the agent expects skills/commands/tools.
- `check`: How to verify if the agent is installed on the user's system.
    - `binary`: Name of the binary to check in PATH (e.g., `claude`).
    - `path`: Absolute path to a file that must exist (supports `~`).
    - `always`: Set to `true` for agents that are always available (like `global-skills`).

### Optional Fields
- `config_dir`: The base directory for the agent's configuration (supports `~`).
- `config_filename`: The name of the configuration file (e.g., `settings.json`).
- `config_update`: Required if `method` is `config`.
    - `path`: Dot-notation path to the configuration key (e.g., `skills.paths`).
    - `action`: `append` (for lists) or `set` (for single values).
- `extra_paths`: A dictionary of additional paths to be synced (used by `pi.dev`).
    - `extensions`: List of paths.
    - `prompts`: List of paths.
    - `themes`: List of paths.

## Example: Adding a New Agent

If you want to add support for an agent called `my-agent`:

1.  **Identify its config location**: e.g., `~/.myagent/config.json`.
2.  **Identify where it stores skills**: e.g., `~/.myagent/plugins/`.
3.  **Check if it supports custom paths**:
    - If yes, use `method: config`.
    - If no, use `method: copy`.

4.  **Add to `agent_registry.yaml`**:

```yaml
my-agent:
  method: copy
  config_dir: "~/.myagent"
  config_filename: "config.json"
  skills_dir_name: "plugins"
  check:
    binary: "myagent"
```

## Examples: VS Code Extensions & IDEs

### RooCode (Native Method)
RooCode natively reads from `~/.agents/skills/`, so no copy is needed:

```yaml
roocode:
  method: native
  config_dir: "~/.roo"
  config_filename: "custom_modes.yaml"
  skills_dir_name: "skills"
  check:
    path: "~/.roo/custom_modes.yaml"
  notes: "Native support for ~/.agents/skills/"
  mode_specific: true  # Supports skills-code/, skills-architect/, etc.
```

### Cline (Copy Method)
Cline uses copy to sync skills from the global hub:

```yaml
cline:
  method: copy
  config_dir: "~/.cline"
  config_filename: "state.json"
  skills_dir_name: "skills"
  check:
    binary: "cline"
  copy_from: "~/.agents/skills/"
  copy_to: "~/.cline/skills/"
  project_skills:
    - ".cline/skills/"
    - ".clinerules/skills/"
```

### Cursor (Copy with Transform)
Cursor uses a flat structure (`.cursor/rules/{name}.md`) instead of skill directories:

```yaml
cursor:
  method: copy
  config_dir: "~/.cursor"
  config_filename: "settings.json"
  skills_dir_name: "rules"
  check:
    binary: "cursor"
  copy_from: "~/.agents/skills/"
  copy_to: "~/.cursor/rules/"
  transform: "flatten"  # Transforms skills/{name}/SKILL.md → rules/{name}.md
```

### Windsurf (Copy Method)
Windsurf uses the same structure as Cline:

```yaml
windsurf:
  method: copy
  config_dir: "~/.codeium/windsurf"
  config_filename: "config.json"
  skills_dir_name: "skills"
  check:
    binary: "windsurf"
  copy_from: "~/.agents/skills/"
  copy_to: "~/.codeium/windsurf/skills/"
```

## Specialized Handlers

For agents that need custom logic (like Cursor's flatten transform), create a handler in `src/agent_sync/agents/{agent}.py`:

```python
"""{Agent Name} agent handler."""

from pathlib import Path
from typing import List, Dict, Any
from .base import BaseAgent

class {AgentName}Agent(BaseAgent):
    """Custom handler for {agent}."""
    
    def __init__(self, name: str, data: Dict[str, Any]):
        super().__init__(name, data)
        # Custom initialization
    
    def sync_skills(self, source: Path, dry_run: bool = False) -> List[str]:
        """Custom sync logic."""
        # Your implementation
        return []
```

Then register it in `src/agent_sync/agents/__init__.py`:

```python
AGENT_HANDLERS = {
    "{agent}": {AgentName}Agent,
    # ... other agents
}
```

## Testing Your Change

After adding the agent to the registry, you can verify it by running:

```bash
agent-sync agents
```

It should appear in the list with its status and chosen skills method.
