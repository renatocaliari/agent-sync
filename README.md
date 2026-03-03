# 🔄 agent-sync

**Sync your AI agent configurations and skills across multiple machines**

Supports: **opencode** • **claude-code** • **gemini-cli** • **pi.dev** • **qwen-code**

---

## ⚡ Quick Start

```bash
# Install
pip install agent-sync

# First machine
agent-sync setup    # Interactive wizard
agent-sync push     # Sync to GitHub

# Other machines
agent-sync link https://github.com/username/agent-sync-configs.git
agent-sync pull
```

That's it! Your configs and skills are now synced.

---

## 🎯 What It Does

| Problem | Solution |
|---------|----------|
| Configs scattered across machines | **One source of truth** on GitHub |
| Skills duplicated per agent | **Centralized** in `~/.agents/skills/` |
| Manual setup on each machine | **Automatic** configuration |
| Risk of leaking API keys | **Auto-scrubbed** before sync |

---

## 🔐 Security First

**By default, agent-sync protects your secrets:**

```bash
# Your configs are scrubbed before sync
"Authorization": "Bearer {{env:AGENT_SYNC_TOKEN}}"  # ← Synced

# Real token stored locally, never synced
~/.config/agent-sync/.env  # ← Git-ignored
```

| Synced ✅ | Never Synced ❌ |
|-----------|-----------------|
| Config structure | API keys |
| Skills | Auth tokens |
| Settings | Passwords |
| | MCP credentials |

**Requirements:**
- ✅ Private GitHub repository (free)
- ✅ Secrets disabled by default
- ✅ Auto-scrubbing enabled always

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
│  • qwen-code                                        • qwen-code
└─────────────────────────────────────────────────────────┘
```

### Skills Flow

```
1. Centralize (first time)
   ~/.config/opencode/skills/ ──┐
   ~/.claude/commands/          ├──► ~/.agents/skills/
   ~/.qwen/skills/              ──┘

2. Configure agents (automatic)
   Claude Code: symlink → ~/.agents/skills/
   Opencode:    config update
   Qwen Code:   native support

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
```

### On GitHub (Private Repo)
```
agent-sync-configs/
├── configs/
│   ├── opencode/opencode.jsonc
│   ├── claude-code/settings.json
│   ├── gemini-cli/settings.json
│   └── qwen-code/settings.json
│
└── skills/
    ├── code-review/
    ├── python-expert/
    └── ...
```

---

## 🛠️ Commands

### Setup
```bash
agent-sync setup          # Interactive setup wizard
agent-sync skills centralize  # Centralize existing skills
```

### Sync
```bash
agent-sync push           # Upload changes to GitHub
agent-sync pull           # Download changes from GitHub
agent-sync link <url>     # Connect to existing repo
```

### Manage
```bash
agent-sync config show    # View current config
agent-sync agents         # List agents and status
agent-sync enable <name>  # Enable agent sync
agent-sync disable <name> # Disable agent sync
```

---

## 🤖 Supported Agents

| Agent | Config | Skills | Method |
|-------|--------|--------|--------|
| **opencode** | `~/.config/opencode/` | `~/.config/opencode/skills/` | Config |
| **claude-code** | `~/.claude/` | `~/.claude/commands/` | Symlink |
| **gemini-cli** | `~/.gemini/` | `~/.gemini/tools/` | Copy |
| **pi.dev** | `~/.pi/` | `~/.pi/agent/skills/` | Native |
| **qwen-code** | `~/.qwen/` | `~/.qwen/skills/` | Native |

All agents also support `~/.agents/skills/` for shared skills.

---

## 📖 Documentation

- [Setup Wizard Guide](docs/SETUP_WIZARD.md) - Detailed walkthrough
- [Reconfiguration](docs/RECONFIGURATION.md) - Changing settings later
- [Agent Paths](docs/AGENT_PATHS.md) - Where each agent stores files
- [Implementation](docs/IMPLEMENTATION_SUMMARY.md) - Technical details

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
