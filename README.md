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

`agent-sync` uses a categorized, tree-like help structure. You can see all options for any command directly from the main help:

```bash
agent-sync --help
```

### Command Categories

#### 🔄 Sync
- `push` - Commit and push local changes `[-m, --skills-only, --configs-only]`
- `pull` - Fetch and apply remote configuration `[--force, --skills-only, --configs-only]`
- `status` - Show sync status and last sync times

#### 🤖 Agents
- `agents` - List supported agents and their status
- `enable` / `disable` - Toggle sync for a specific agent

#### ⚙️ Configuration
- `setup` - Run the interactive setup wizard
- `init` - Initialize a new sync repository `[--name, --private, --agents, --no-wizard, --force]`
- `config` - Manage agent-sync configuration
    - `show` - Show current configuration
    - `edit` - Open config in editor `[--agent]`
    - `repo` - View/set repository URL `[--remove]`
    - `reset` - Reset to defaults `[--yes]`

#### 📚 Skills
- `skills` - Manage global skills
    - `list` - List all centralized skills
    - `centralize` - Centralize skills from all agents `[--copy, --push, --distribute]`
    - `publish` - Publish skills to public GitHub `[--repo, --dry-run, --interactive]`

#### 🛠️ System
- `update` - Check for and install CLI updates (interactive)
- `version` - Show version information

---

If you are an AI model (LLM) contributing to this project, please read [AGENTS.md](AGENTS.md) for versioning and architectural mandates.

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
