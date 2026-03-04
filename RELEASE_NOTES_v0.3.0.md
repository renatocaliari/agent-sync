# 🔄 agent-sync v0.3.0

**Released:** March 4, 2026

---

## 🎉 What's New

This release introduces a powerful new option for skill management and fixes a critical bug with native agents.

---

## ✨ New Feature: `--distribute` Option

### Command
```bash
agent-sync skills centralize --distribute
```

### What It Does

After centralizing skills to `~/.agents/skills/`, the `--distribute` option **copies all skills to ALL agent directories**:

```
~/.agents/skills/  ──distribute──►  ~/.config/opencode/skills/
(source of truth)                  ~/.claude/commands/
                                   ~/.gemini/tools/
                                   ~/.pi/agent/skills/
                                   ~/.qwen/skills/
```

### Use Cases

| Use Case | Description |
|----------|-------------|
| **💾 Backup** | Local copies in each agent directory for redundancy |
| **🧪 Testing** | Verify if agents read from local vs global skills |
| **🐛 Debug** | Troubleshoot symlink or config issues |

### Examples

```bash
# Centralize and distribute for backup
agent-sync skills centralize --distribute

# Centralize, distribute, and push to GitHub
agent-sync skills centralize --distribute --push

# Copy (not move) and distribute
agent-sync skills centralize --copy --distribute
```

### Output Example

```
📁 Moving Skills
✓ 24 skills moved to ~/.agents/skills/

📤 Distributing Skills to All Agents
⚠ This will copy ALL skills to ALL agent directories.

Use this for:
  • Backup: local copies in each agent directory
  • Testing: verify agents read from local vs global
  • Debug: troubleshoot symlink/config issues

Continue with distribution? [Y/n]: y

  Distributing to opencode...
    ✓ 24 skills copied
  Distributing to claude-code...
    ✓ 24 skills copied
  Distributing to gemini-cli...
    ✓ 24 skills copied
  Distributing to pi.dev...
    ✓ 24 skills copied
  Distributing to qwen-code...
    ✓ 24 skills copied

✓ Distributed 120 skills to 5 agents
```

---

## 🐛 Bug Fixes

### Native Agents Receiving Duplicate Skill Copies

**Problem:** When running `agent-sync setup`, skills were being **duplicated** in native agent directories:

```
~/.pi/agent/skills/     - 24 skills copied ❌
~/.qwen/skills/         - 24 skills copied ❌
~/.agents/skills/       - 24 skills (source of truth) ✅
```

**Root Cause:** The `_configure_agent()` method was not checking `supports_native()` before applying the fallback copy.

**Solution:**
1. Added `supports_native()` check before fallback in `_configure_agent()`
2. Added `_cleanup_native_agents_skills()` to remove previously duplicated skills
3. Native agents now correctly skip copy and use `~/.agents/skills/` directly

**Result:**
```
~/.pi/agent/skills/     - Empty (uses ~/.agents/skills/ directly) ✅
~/.qwen/skills/         - Empty (uses ~/.agents/skills/ directly) ✅
~/.agents/skills/       - 24 skills (source of truth) ✅
```

---

## 📊 Agent Configuration Methods

After this release, each agent uses the optimal method:

| Agent | Method | Description |
|-------|--------|-------------|
| **claude-code** | `symlink` | Creates `~/.claude/commands/_global` → `~/.agents/skills/` |
| **opencode** | `config` | Updates config to include `skills.paths: ["~/.agents/skills/"]` |
| **pi.dev** | `native` | Already reads from `~/.agents/skills/` (no change) |
| **qwen-code** | `native` | Already reads from `~/.agents/skills/` (no change) |
| **gemini-cli** | `fallback` | Copies skills to `~/.gemini/tools/` (only agent requiring copy) |

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

---

## 🔧 Migration

### If You're Affected by the Duplicate Skills Bug

If you see skills duplicated in `~/.pi/agent/skills/` or `~/.qwen/skills/`, simply re-run setup:

```bash
# Re-run setup to fix configuration
agent-sync setup

# Or re-configure agents only
agent-sync config edit  # Save without changes to trigger reconfigure
```

The cleanup will automatically remove duplicated skills from native agents.

### Using the New --distribute Option

If you want local backups in all agent directories:

```bash
# Centralize and distribute
agent-sync skills centralize --distribute

# Or centralize, distribute, and sync to GitHub
agent-sync skills centralize --distribute --push
```

**Note:** Native agents (pi.dev, qwen-code) will still prefer `~/.agents/skills/` even with local copies.

---

## 📋 Full Changelog

See [CHANGELOG.md](https://github.com/renatocaliari/agent-sync/blob/main/CHANGELOG.md) for complete details.

---

## 📞 Support

- **Issues:** [GitHub Issues](https://github.com/renatocaliari/agent-sync/issues)
- **Discussions:** [GitHub Discussions](https://github.com/renatocaliari/agent-sync/discussions)

---

## 🙏 Acknowledgments

Thanks to all users who reported the duplicate skills bug and suggested the `--distribute` feature!
