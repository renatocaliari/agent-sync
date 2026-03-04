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
agent-sync check-update
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
  check-update     Check for available updates.
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

# Link other machines
agent-sync link <url>     # Connect to existing repo
agent-sync pull           # Download configs

# Manage skills
agent-sync skills list                # List all skills
agent-sync skills centralize          # Centralize from agents
agent-sync skills centralize --copy   # Copy instead of move
agent-sync skills centralize --push   # Centralize + push
agent-sync skills centralize --distribute  # Centralize + copy to all agents (backup/testing)
agent-sync skills publish             # Publish skills to public GitHub (interactive)
agent-sync skills publish --dry-run   # Preview before publishing

# Configuration
agent-sync config show    # View current config
agent-sync config repo    # View/set repository URL
agent-sync config edit    # Edit manually
agent-sync config reset   # Reset to defaults

# Status & updates
agent-sync status         # Show sync status
agent-sync agents         # List all agents
agent-sync check-update   # Check for CLI updates
```

---

## 🛠️ CLI Commands Reference

### `agent-sync skills centralize --help`

```
$ agent-sync skills centralize --help

Usage: agent-sync skills centralize [OPTIONS]

  Centralize skills from all agents to ~/.agents/skills/.

  This command scans all agent directories for existing skills and centralizes
  them to the global ~/.agents/skills/ directory (single source of truth).

  Examples:
    # Move skills (default - removes from agent directories)
    agent-sync skills centralize
    
    # Copy skills (keeps originals in agent directories)
    agent-sync skills centralize --copy
    
    # Move skills and push to GitHub automatically
    agent-sync skills centralize --push
    
    # Copy skills and push to GitHub
    agent-sync skills centralize --copy --push
    
    # Centralize AND copy to all agent directories (backup/testing)
    agent-sync skills centralize --distribute

  What happens:
    1. Scans all agent directories for skills
    2. Detects conflicts (same skill name in multiple agents)
    3. Resolves conflicts by renaming with agent prefix
    4. Moves/copies skills to ~/.agents/skills/
    5. Optionally pushes to GitHub
    6. With --distribute: copies all skills to all agent directories

  After centralizing:
    - Skills live in ~/.agents/skills/ (source of truth)
    - Agents use symlinks or config to access global skills
    - Original skill directories may be removed (if --copy not used)
    - With --distribute: all agents have local copies for backup/testing

Options:
  --copy        Copy instead of moving skills
  --push        Automatically push to GitHub after centralizing
  --distribute  After centralizing, copy all skills to all agent directories
                (for backup or testing)
  --help        Show this message and exit.
```

### `agent-sync config repo --help`

```
$ agent-sync config repo --help

Usage: agent-sync config repo [OPTIONS] [REPO_URL]

  View or set the GitHub repository URL.

  Examples:
    # View current repository
    agent-sync config repo
    
    # Set repository URL
    agent-sync config repo https://github.com/user/repo.git
    
    # Remove repository configuration
    agent-sync config repo --remove

Options:
  --remove  Remove repository configuration
  --help    Show this message and exit.
```

### `agent-sync init --help`

```
$ agent-sync init --help

Usage: agent-sync init [OPTIONS]

  Initialize a new sync repository (first machine).

  Creates a new GitHub repository and configures agent-sync to sync to it.

  Examples:
    # Interactive wizard (creates new repo)
    agent-sync init
    
    # Create specific repo name (non-interactive)
    agent-sync init --name my-configs --private
    
    # Force re-initialize (overwrites existing config)
    agent-sync init --name new-configs --force

  ⚠️ SECURITY:
    - Always use PRIVATE repositories for configs
    - Configs may contain API keys and tokens
    - GitHub private repos are FREE for personal use

Options:
  --name TEXT           Repository name (skips wizard if provided)
  --private / --public  Make repository private
  --agents TEXT         Agents to sync (skips wizard if provided)
  --no-wizard           Skip interactive wizard
  --force               Force initialization even if already configured
  --help                Show this message and exit.
```

### `agent-sync skills publish --help`

```
$ agent-sync skills publish --help

Usage: agent-sync skills publish [OPTIONS]

  Publish selected skills to a public GitHub repository.

Options:
  --repo TEXT        GitHub repository URL for publishing skills
  --dry-run          Show what would be published without actually publishing
  -i, --interactive  Interactive TUI to select which skills to publish
  --help             Show this message and exit.
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
   → Creates fallback symlinks only when needed

2. Configure agents (automatic)
   Claude Code: symlink → ~/.agents/skills/
   Opencode:    config update
   Qwen Code:   native support
   Pi.dev:      native support
   Gemini CLI:  fallback (copy)

3. Sync to GitHub
   ~/.agents/skills/ ──push──► GitHub ──pull──► Other machines
