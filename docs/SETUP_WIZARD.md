# Setup Wizard Guide

The **agent-sync** interactive setup wizard for initial configuration and reconfiguration.

---

## When Wizard Runs

### Automatically
- When running `agent-sync init` for the first time (without arguments)
- When no configuration exists at `~/.config/agent-sync/config.yaml`

### Manually
- Run `agent-sync setup` to reconfigure at any time

### Skip Wizard
- Use `agent-sync init --name my-repo --no-wizard` to skip
- Or pass parameters directly: `--agents opencode claude-code`

---

## Wizard Steps

### Step 1: Detect Installed Agents

```
Step 1: Detecting Installed Agents
────────────────────────────────────

✓ Found installed agents:
  • opencode
  • claude-code
  • qwen-code

Not installed (2):
  • gemini-cli
  • pi.dev
```

Automatically detects which agents are installed on your system.

---

### Step 2: Select Agents to Sync

```
Step 2: Select Agents to Sync
──────────────────────────────

┏━━━━━━━━━━━━━━━┳━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Agent         ┃ Status ┃ Config Path              ┃
┡━━━━━━━━━━━━━━━╇━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ opencode      │ ✓      │ ~/.config/opencode/...   │
│ claude-code   │ ✓      │ ~/.claude/settings.json  │
│ gemini-cli    │ ✗      │ ~/.gemini/settings.json  │
│ pi.dev        │ ✗      │ ~/.pi/settings.json      │
│ qwen-code     │ ✓      │ ~/.qwen/settings.json    │
└───────────────┴────────┴──────────────────────────┘

Which agents to sync [all]: all
```

**Options:**
- `all` - All installed agents
- `none` - No agents
- `opencode,claude-code` - Comma-separated list

---

### Step 3: Configure Sync Options

```
Step 3: Configure Sync Options
───────────────────────────────

Configuring opencode:
  Sync configuration files? [Y/n]: y

Configuring claude-code:
  Sync configuration files? [Y/n]: y

Configuring qwen-code:
  Sync configuration files? [Y/n]: y
```

For each selected agent, choose:
- **Sync configs**: Configuration files (e.g., `settings.json`)
- **Skills**: Always synced via `~/.agents/skills/` (global)

---

### Step 4: Centralize Skills

```
Step 4: Centralizing Skills
────────────────────────────

Scanning for existing skills in all agents...
All skills will be centralized to ~/.agents/skills/

Found 24 skills across 4 agents.

Centralize all skills to ~/.agents/skills/? [Y/n]: y
```

Automatically:
- Scans all agent skill directories
- Detects conflicts (same skill in multiple agents)
- Resolves conflicts by renaming with agent prefix
- Copies to `~/.agents/skills/` (source of truth)

---

### Step 5: Configure Agents

```
Step 5: Configuring Agents
───────────────────────────

Automatically configuring agents to use global skills...

  ✓ opencode:     Updated config to include global skills
  ✓ claude-code:  Created symlink ~/.claude/commands/_global
  ✓ qwen-code:    Already uses ~/.agents/skills/ (no change)
  ✓ gemini-cli:   Using fallback (skills copied to agent path)
```

Automatically configures each agent to use `~/.agents/skills/`:
- **Symlink**: Claude Code
- **Config update**: Opencode
- **Native**: Pi.dev, Qwen Code
- **Fallback (copy)**: Gemini CLI

---

### Step 6: Repository Settings

```
Step 6: Repository Settings
────────────────────────────

⚠ SECURITY: Use PRIVATE repository for configs!

Your configs may contain sensitive information.
Private repositories are FREE on GitHub.

Repository name [agent-sync-configs]: my-agent-configs
Make repository PRIVATE? [Y/n]: y
```

**Important:**
- ⚠️ Private repository recommended
- ✅ Free on GitHub

---

### Step 7: Summary

```
╔══════════════════════════════════════════════════════════╗
║                  ✅ SETUP COMPLETE!                      ║
╠══════════════════════════════════════════════════════════╣
║                                                          ║
║  📦 Repository: my-agent-configs                         ║
║  📁 Skills: 24 centralized → ~/.agents/skills/           ║
║                                                          ║
║  Per-Agent Summary:                                      ║
║  🔗 opencode      - Config updated                      ║
║  🔗 claude-code   - Symlink created                     ║
║  ✓ qwen-code     - Native support                       ║
║  📋 gemini-cli    - Fallback (copy)                     ║
║                                                          ║
║  Next Steps:                                             ║
║    1. agent-sync config show                            ║
║    2. agent-sync push                                   ║
║    3. agent-sync link <url>  (other machines)           ║
║                                                          ║
╚══════════════════════════════════════════════════════════╝
```

---

## After Setup

### Create Repository

```bash
# Initialize GitHub repository
agent-sync init

# Or if already configured via wizard:
agent-sync init --no-wizard
```

### Push Configs

```bash
# Send your configs to GitHub
agent-sync push
```

---

## Generated Configuration

The wizard creates `~/.config/agent-sync/config.yaml`:

```yaml
repo_url: null  # Set after `agent-sync init`
agents:
  - opencode
  - claude-code
  - qwen-code
  - global-skills

agents_config:
  opencode:
    enabled: true
    sync:
      configs: true
  
  claude-code:
    enabled: true
    sync:
      configs: true
  
  qwen-code:
    enabled: true
    sync:
      configs: true
  
  global-skills:
    enabled: true
    sync:
      configs: false
```

---

## Tips

1. **First time**: Use wizard to configure everything correctly
2. **Reconfigure**: Run `agent-sync setup` anytime
3. **Non-interactive**: Use flags `--name`, `--agents`, `--no-wizard`
4. **Global skills**: Useful for shared skills across agents

---

## Troubleshooting

### Wizard doesn't appear
- Check for existing config: `cat ~/.config/agent-sync/config.yaml`
- Delete and run again: `rm ~/.config/agent-sync/config.yaml && agent-sync setup`

### Agent not detected
- Check if agent is installed: `which opencode`
- Agent may not be in PATH

### Cancel wizard
- Press `Ctrl+C` anytime
- Or answer `n` at final confirmation
