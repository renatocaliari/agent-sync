# agent-sync v0.5.0

**Released:** March 4, 2026

---

## New: `skills publish`

Publish selected skills to a public GitHub repository.

```bash
# Interactive mode
agent-sync skills publish --interactive

# Dry run
agent-sync skills publish --dry-run

# Specific repo
agent-sync skills publish --repo https://github.com/user/my-skills
```

---

## Security

**Only skill files published:**
- SKILL.md
- .md, .py, .sh files
- references/, templates/, scripts/ directories

**Never published:**
- Config files (settings.json, config.yaml)
- Files with 'auth', 'token', 'key', 'secret' in name
- .env files

**Safety features:**
- Explicit confirmation required (default: NO)
- Warns if repo is private
- Separate config file (`~/.config/agent-sync/publish.yaml`)
- Auto .gitignore blocks configs/secrets

---

## Installation

```bash
pipx upgrade agent-sync
```

---

## Two-Repository Model

**Private** (`agent-sync-configs`): Your personal configs across your machines.

**Public** (`my-skills`): Skills you share with the community.

---

## Example

```bash
# Publish skills
agent-sync skills publish --interactive

# Others install with:
npx skills add user/my-skills
```