```

---

## 📁 What Gets Synced

### On Your Computer
```
~/.agents/skills/              # All skills (source of truth)
~/.config/agent-sync/          # agent-sync settings
~/.config/opencode/            # Agent-specific configs
~/.claude/
~/.gemini/
~/.qwen/
~/.pi/
```

### On GitHub (Private Repo)
```
agent-sync-configs/
├── configs/
│   ├── opencode/
│   │   ├── opencode.jsonc     # Main config + plugins
│   │   └── opencode.json      # Alternative format
│   ├── claude-code/
│   │   ├── settings.json      # Main config + MCP servers
│   │   └── claude.json        # Alternative format
│   ├── gemini-cli/
│   │   └── settings.json      # Config + MCP + auth settings
│   ├── pi.dev/
│   │   ├── settings.json      # Main config
│   │   ├── models.json        # Model configurations
│   │   └── lsp-settings.json  # LSP configurations
│   └── qwen-code/
│       └── settings.json      # Config + MCP servers
│
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
- ❌ API keys in configs - Auto-scrubbed
- ❌ Bearer tokens - Auto-scrubbed
- ❌ Passwords - Auto-scrubbed

---

## 🛠️ Commands

### Setup
```bash
agent-sync setup              # Interactive setup wizard
agent-sync skills centralize  # Centralize existing skills
                              # → Asks if you want to push after
                              # → Use --push to auto-push
```

### Sync
```bash
agent-sync push               # Upload changes to GitHub
agent-sync pull               # Download changes from GitHub
agent-sync link <url>         # Connect to existing repo
```

### Manage
```bash
agent-sync config show        # View current config
agent-sync config edit        # Edit config manually
agent-sync config reset       # Reset to defaults
agent-sync agents             # List agents and status
agent-sync enable <name>      # Enable agent sync
agent-sync disable <name>     # Disable agent sync
agent-sync secrets export     # Backup secrets to file
```

### Skills
```bash
agent-sync skills list        # List all centralized skills
agent-sync skills centralize  # Move skills to ~/.agents/skills/
agent-sync skills centralize --copy  # Copy instead of move
agent-sync skills centralize --push  # Auto-push after centralize
```

---

## 🤖 Using Inside Agent CLIs

Once installed, you can use `agent-sync` from any agent CLI:

### Claude Code
```
/agent-sync push
```

### Opencode
```
/opencode agent-sync push
```

### Gemini CLI
```bash
agent-sync push
```

### Any Agent (shell command)
```bash
!agent-sync push
```

All agents have access to the `agent-sync` command as long as it's in your PATH.

---

## 🤖 Supported Agents

| Agent | Config Files | Skills Path | Method |
|-------|-------------|-------------|--------|
| **opencode** | `opencode.json`, `opencode.jsonc` | `~/.config/opencode/skills/` | Config |
| **claude-code** | `settings.json`, `claude.json` | `~/.claude/commands/` | Symlink |
| **gemini-cli** | `settings.json` | `~/.gemini/tools/` | Copy |
| **pi.dev** | `settings.json`, `models.json`, `lsp-settings.json` | `~/.pi/agent/skills/` | Native |
| **qwen-code** | `settings.json` | `~/.qwen/skills/` | Native |

All agents also support `~/.agents/skills/` for shared skills.

**Files automatically excluded:** `*auth*.json`, `*accounts*.json`, `*overrides*`, `*.lock`

---

## 📍 Agent Configuration Paths

### Opencode
- **Config:** `~/.config/opencode/opencode.json`
- **Skills:** `~/.config/opencode/skills/`
- **Docs:** https://opencode.ai/docs/

### Claude Code
- **Config:** `~/.claude/settings.json`
- **Skills:** `~/.claude/commands/`
- **Docs:** https://code.claude.com/docs/

### Gemini CLI
- **Config:** `~/.gemini/settings.json`
- **Skills:** `~/.gemini/tools/`
- **Docs:** https://gemini-cli-docs.pages.dev/

### Pi.dev
- **Config:** `~/.pi/settings.json`
- **Skills:** `~/.pi/agent/skills/` or `~/.agents/skills/`
- **Docs:** https://github.com/badlogic/pi-mono

### Qwen-code
- **Config:** `~/.qwen/settings.json`
- **Skills:** `~/.qwen/skills/` or `~/.agents/skills/`
- **Docs:** https://qwenlm.github.io/qwen-code-docs/

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

See `agent-sync --help` for all commands.

---

## 🔧 Troubleshooting

### Command Not Found

```bash
# Add to PATH
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc
```

### Skills Not Detected

```bash
# List centralized skills
agent-sync skills list

# Re-centralize if needed
agent-sync skills centralize
```

### Config Not Syncing

```bash
# Check agent is enabled
agent-sync agents

# Enable agent if needed
agent-sync enable opencode

# Push changes
agent-sync push
```

---

## 🙏 Inspiration

Inspired by [opencode-synced](https://github.com/iHildy/opencode-synced), expanded to support multiple agent CLIs with centralized skills and automatic secret protection.

---

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/renatocaliari/agent-sync/issues)
- **Discussions**: [GitHub Discussions](https://github.com/renatocaliari/agent-sync/discussions)

---

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.
