# Reconfiguration Guide

Reconfigure **agent-sync** at any time, even after extended use.

---

## When to Reconfigure

- ✅ Add new agent (e.g., started using Gemini CLI)
- ✅ Remove unused agent
- ✅ Change what gets synced (e.g., stop syncing skills)
- ✅ Enable/disable global skills
- ✅ Change secrets settings
- ✅ Fix incorrect configuration

---

## Reconfiguration Methods

### 1. Setup Wizard (Recommended)

```bash
# Reconfigure everything with interactive wizard
agent-sync setup
```

**What happens:**
- Detects installed agents
- Shows current configuration
- Allows changing everything
- Keeps your repository linked
- **Doesn't delete repo data**

**Flow:**
```
1. Warning about existing configuration
2. Confirmation to continue
3. Full wizard (same as initial setup)
4. Configuration updated
5. Prompt to run `agent-sync push`
```

---

### 2. Configuration Commands

#### View Current Configuration

```bash
# Show configuration
agent-sync config show
```

**Example output:**
```
📋 Current Configuration

Repository: https://github.com/user/my-configs.git

Enabled Agents:
  ✓ opencode: configs
  ✓ claude-code: configs
  ✗ gemini-cli (disabled)
  ✓ qwen-code: configs

Secrets:
  Include secrets: No
  Include MCP: No
```

---

#### Edit Manually

```bash
# Open config file in editor
agent-sync config edit

# Or edit manually
nano ~/.config/agent-sync/config.yaml
```

**Example edit:**

```yaml
# Before
agents_config:
  opencode:
    enabled: true
    sync:
      configs: true

# After - disable opencode
agents_config:
  opencode:
    enabled: false  # ← Change here
```

---

#### Reset to Defaults

```bash
# Reset configuration (keeps repo linked)
agent-sync config reset
```

**What it does:**
- Resets all settings to defaults
- Keeps `repo_url` (doesn't unlink)
- Enables all detected agents
- Removes custom configurations

**After reset:**
```bash
# Reconfigure with wizard
agent-sync setup

# Or edit manually
agent-sync config edit
```

---

### 3. Enable/Disable Commands

```bash
# Enable specific agent
agent-sync enable gemini-cli

# Disable specific agent
agent-sync disable claude-code

# Check status
agent-sync agents
```

**Quick and direct** - good for simple changes.

---

## Common Scenarios

### Scenario 1: Add New Agent

You started using Gemini CLI:

```bash
# Option A: Wizard (easiest)
agent-sync setup
# → Select gemini-cli from list
# → Configure sync options
# → Confirm

# Option B: Quick command
agent-sync enable gemini-cli

# Then: push changes
agent-sync push -m "feat: add gemini-cli sync"
```

---

### Scenario 2: Stop Syncing Configs

```bash
# Option A: Wizard
agent-sync setup
# → For each agent: answer "n" to "Sync configs?"

# Option B: Edit config
agent-sync config edit

# Change in YAML:
agents_config:
  opencode:
    enabled: false  # ← Change to false

# Then: push
agent-sync push -m "chore: disable opencode sync"
```

---

### Scenario 3: Fix Wrong Configuration

Configuration got messed up:

```bash
# Reset everything
agent-sync config reset

# Reconfigure from scratch
agent-sync setup

# Verify
agent-sync config show
agent-sync agents
```

---

## What's Kept vs. Changed

### Kept ✅
- Repository URL
- Configs already synced in repo
- Git history
- Secrets in local `.env`

### Changed 🔄
- Configuration in `~/.config/agent-sync/config.yaml`
- Enabled/disabled agents
- Sync options per agent
- Secrets settings

### Not Affected ❌
- Files in `~/.agents/skills/`
- Agent configs (`~/.claude/`, `~/.qwen/`, etc.)
- GitHub remote repository

---

## Best Practices

### 1. Push After Reconfiguring

```bash
agent-sync setup
agent-sync push -m "chore: reconfigure agents"
```

### 2. Notify Other Users

If sharing the repo:

```bash
# After reconfiguring and pushing
git commit -m "chore: add gemini-cli sync

Other users should run:
  agent-sync pull
"
```

### 3. Test Before Push

```bash
# Check status
agent-sync status

# Check agents
agent-sync agents

# Then: push
agent-sync push
```

### 4. Backup Config

```bash
# Backup before reset
cp ~/.config/agent-sync/config.yaml \
   ~/.config/agent-sync/config.yaml.backup

# After reset
agent-sync config reset
```

---

## Troubleshooting

### Reconfiguration not applying

```bash
# Force pull after reconfiguring
agent-sync pull --force

# Or full reset
agent-sync config reset
agent-sync setup
agent-sync pull --force
```

### Agents not appearing

```bash
# Check if agent is installed
which opencode

# Check detection
agent-sync agents

# If not detected, install agent or check PATH
```

### Configuration corrupted

```bash
# Reset
agent-sync config reset

# Or delete and recreate
rm ~/.config/agent-sync/config.yaml
agent-sync setup
```

---

## Command Summary

| Command | Description | When to Use |
|---------|-------------|-------------|
| `agent-sync setup` | Interactive wizard | Reconfigure everything |
| `agent-sync config show` | View configuration | Check status |
| `agent-sync config edit` | Edit manually | Specific changes |
| `agent-sync config reset` | Reset to defaults | Start fresh |
| `agent-sync enable <agent>` | Enable agent | Add agent quickly |
| `agent-sync disable <agent>` | Disable agent | Remove agent quickly |
| `agent-sync push` | Push changes | After reconfiguring |

---

## Next Steps

After reconfiguring:

1. ✅ Verify configuration: `agent-sync config show`
2. ✅ Push changes: `agent-sync push`
3. ✅ Update other machines: `agent-sync pull`
4. ✅ Test sync: `agent-sync status`
