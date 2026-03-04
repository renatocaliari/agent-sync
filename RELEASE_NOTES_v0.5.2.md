# agent-sync v0.5.2

**Released:** March 4, 2026

---

## ⚠️ Critical Security Fixes

### 1. Repo Directory Creation Error

**Error:**
```
❌ Error: [Errno 2] No such file or directory: 
'/Users/cali/Library/Application Support/agent-sync/repo'
```

**Fix:**
- Enhanced directory creation with try/except
- Verifies directory was actually created
- Better error messages with actionable steps

---

### 2. Check if Repo Exists on GitHub

**Before:** Always tried to create new repo, failed if existed

**After:**
```
1. Check if repo exists on GitHub
2. If exists:
   - Private → Link automatically ✅
   - Public → ⚠️ WARNING + require explicit confirm
3. If doesn't exist → Create new (private by default)
```

---

### 3. Security Warning for Public Repos

**Warning displayed:**
```
⚠️  WARNING: Repository is PUBLIC!

Your configs may contain:
  • API keys
  • Auth tokens
  • MCP credentials

Continue with public repository? [y/N]: n
```

**Default:** `N` (safe by default)

**Why:** Config files may contain sensitive data. Public repos expose everything.

---

## 🔒 Security Improvements

| Scenario | Old Behavior | New Behavior |
|----------|-------------|--------------|
| Repo exists (private) | ❌ Error | ✅ Auto-link |
| Repo exists (public) | ❌ Error | ⚠️ Warning + confirm |
| Repo doesn't exist | ✅ Create | ✅ Create (private default) |
| Directory can't be created | ❌ Crash | ✅ Clear error message |

---

## Installation

```bash
pipx upgrade agent-sync
```

---

## What Changed

### `init` Command Flow

**First time (repo doesn't exist):**
```bash
agent-sync init
# → Creates PRIVATE repo on GitHub
# → Clones locally
# → Pushes initial structure
# → Done ✅
```

**Repo already exists (private):**
```bash
agent-sync init --name my-configs
# → Detects existing repo
# → Links automatically
# → Done ✅
```

**Repo already exists (public):**
```bash
agent-sync init --name my-configs
# → Detects existing repo
# → ⚠️ WARNING: Repository is PUBLIC!
# → Your configs may contain: API keys, tokens...
# → Continue with public repository? [y/N]:

# If 'n':
❌ Aborted. Use private repo for configs.

# If 'y':
→ Links anyway (user accepts risk)
```

---

## Recommendation

**ALWAYS use private repositories for agent-sync configs.**

GitHub private repos are:
- ✅ FREE for personal use
- ✅ Unlimited collaborators
- ✅ Full feature set

Public repos should ONLY be used for:
- Sharing non-sensitive configs (e.g., public skills)
- Open source agent configurations

---

## Full Changelog

See [CHANGELOG.md](https://github.com/renatocaliari/agent-sync/blob/main/CHANGELOG.md)

---

## Support

- **Issues:** [GitHub Issues](https://github.com/renatocaliari/agent-sync/issues)
- **Discussions:** [GitHub Discussions](https://github.com/renatocaliari/agent-sync/discussions)
