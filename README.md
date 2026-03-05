# 🔄 agent-sync

**Centralize and sync AI agent configurations and skills across machines and agents**

Supports: **opencode** • **claude-code** • **gemini-cli** • **pi.dev** • **qwen-code**

---

## ⚡ Quick Start

### Install CLI (Required)

**Option 1: Install from GitHub**
```bash
pipx install git+https://github.com/renatocaliari/agent-sync.git
```

**Option 2: Install with pip**
```bash
pip install git+https://github.com/renatocaliari/agent-sync.git
```

**Option 3: Install from source**
```bash
git clone https://github.com/renatocaliari/agent-sync.git
cd agent-sync
pip install -e .
```

### Install Skill (For AI Agents - Optional)

If you want AI agents (Claude Code, Opencode, Gemini CLI, etc.) to use agent-sync:

```bash
npx skills add renatocaliari/agent-sync -g
```

**Note:** The skill is just documentation for AI agents. You still need to install the CLI separately.

### Verify CLI Installation

```bash
agent-sync --version
# If not found: export PATH="$HOME/.local/bin:$PATH"
```

### Check for Updates

```bash
agent-sync update
# or
pipx upgrade git+https://github.com/renatocaliari/agent-sync.git
```

### First Machine

```bash
agent-sync setup    # Interactive wizard
agent-sync push     # Sync to GitHub
```

### Other Machines

```bash
agent-sync link https://github.com/username/agent-sync-configs.git
agent-sync pull
```

**That's it!** Your configs and skills are now synced across machines and agents.

---

## 🎯 What It Does

| Problem | Solution |
|---------|----------|
| Configs scattered across machines | **One source of truth** on GitHub |
| Skills duplicated per agent | **Centralized** in `~/.agents/skills/` |
| Manual setup on each machine | **Automatic** configuration |
| Risk of leaking API keys | **Auto-scrubbed** before sync |

---

## 🛠️ CLI Commands

```
$ agent-sync --help

Usage: agent-sync [OPTIONS] COMMAND [ARGS]...

  🔄 agent-sync - Sync configs and skills across multiple AI agents.

  Supported agents: opencode, claude-code, gemini-cli, pi.dev, qwen-code

Options:
  --version  Show the version and exit.
  --help     Show this message and exit.

Commands:
  agents           List supported agents and their status.
  update           Check for available updates and install them.
  config           Manage configuration (view, edit, reset).
  disable          Disable sync for a specific agent.
  enable           Enable sync for a specific agent.
  generate-config  Generate initial configuration file.
  init             Initialize a new sync repository (first machine).
  link             Link to an existing sync repository (additional...
  pull             Fetch and apply remote configuration.
  push             Commit and push local changes.
  secrets          Manage secrets and environment variables.
  setup            Run the interactive setup wizard to configure or...
  skills           Manage global skills.
  status           Show sync status and last sync times.
  version          Show version information.
```

### Most Used Commands

```bash
# First time setup
agent-sync setup          # Interactive wizard
agent-sync push           # Upload to GitHub

# Manage skills
agent-sync skills list                # List all skills
agent-sync skills centralize          # Centralize from agents
agent-sync skills centralize --copy   # Copy instead of move
agent-sync skills centralize --push   # Centralize + push

# Configuration
agent-sync config show    # View current config
agent-sync config repo    # View/set repository URL
agent-sync config edit    # Edit manually
agent-sync config reset   # Reset to defaults

# Status & updates
agent-sync status         # Show sync status
agent-sync agents         # List all agents
agent-sync update         # Check and install updates
```

---

## 🔐 Security

**Your config files may contain API keys and tokens.**

- ⚠️ **ALWAYS use PRIVATE repository**
- ⚠️ **Keep your repo private**
- ✅ Config files are synced as-is
- ✅ Each agent manages their own authentication

---

## 📊 How It Works

