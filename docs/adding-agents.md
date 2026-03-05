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

## Testing Your Change

After adding the agent to the registry, you can verify it by running:

```bash
agent-sync agents
```

It should appear in the list with its status and chosen skills method.
