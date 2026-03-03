# 🔄 agent-sync

**Synchronize configurations and skills across multiple AI agent CLIs**

Supports: **opencode**, **claude-code**, **gemini-cli**, **pi.dev**, **qwen-code**

---

## 🎯 What It Does

`agent-sync` is a unified CLI that synchronizes your configurations, skills, and prompts between different AI agents and multiple machines via a **private GitHub repository**.

### Key Features

| Feature | Description |
|---------|-------------|
| **Multi-Agent** | Support for 5+ agents (opencode, claude, gemini, pi, qwen) |
| **Centralized Skills** | All skills in `~/.agents/skills/` (source of truth) |
| **Auto-Configuration** | Automatically configures agents to use global skills |
| **Secrets Safe** | API keys never synced by default (secure by design) |
| **GitHub-Based** | Private repository for sync |
| **Conflict Resolution** | Auto-resolves duplicate skills across agents |

---

## 📊 Visual Overview

### Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    YOUR MACHINES                                │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Machine A                          Machine B                   │
│  ┌─────────────────┐               ┌─────────────────┐         │
│  │ ~/.agents/      │               │ ~/.agents/      │         │
│  │   skills/       │◄─────────────►│   skills/       │         │
│  │   (source)      │    GitHub     │   (synced)      │         │
│  └────────┬────────┘    Private    └─────────────────┘         │
│           │             Repo                                    │
│           ▼                                                     │
│  ┌─────────────────┐                                           │
│  │ Agent Configs   │                                           │
│  │ • opencode      │                                           │
│  │ • claude-code   │                                           │
│  │ • gemini-cli    │                                           │
│  │ • qwen-code     │                                           │
│  └─────────────────┘                                           │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Skills Flow

```
┌─────────────────────────────────────────────────────────────────┐
│  SKILL SYNCHRONIZATION                                          │
└─────────────────────────────────────────────────────────────────┘

Step 1: Centralize (First Time)
───────────────────────────────
~/.config/opencode/skills/  ──┐
~/.claude/commands/           ├──► ~/.agents/skills/ ──┐
~/.qwen/skills/               ──┘   (source of truth)  │
                                                        │
Step 2: Sync to GitHub                                  │
─────────────────────────                               ▼
~/.agents/skills/ ──────────────────────► GitHub Repo (skills/global/)
                                                        │
Step 3: Pull on Other Machines                          │
────────────────────────────                              │
GitHub Repo ───────────────────────────► ~/.agents/skills/
                                                        │
Step 4: Distribute (Automatic)                          │
────────────────────────────────                          │
~/.agents/skills/ ──symlink──► ~/.claude/commands/_global
                ──config───► ~/.config/opencode/opencode.json
                ──native───► ~/.qwen/skills/ (already works)
```

### Directory Structure

```
Your Computer                          GitHub Repository
─────────────────                      ─────────────────

~/.agents/skills/                    repo/
├── code-review/                     ├── configs/
│   └── SKILL.md                     │   ├── opencode/
├── python-expert/                   │   │   └── opencode.json
│   └── SKILL.md                     │   ├── claude-code/
└── security-audit/                  │   │   └── settings.json
    └── SKILL.md                     │   └── ...
                                     │
~/.config/agent-sync/                ├── skills/
├── config.yaml                      │   └── global/
└── overrides.yaml                   │       ├── code-review/
                                     │       │   └── SKILL.md
~/.claude/commands/_global ────────► │       └── python-expert/
    (symlink to ~/.agents/skills/)   │           └── SKILL.md
                                     │
~/.config/opencode/                  ├── prompts/
├── opencode.json                    │   └── ...
└── skills/ ───────────────────────► │
    (configured to read global)      └── README.md
```

---

## 🚀 Quick Start

### Prerequisites

```bash
# Install Git
brew install git

# Install GitHub CLI
brew install gh
gh auth login

# Install agent-sync
pip install agent-sync
```

### First Machine - Interactive Setup (Recommended)

```bash
# Run setup wizard
agent-sync setup

# The wizard will automatically:
# 1. Detect installed agents
# 2. Centralize existing skills → ~/.agents/skills/
# 3. Configure agents to use global skills
# 4. Create PRIVATE GitHub repository
# 5. Show detailed summary

# Send configs to GitHub
agent-sync push
```

### Additional Machines