```
┌─────────────────────────────────────────────────────────┐
│  Machine A                        Machine B             │
│                                                         │
│  ~/.agents/skills/  ────────►  GitHub  ────────►  ~/.agents/skills/
│  (source of truth)              (private)          (synced)
│                                                         │
│  Agent Configs ─────────────────────────────────►  Agent Configs
│  • opencode                                         • opencode
│  • claude-code                                      • claude-code
│  • gemini-cli                                       • gemini-cli
│  • pi.dev                                           • pi.dev
│  • qwen-code                                        • qwen-code
└─────────────────────────────────────────────────────────┘
```

### Skills Flow

```
1. Centralize (first time)
   ~/.config/opencode/skills/ ──┐
   ~/.claude/commands/          │
   ~/.gemini/tools/             ├──► ~/.agents/skills/
   ~/.pi/agent/skills/          │    (source of truth)
   ~/.qwen/skills/              ──┘
   
   → Moves all skills to central location
   → Removes user symlinks from agent directories
   → Configures agents to use global path or local copies

2. Configure agents (automatic)
   Opencode:    Config update (multiple paths)
   Pi.dev:      Native support (~/.agents/skills)
   Claude Code: Copy fallback (optimized for speed)
   Gemini CLI:  Copy fallback (optimized for speed)
   Qwen Code:   Copy fallback (optimized for speed)

3. Sync to GitHub
   ~/.agents/skills/ ──push──► GitHub ──pull──► Other machines
```

---

## 📁 What Gets Synced

### On Your Computer
```
~/.agents/skills/              # All skills (source of truth)
~/.config/agent-sync/          # agent-sync settings
~/.config/agent-sync/registry.yaml # Agent definitions (internal)
~/.config/opencode/            # Agent-specific configs
...
```

### On GitHub (Private Repo)
```
agent-sync-configs/
├── configs/
│   ├── opencode/
│   │   ├── opencode.jsonc     # Main config + plugins
│   └── ...
└── skills/
    ├── code-review/
    ├── python-expert/
    └── ...
```

### What's Protected (Never Synced)
- ❌ `*auth*.json` - Authentication files
- ❌ `*accounts*.json` - Account credentials  
- ❌ `*overrides*` - Local overrides
- ❌ `*.lock` - Package locks

---

## 🤖 Supported Agents

| Agent | Config Files | Skills Path | Method |
|-------|-------------|-------------|--------|
| **opencode** | `opencode.json`, `opencode.jsonc` | `~/.config/opencode/skills/` | Config |
| **pi.dev** | `settings.json`, `models.json` | `~/.pi/agent/skills/` | Native |
| **global-skills** | - | `~/.agents/skills/` | Native |
| **claude-code** | `settings.json` | `~/.claude/commands/` | Copy |
| **gemini-cli** | `settings.json` | `~/.gemini/tools/` | Copy |
| **qwen-code** | `settings.json` | `~/.qwen/skills/` | Copy |

All agents also support `~/.agents/skills/` for shared skills.

**Files automatically excluded:** `*auth*.json`, `*accounts*.json`, `*overrides*`, `*.lock`

---

## 🏗️ Architecture (YAML Registry)

agent-sync uses a YAML-based registry to define how each agent is configured. This makes it easy to add new agents or customize existing ones.

The registry is located at `src/agent_sync/agent_registry.yaml`. You can also override the configuration method for any agent in your local `config.yaml`:

```yaml
agents_config:
  claude-code:
    skills_method: copy  # Options: native, config, copy
```

See the [Adding New Agents guide](docs/adding-agents.md) for more details.

---

## 🔄 Reconfiguration

Change settings at any time:

```bash
# Full reconfiguration
agent-sync setup

# Quick commands
agent-sync enable <agent>       # Enable agent
agent-sync disable <agent>      # Disable agent
agent-sync config show          # View config
agent-sync config edit          # Edit manually
agent-sync config reset         # Reset defaults
```

---

## 🙏 Inspiration

Inspired by [opencode-synced](https://github.com/iHildy/opencode-synced), expanded to support multiple agent CLIs with centralized skills and automatic secret protection.

---

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.
