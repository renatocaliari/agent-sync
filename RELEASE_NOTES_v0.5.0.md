# 🔄 agent-sync v0.5.0

**Released:** March 4, 2026

---

## 🎉 What's New: Publish Your Skills!

This release introduces **`agent-sync skills publish`** - a secure way to share your custom skills with the community!

---

## ✨ New Command: `skills publish`

### Share Your Skills with the World

```bash
# Interactive mode (recommended)
agent-sync skills publish --interactive

# Dry run (preview what would be published)
agent-sync skills publish --dry-run

# Publish to specific repository
agent-sync skills publish --repo https://github.com/user/my-skills
```

### What It Does

1. **Scans** your `~/.agents/skills/` directory
2. **Lets you select** which skills to publish (TUI)
3. **Validates** only skill files (NO configs, NO API keys)
4. **Creates** a public GitHub repository (if doesn't exist)
5. **Publishes** your skills with a generated README
6. **Enables** others to install with: `npx skills add <your-username>/<repo>`

---

## 🛡️ Security First

### What WILL Be Published

```
✓ SKILL.md files (skill definitions)
✓ .md, .py, .sh files (skill scripts)
✓ references/ directory (documentation)
✓ templates/ directory (templates)
✓ scripts/ directory (automation scripts)
```

### What Will NEVER Be Published

```
✗ Config files (settings.json, config.yaml, etc.)
✗ Files containing 'auth', 'token', 'key', 'secret' in name
✗ .env files
✗ Your private agent-sync-configs repository
```

### Safety Features

| Feature | Description |
|---------|-------------|
| **Explicit confirmation** | Default is **NO** - you must explicitly confirm |
| **Separate config** | Uses `~/.config/agent-sync/publish.yaml` (not your main config) |
| **Visibility warning** | Warns if repo is private (others can't install) |
| **Auto .gitignore** | Blocks configs, secrets, auth files automatically |
| **Dry-run mode** | Preview before publishing with `--dry-run` |

---

## 📊 Workflow

### Publish Your Skills

```bash
# Step 1: Interactive selection
agent-sync skills publish --interactive

# Output:
📤 Select Skills to Publish

Skills found:
  [✓] 1. agent-browser
  [✓] 2. docker-deploy
  [○] 3. internal-tool (not a valid skill - no SKILL.md)

Toggle skills (e.g., '1,3,5' or 'all' or 'none' or 'done') [done]: done

📋 Skills to Publish
┌────────┬─────────────────┬──────────────────────────────┐
│ Status │ Skill Name      │ Path                         │
├────────┼─────────────────┼──────────────────────────────┤
│ ✓      │ agent-browser   │ /Users/user/.agents/skills/… │
│ ✓      │ docker-deploy   │ /Users/user/.agents/skills/… │
└────────┴─────────────────┴──────────────────────────────┘

⚠️  SECURITY WARNING
You are about to publish skills to a PUBLIC repository.

What WILL be published:
  ✓ SKILL.md files (skill definitions)
  ✓ .md, .py, .sh files (skill scripts)
  ...

What will NEVER be published:
  ✗ Any config files
  ✗ Any files containing 'auth', 'token', 'key', 'secret'
  ...

Confirm publishing to PUBLIC repository? [y/N]: y

✓ Successfully published 2 skills!

📦 Repository: https://github.com/user/my-skills

💡 Others can now install your skills with:
  npx skills add user/my-skills
```

### Install Someone Else's Skills

```bash
# Install skills from a public repository
npx skills add user/my-skills
```

---

## 🔒 Two-Repository Model

### Private Repository (agent-sync-configs)

```
github.com/user/agent-sync-configs (PRIVATE)
├── configs/          # Your personal configs
│   ├── opencode/
│   ├── claude-code/
│   └── ...
└── skills/           # Your skills backup
```

**Purpose:** Sync your personal configs across YOUR machines.

**Access:** Only YOU (private).

---

### Public Repository (my-skills)

```
github.com/user/my-skills (PUBLIC)
├── skills/           # Skills you want to SHARE
│   ├── agent-browser/
│   ├── docker-deploy/
│   └── ...
└── README.md         # Auto-generated with install instructions
```

**Purpose:** Share your custom skills with the COMMUNITY.

**Access:** EVERYONE (public).

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

### Publish All Valid Skills

```bash
agent-sync skills publish
```

### Select Skills Interactively

```bash
agent-sync skills publish --interactive
```

### Preview Before Publishing

```bash
agent-sync skills publish --dry-run
```

### Publish to Specific Repository

```bash
agent-sync skills publish --repo https://github.com/user/my-skills
```

### Full Workflow

```bash
# 1. Centralize your skills
agent-sync skills centralize

# 2. Preview what would be published
agent-sync skills publish --dry-run

# 3. Select skills interactively and publish
agent-sync skills publish --interactive

# 4. Share with others
# Tell them to run: npx skills add user/my-skills
```

---

## 🙏 Community

This feature enables the **agent-sync skills ecosystem**!

### For Skill Creators

- Share your custom skills with the community
- Get recognition for your work
- Help others automate their workflows

### For Skill Users

- Discover skills from other users
- Install with one command: `npx skills add`
- Fork and modify skills

---

## 📋 Full Changelog

See [CHANGELOG.md](https://github.com/renatocaliari/agent-sync/blob/main/CHANGELOG.md) for complete details.

---

## 📞 Support

- **Issues:** [GitHub Issues](https://github.com/renatocaliari/agent-sync/issues)
- **Discussions:** [GitHub Discussions](https://github.com/renatocaliari/agent-sync/discussions)

---

## 🔜 Coming Soon

- Browse public skills catalog
- Rate and review skills
- Skill dependencies
- Auto-update installed skills

---

**Happy sharing! 🎉**