```bash
# Link to existing repository
agent-sync link https://github.com/username/agent-sync-configs.git

# Download configs and skills
agent-sync pull
```

### Useful Commands

```bash
# Centralize existing skills
agent-sync skills centralize

# View configuration
agent-sync config show

# Reconfigure
agent-sync setup

# Enable/disable specific agent
agent-sync enable opencode
agent-sync disable claude-code
```

---

## 🔐 Security

### Private Repository (Default)

```
⚠ SECURITY: Use PRIVATE repository for configs!

Your configs may contain sensitive information.
Private repositories are FREE on GitHub.

Make repository PRIVATE? [Y/n]: y
```

### Secrets Handling

| Item | Synced? | Default | Recommendation |
|------|---------|---------|----------------|
| **Config files** | ✅ Yes | Yes | ✅ Safe |
| **Skills** | ✅ Yes | Yes | ✅ Safe |
| **API Keys** | ⚠️ Optional | **No** | ❌ Don't sync |
| **Auth tokens** | ⚠️ Optional | **No** | ❌ Don't sync |
| **MCP credentials** | ⚠️ Optional | **No** | ❌ Don't sync |

### Automatic Protection

```yaml
# ~/.config/agent-sync/config.yaml
include_secrets: false      # ← Default: DON'T sync secrets
include_mcp_secrets: false  # ← Default: DON'T sync MCP secrets
```

**If you enable secrets:**
- ⚠️ Repository **MUST** be private
- ⚠️ Warning shown during setup
- ⚠️ Secrets stored in `~/.config/agent-sync/.env` (never synced)

---

## 📁 File Structure

### On Your Computer

```
~/.agents/skills/                    ← Source of truth (global)
├── code-review/
│   └── SKILL.md
├── python-expert/
│   └── SKILL.md
└── security-audit/
    └── SKILL.md

~/.config/agent-sync/
├── config.yaml                      ← agent-sync configuration
└── overrides.yaml                   ← Local overrides (not synced)

~/.config/<agent>/                   ← Agent-specific configs
├── opencode/opencode.json
├── claude-code/settings.json
└── ...

~/.claude/commands/_global → ~/.agents/skills/  ← Symlink (Claude Code)
```

### On GitHub Repository

```
agent-sync-configs/                  ← PRIVATE repository
├── configs/
│   ├── opencode/
│   │   └── opencode.json
│   ├── claude-code/
│   │   └── settings.json
│   └── ...
│
├── skills/
│   └── global/                      ← Synchronized skills
│       ├── code-review/
│       │   └── SKILL.md
│       └── ...
│
├── prompts/                         ← Optional
│   └── ...
│
├── .gitignore
└── README.md
```

---

## 🤖 Supported Agents

| Agent | Config Path | Skills Path | Method |
|-------|-------------|-------------|--------|
| **opencode** | `~/.config/opencode/opencode.json` | `~/.config/opencode/skills/` | Config |
| **claude-code** | `~/.claude/settings.json` | `~/.claude/commands/` | Symlink |
| **gemini-cli** | `~/.gemini/settings.json` | `~/.gemini/tools/` | Fallback |
| **pi.dev** | `~/.pi/settings.json` | `~/.pi/agent/skills/` | Native |
| **qwen-code** | `~/.qwen/settings.json` | `~/.qwen/skills/` | Native |
| **global-skills** | - | `~/.agents/skills/` | Always |

### Configuration Methods

| Method | How It Works | Agents |
|--------|--------------|--------|
| **Symlink** | `~/.claude/commands/_global` → `~/.agents/skills/` | claude-code |
| **Config** | Update agent config to include global path | opencode |
| **Native** | Agent already reads from `~/.agents/skills/` | pi.dev, qwen-code |
| **Fallback** | Copy skills to agent-specific directory | gemini-cli |

---

## 📋 Commands Reference

### Setup & Configuration

```bash
# Interactive setup (recommended for first time)
agent-sync setup

# View current configuration
agent-sync config show

# Edit configuration file
agent-sync config edit

# Reset to defaults (keeps repo linked)
agent-sync config reset
```

### Skills Management

```bash
# Centralize skills from all agents to ~/.agents/skills/
agent-sync skills centralize

# This will:
# - Scan all agent skill directories
# - Detect conflicts (same skill in multiple agents)
# - Resolve conflicts automatically (rename with prefix)
# - Copy to ~/.agents/skills/
```

