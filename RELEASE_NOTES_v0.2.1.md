# 🔄 agent-sync v0.2.1

**Released:** March 4, 2026

---

## 🐛 Bug Fix Release

This is a **patch release** fixing a critical bug where native agents (pi.dev, qwen-code) were receiving duplicate copies of skills.

---

## 🎯 What Was Fixed

### Problem

When running `agent-sync setup` or `configure_agents()`, the skills were being **duplicated** in agent directories:

```
~/.pi/agent/skills/     - 24 skills copied ❌
~/.qwen/skills/         - 24 skills copied ❌
~/.agents/skills/       - 24 skills (source of truth) ✅
```

**Why?** The `_configure_agent()` method was not checking if an agent **natively supports** `~/.agents/skills/` before applying the fallback copy.

### Solution

1. **Added `supports_native()` check** before fallback copy in `_configure_agent()`
2. **Added `_cleanup_native_agents_skills()`** to remove previously duplicated skills
3. **Native agents now correctly skip copy** and use `~/.agents/skills/` directly

### Result

```
~/.pi/agent/skills/     - Empty (uses ~/.agents/skills/ directly) ✅
~/.qwen/skills/         - Empty (uses ~/.agents/skills/ directly) ✅
~/.agents/skills/       - 24 skills (source of truth) ✅
```

---

## 📊 Agent Configuration Methods

After this fix, each agent uses the correct method:

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

## 🔧 What Changed

### Files Modified

- `src/agent_sync/skills.py` (+58 lines, -8 lines)
  - Added `supports_native()` check in `_configure_agent()`
  - Added `_cleanup_native_agents_skills()` method
  - Updated `configure_agents()` to call cleanup after configuration

### Migration

If you're affected by this bug (skills duplicated in pi.dev or qwen-code), simply run:

```bash
# Re-run setup to fix configuration
agent-sync setup

# Or just re-configure agents
agent-sync config edit  # Then save without changes to trigger reconfigure
```

The cleanup will automatically remove duplicated skills from native agents.

---

## 📋 Full Changelog

See [CHANGELOG.md](https://github.com/renatocaliari/agent-sync/blob/main/CHANGELOG.md) for complete details.

---

## 📞 Support

- **Issues:** [GitHub Issues](https://github.com/renatocaliari/agent-sync/issues)
- **Discussions:** [GitHub Discussions](https://github.com/renatocaliari/agent-sync/discussions)
