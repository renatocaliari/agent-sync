# agent-sync v0.6.2

**Released:** March 4, 2026

---

## Critical Sync Fixes: Deletions Now Sync

### Before (Broken)

```bash
# Delete a skill locally
rm -rf ~/.agents/skills/old-skill

# Push skills
agent-sync push --skills-only

# ❌ Skill still exists in repo!
# User had to manually delete from GitHub
```

### After (Fixed)

```bash
# Delete a skill locally
rm -rf ~/.agents/skills/old-skill

# Push skills
agent-sync push --skills-only

# ✅ Skill removed from repo automatically!
```

---

## What Changed

### Fixed
- `_stage_skills()` now removes skills deleted from `~/.agents/skills/`
- `_stage_agent_configs()` now removes configs deleted locally
- `pull()` console import moved to function level

### Use Cases Fixed

| Scenario | Before | After |
|----------|--------|-------|
| Delete skill | ❌ Stays in repo | ✅ Removed on push |
| Delete config (`.json`) | ❌ Stays in repo | ✅ Removed on push |
| Keep `.jsonc`, remove `.json` | ❌ Both stay | ✅ Only `.jsonc` remains |

---

## Examples

### Remove a Skill

```bash
# Remove locally
rm -rf ~/.agents/skills/old-skill

# Sync to GitHub
agent-sync push --skills-only -m "remove: old-skill"

# ✅ Removed from repo
```

### Remove a Config File

```bash
# You have both:
# - ~/.config/opencode/opencode.json
# - ~/.config/opencode/opencode.jsonc

# Remove the one you don't want
rm ~/.config/opencode/opencode.json

# Sync to GitHub
agent-sync push --configs-only -m "remove: opencode.json"

# ✅ Only opencode.jsonc remains in repo
```

---

## Installation

```bash
pipx upgrade agent-sync
```

---

## Full Changelog

See [CHANGELOG.md](https://github.com/renatocaliari/agent-sync/blob/main/CHANGELOG.md)