### Synchronization

```bash
# Initialize new repository (first machine)
agent-sync init

# Link to existing repository (additional machines)
agent-sync link <repo-url>

# Push changes to GitHub
agent-sync push

# Pull changes from GitHub
agent-sync pull
```

### Agent Management

```bash
# List all agents and their status
agent-sync agents

# Enable sync for specific agent
agent-sync enable opencode

# Disable sync for specific agent
agent-sync disable claude-code
```

### Secrets

```bash
# Enable secrets synchronization
agent-sync secrets enable

# Disable secrets synchronization
agent-sync secrets disable
```

---

## 🔄 Workflows

### First-Time Setup

```bash
# 1. Run wizard
agent-sync setup

# 2. Review summary
# → Shows per-agent configuration
# → Shows skills centralized
# → Shows repository URL

# 3. Push to GitHub
agent-sync push
```

### Adding New Skill

```bash
# 1. Create skill in global directory
mkdir -p ~/.agents/skills/my-skill
echo "# My Skill" > ~/.agents/skills/my-skill/SKILL.md

# 2. Push to GitHub
agent-sync push -m "feat: add my-skill"

# 3. On other machines
agent-sync pull
```

### Adding New Agent

```bash
# 1. Enable agent
agent-sync enable gemini-cli

# 2. Push configuration
agent-sync push -m "feat: add gemini-cli sync"
```

### Reconfiguring

```bash
# Already using and want to change something?
agent-sync setup

# This will:
# - Show current configuration
# - Ask for confirmation to overwrite
# - Run full wizard again
# - Keep repository URL
```

---

## 🛠️ Development

### Install for Development

```bash
git clone https://github.com/renatocaliari/agent-sync.git
cd agent-sync
pip install -e ".[dev]"
```

### Run Tests

```bash
make test
```

### Lint & Format

```bash
make lint
make format
```

---

## 📝 Configuration Reference

### `~/.config/agent-sync/config.yaml`

```yaml
# GitHub repository URL (set automatically)
repo_url: https://github.com/username/agent-sync-configs.git

# Agents to synchronize
agents:
  - opencode
  - claude-code
  - qwen-code
  - global-skills

# Per-agent configuration
agents_config:
  opencode:
    enabled: true
    sync:
      configs: true
      # skills: always true (implicit)
  
  claude-code:
    enabled: true
    sync:
      configs: true
  
  global-skills:
    enabled: true
    sync:
      configs: false

# Secrets (default: disabled)
include_secrets: false
include_mcp_secrets: false
```

### `~/.config/agent-sync/overrides.yaml`

```yaml
# Local overrides (NEVER synced)
machine_name: "macbook-pro-work"

custom_paths:
  opencode: /custom/path/to/opencode
```

---

## ⚠️ Important Notes

### Do's ✅

- ✅ Use **private** repository
- ✅ Run `agent-sync pull` before `push`
- ✅ Check `agent-sync status` regularly
- ✅ Use `--force` carefully on `pull`

### Don'ts ❌

- ❌ Commit `.env` or secret files
- ❌ Use public repo with secrets enabled
- ❌ Edit configs directly on GitHub
- ❌ Share your private repo URL

---

## 🐛 Troubleshooting

### Skills Not Detected

```bash
# Check if skills have SKILL.md
ls ~/.agents/skills/my-skill/

# Should contain:
# SKILL.md (required)
# (optional: scripts, assets)
```

### Agent Not Configured

```bash
# Check agent status
agent-sync agents

# Reconfigure specific agent
agent-sync setup
```

### Sync Conflicts

```bash
# Force pull (overwrites local changes)
agent-sync pull --force

# Or resolve manually
agent-sync config edit
```

---

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.

---

## 🙏 Inspiration

This project was inspired by [opencode-synced](https://github.com/iHildy/opencode-synced), but expanded to support multiple agent CLIs with centralized skills.

---

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/renatocaliari/agent-sync/issues)
- **Discussions**: [GitHub Discussions](https://github.com/renatocaliari/agent-sync/discussions)

---

## 📈 Roadmap

- [ ] Add tests for SkillsManager
- [ ] Improve documentation for each agent
- [ ] Add `skills distribute` command (optional)
- [ ] Support for more agents (codex, etc.)
