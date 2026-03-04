# 🔄 agent-sync v0.4.0

**Released:** March 4, 2026

---

## 🎯 What's New

This release introduces a **safer, more intuitive workflow** for managing your repository configuration, with explicit commands and protection against accidental overwrites.

---

## ✨ New Command: `agent-sync config repo`

### Quick Repository Management

No more running the full wizard just to check or change your repository!

```bash
# View current repository
agent-sync config repo
# Output: 📦 Repository: https://github.com/user/repo.git

# Set repository URL (e.g., on a new machine)
agent-sync config repo https://github.com/user/my-configs.git
# Output: ✓ Repository configured

# Remove repository configuration
agent-sync config repo --remove
# Output: ✓ Repository configuration removed
```

### Use Cases

| Scenario | Command |
|----------|---------|
| **Check repo** | `agent-sync config repo` |
| **Link machine** | `agent-sync config repo <url>` + `agent-sync pull` |
| **Switch repos** | `agent-sync config repo <new-url>` |
| **Unlink** | `agent-sync config repo --remove` |

---

## 🛡️ Safety: `init` Now Requires `--force`

### Before (Risky)
```bash
agent-sync init --name new-repo
# ⚠️ Could accidentally overwrite existing config!
```

### After (Safe)
```bash
agent-sync init --name new-repo
# ⚠ Already configured!
#    Repository: https://github.com/user/existing-repo.git
#
# 💡 Options:
#    - Use 'agent-sync config repo' to view/change repository
#    - Use 'agent-sync setup' to reconfigure agents
#    - Use 'agent-sync init --force' to overwrite existing config

# To force (explicit):
agent-sync init --name new-repo --force
# ⚠ Forcing re-initialization!
#    Existing repository: https://github.com/user/existing-repo.git
#    This will overwrite your local configuration.
```

---

## 📊 Workflow Comparison

### Old Workflow (Confusing)
```bash
agent-sync init          # What does this do? Create? Configure?
agent-sync setup         # Does this overwrite?
# No easy way to just check repo URL
```

### New Workflow (Clear)
```bash
# Check status
agent-sync config repo           # View repo
agent-sync config show           # View full config

# Configure
agent-sync config repo <url>     # Link existing repo
agent-sync init --name X         # Create NEW repo (only if not configured)
agent-sync init --name X --force # Force create (with warning)

# Sync
agent-sync pull
agent-sync push
```

---

## 🔒 Security Improvements

### Protection Against Accidental Overwrite

| Action | Old Behavior | New Behavior |
|--------|-------------|--------------|
| `init` with existing config | ⚠️ Overwrites silently | ✅ Blocks + shows options |
| `init --force` | N/A | ⚠️ Warns before overwriting |
| Change repo URL | ⚠️ Edit config manually | ✅ `config repo <url>` (reversible) |
| Unlink repo | ⚠️ Delete config file | ✅ `config repo --remove` (safe) |

### Explicit Is Safe

The new design follows the principle: **explicit commands for dangerous operations**.

- `config repo` → Safe, reversible
- `init` → Only for NEW repos
- `init --force` → Explicit override with warning

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

## 📚 Examples

### First Machine (Create New Repo)

```bash
# Option 1: Interactive wizard
agent-sync init

# Option 2: Non-interactive
agent-sync init --name my-configs --private --no-wizard
```

### Additional Machines (Link Existing)

```bash
# Option 1: Quick link (recommended)
agent-sync link https://github.com/user/my-configs.git
agent-sync pull

# Option 2: Configure then pull
agent-sync config repo https://github.com/user/my-configs.git
agent-sync pull
```

### Check Status

```bash
# Just the repo URL
agent-sync config repo

# Full configuration
agent-sync config show
```

### Switch to Different Repo

```bash
# Change repository URL
agent-sync config repo https://github.com/user/new-configs.git

# Pull from new repo
agent-sync pull --force  # May be needed if histories differ
```

---

## 📋 Full Changelog

See [CHANGELOG.md](https://github.com/renatocaliari/agent-sync/blob/main/CHANGELOG.md) for complete details.

---

## 📞 Support

- **Issues:** [GitHub Issues](https://github.com/renatocaliari/agent-sync/issues)
- **Discussions:** [GitHub Discussions](https://github.com/renatocaliari/agent-sync/discussions)

---

## 🙏 Acknowledgments

This release improves the user experience based on real-world usage feedback. Thanks to users who reported confusion about the `init` vs `setup` workflow!
