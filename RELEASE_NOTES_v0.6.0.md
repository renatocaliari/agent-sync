# agent-sync v0.6.0

**Released:** March 4, 2026

---

## New Feature: Selective Sync

Push or pull **only skills** or **only configs** instead of everything.

---

## Usage

### Push

```bash
# Push everything (default)
agent-sync push

# Push only skills
agent-sync push --skills-only

# Push only configs
agent-sync push --configs-only
```

### Pull

```bash
# Pull everything (default)
agent-sync pull

# Pull only skills
agent-sync pull --skills-only

# Pull only configs
agent-sync pull --configs-only
```

---

## Use Cases

| Scenario | Command |
|----------|---------|
| Added new skill | `agent-sync push --skills-only` |
| Changed only configs | `agent-sync push --configs-only` |
| Want only skills from another machine | `agent-sync pull --skills-only` |
| Want only configs from another machine | `agent-sync pull --configs-only` |

---

## Benefits

- **Faster sync** when you know what changed
- **More control** over what gets synced
- **Avoid conflicts** by syncing only what you need

---

## Installation

```bash
pipx upgrade agent-sync
```

---

## Full Changelog

See [CHANGELOG.md](https://github.com/renatocaliari/agent-sync/blob/main/CHANGELOG.md)
