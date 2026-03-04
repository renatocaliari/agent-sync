# 🔄 agent-sync v0.2.0

**Released:** March 4, 2026

---

## 🎉 Highlights

This release brings **cross-platform support** for Windows and macOS, full **Pi.dev extensions/prompts/themes sync**, and major improvements to the **skills centralize** workflow.

### 🌟 Major Features

#### 🖥️ Cross-Platform Support
Proper directory paths for all major operating systems using `platformdirs`:

| OS | Config Path | Data Path |
|----|-------------|-----------|
| **Linux** | `~/.config/agent-sync/` | `~/.local/share/agent-sync/` |
| **macOS** | `~/Library/Application Support/agent-sync/` | `~/Library/Application Support/agent-sync/` |
| **Windows** | `%APPDATA%\agent-sync\` | `%LOCALAPPDATA%\agent-sync\` |

#### 🎯 Pi.dev Full Support
Complete synchronization for Pi.dev agent:
- ✅ **Extensions** - `~/.pi/agent/extensions/` and `~/.pi/extensions/`
- ✅ **Prompts** - `~/.pi/agent/prompts/`
- ✅ **Themes** - `~/.pi/agent/themes/`
- ✅ **Models** - `~/.pi/agent/models.json`
- ✅ **LSP Settings** - `~/.pi/agent/lsp-settings.json`

#### 🔧 Skills Centralize Improvements
New options for the `skills centralize` command:
```bash
# Copy skills (keep originals in agent directories)
agent-sync skills centralize --copy

# Move skills and push to GitHub automatically
agent-sync skills centralize --push

# Copy and push
agent-sync skills centralize --copy --push
```

**Detailed reports** now show:
- Number of skills moved/copied
- Conflicts resolved with automatic renaming
- User symlinks cleaned up from agent directories

#### 📦 Version Management
New commands for version control:
```bash
# Show current version
agent-sync --version

# Check for available updates
agent-sync check-update
```

**Async update notifications** on `push` and `pull` commands (once per week).

#### 🔐 Private Repository Support
Update checks now work with private repositories using `GITHUB_TOKEN`:
```bash
export GITHUB_TOKEN=ghp_...
agent-sync check-update
```

---

## 🔧 Changes

### Setup Wizard
- **Streamlined** - Removed unused secrets sync UI (step 7)
- Secrets sync was never implemented - configs sync as-is
- Wizard now has **7 steps** instead of 8
- Faster setup experience

### Documentation
- **Consolidated** - Removed `/docs` directory (1160 lines)
- Added CLI `--help` output to README
- Added "Most Used Commands" section
- Added "Agent Configuration Paths" section
- Added "Reconfiguration" section
- All documentation now in **README.md** for better discoverability

### Config Display
- Simplified `agent-sync config show` output
- Removed secrets section (was never implemented)

### Skills Flow
- Default behavior is now `--move` (not `--copy`)
- Automatic conflict detection and resolution
- Idempotent centralization (skip if already exists)

---

## 🐛 Bug Fixes

| Issue | Fix |
|-------|-----|
| Claude Code fallback symlink | Correct handling when symlink not supported |
| Pi.dev config path | Changed from `~/.pi/` to `~/.pi/agent/` |
| Secret scrubber | Only scrub MCP secrets, not native agent API keys |
| Secrets with hyphens | Proper handling of env var names with hyphens |

---

## 📦 Installation

### Upgrade Existing Installation
```bash
# Using pipx (recommended)
pipx upgrade agent-sync

# Using pip
pip install --upgrade agent-sync

# Using npx skills (for AI agents)
npx skills update renatocaliari/agent-sync -g
```

### Fresh Install
```bash
pipx install git+https://github.com/renatocaliari/agent-sync.git
```

### Install from Source
```bash
git clone https://github.com/renatocaliari/agent-sync.git
cd agent-sync
pip install -e .
```

---

## 📋 What's Synced

| Agent | Config Files | Skills Path | Method |
|-------|-------------|-------------|--------|
| **opencode** | `opencode.json`, `opencode.jsonc` | `~/.config/opencode/skills/` | Config |
| **claude-code** | `settings.json`, `claude.json` | `~/.claude/commands/` | Symlink |
| **gemini-cli** | `settings.json` | `~/.gemini/tools/` | Copy |
| **pi.dev** | `settings.json`, `models.json`, `lsp-settings.json` | `~/.pi/agent/skills/` | Native |
| **qwen-code** | `settings.json` | `~/.qwen/skills/` | Native |

All agents also support `~/.agents/skills/` for shared skills.

---

## 🚀 Quick Start

### First Machine
```bash
# Interactive setup wizard
agent-sync setup

# Push to GitHub (use private repo!)
agent-sync push
```

### Other Machines
```bash
# Link to existing repository
agent-sync link https://github.com/username/agent-sync-configs.git

# Download configs
agent-sync pull
```

### Centralize Skills
```bash
# Move all skills from agent directories to ~/.agents/skills/
agent-sync skills centralize

# Or copy (keep originals)
agent-sync skills centralize --copy
```

---

## 🔒 Security Note

**⚠️ ALWAYS use PRIVATE repositories!**

Your config files may contain:
- API keys
- Auth tokens
- MCP server credentials
- Other sensitive data

GitHub private repositories are **free** for personal use.

---

## 📖 Full Changelog

See [CHANGELOG.md](https://github.com/renatocaliari/agent-sync/blob/main/CHANGELOG.md) for complete details.

---

## 🙏 Acknowledgments

Inspired by [opencode-synced](https://github.com/iHildy/opencode-synced), expanded to support multiple agent CLIs with centralized skills and cross-platform support.

---

## 📞 Support

- **Issues:** [GitHub Issues](https://github.com/renatocaliari/agent-sync/issues)
- **Discussions:** [GitHub Discussions](https://github.com/renatocaliari/agent-sync/discussions)
