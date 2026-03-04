# agent-sync v0.6.1

**Released:** March 4, 2026

---

## Critical UX Fix: Auto-Clone on Pull

### Before (Broken)

```bash
agent-sync config repo https://github.com/user/repo.git
agent-sync pull
# ❌ Error: Not linked to a repository
# User had to manually clone:
# git clone <url> ~/.local/share/agent-sync/repo
```

### After (Fixed)

```bash
agent-sync config repo https://github.com/user/repo.git
agent-sync pull
# ✅ Auto-clones repository
# ✅ Applies configs and skills
```

---

## What Changed

### Fixed
- `pull` now auto-clones repo if not exists locally
- Check for valid git repo (`.git/` exists) not just directory
- Import console locally to avoid undefined error

### User Impact
- **No manual clone needed** - just `config repo` + `pull`
- **No `agent-sync link` required** - simpler workflow
- **Better error messages** - clear guidance if repo URL not set

---

## Installation

```bash
pipx upgrade agent-sync
```

---

## Full Changelog

See [CHANGELOG.md](https://github.com/renatocaliari/agent-sync/blob/main/CHANGELOG.md)
