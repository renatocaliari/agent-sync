# Agent CLI Configuration Paths

This document lists the exact paths used by each agent CLI, based on official documentation.

---

## Opencode

**Documentation:** https://opencode.ai/docs/

### Paths

| Type | Path | Description |
|------|------|-----------|
| Config | `~/.config/opencode/opencode.json` | Main configuration |
| Skills | `~/.config/opencode/skills/` | Global skills |
| Tools | `~/.config/opencode/tools/` | Custom tools |
| Commands | `~/.config/opencode/commands/` | Custom commands |
| Plugins | `~/.config/opencode/plugins/` | Plugins |
| Modes | `~/.config/opencode/modes/` | Custom modes |
| Themes | `~/.config/opencode/themes/` | Themes |
| Agents | `~/.config/opencode/agents/` | Agent configs |

### Project

In project directory: `.opencode/`

```
.opencode/
├── opencode.json
├── skills/
├── tools/
├── commands/
└── modes/
```

### Notes

- Plural names are standard (`skills/`, `tools/`, `commands/`)
- Singular names also work for backwards compatibility
- Skills are `SKILL.md` files inside subdirectories

---

## Claude Code

**Documentation:** https://code.claude.com/docs/

### Paths

| Type | Path | Description |
|------|------|-----------|
| Config | `~/.claude/settings.json` | Main configuration |
| Commands | `~/.claude/commands/` | Custom commands/skills |
| Worktrees | `<repo>/.claude/worktrees/` | Per-repository worktrees |

### Project

In project directory: `.claude/`

```
.claude/
├── settings.json
└── commands/
```

### Notes

- Settings can be loaded via `--settings ./settings.json`
- Custom commands are `.md` or `.sh` files in `commands/` directory
- Worktrees are specific per repository

---

## Gemini CLI

**Documentation:** https://gemini-cli-docs.pages.dev/

### Paths

| Type | Path | Description |
|------|------|-----------|
| Config | `~/.gemini/settings.json` | User configuration |
| Project Config | `.gemini/settings.json` | Project configuration |
| Tools | `.gemini/` | Custom tool scripts |
| Sandbox | `.gemini/sandbox-*.sb` | Custom sandbox profiles |

### System

| OS | Path |
|----|------|
| Linux | `/etc/gemini-cli/settings.json` |
| Windows | `C:\ProgramData\gemini-cli\settings.json` |
| macOS | `/Library/Application Support/GeminiCli/settings.json` |

### Project

```
.gemini/
├── settings.json
├── sandbox.Dockerfile
└── bin/
    ├── get_tools
    └── call_tool
```

### Notes

- User config overrides system config
- Project config overrides user config
- Custom tools can be in `bin/` inside `.gemini/`

---

## Pi.dev

**Documentation:** https://github.com/badlogic/pi-mono

### Paths

| Type | Path | Description |
|------|------|-----------|
| Config | `~/.pi/settings.json` | Global configuration |
| Global Skills | `~/.pi/agent/skills/` | Global skills |
| Global Skills | `~/.agents/skills/` | Shared skills |
| Project Skills | `.pi/skills/` | Project skills |
| Project Skills | `.agents/skills/` | Project skills (ancestors) |

### Project

```
.pi/
├── settings.json
└── skills/
    └── skill-name/
        └── SKILL.md
```

### Notes

- Skills are directories containing a `SKILL.md` file
- Pi.dev searches for skills in multiple paths (most specific to most general)
- `~/.agents/skills/` is shared with other agents
- npm package skills are also supported via `package.json`

---

## Qwen Code

**Documentation:** https://qwenlm.github.io/qwen-code-docs/

### Paths

| Type | Path | Description |
|------|------|-----------|
| Config | `~/.qwen/settings.json` | User configuration |
| Skills | `~/.qwen/skills/` | Global skills |
| Agents | `~/.qwen/agents/` | Agent configs |
| Project Config | `.qwen/settings.json` | Project configuration |
| Project Skills | `.qwen/skills/` | Project skills |

### Project

```
.qwen/
├── settings.json
├── skills/
│   └── skill-name/
│       └── SKILL.md
└── agents/
```

### Notes

- Skills are directories with `SKILL.md` file
- Config is searched from current directory up to git root
- `--experimental-skills` flag enables skills support
- `~/.agents/skills/` is also supported

---

## Global Skills (~/.agents/skills/)

This directory is **shared** across multiple agents:

| Agent | Supports |
|-------|----------|
| Opencode | ✅ (via config) |
| Claude Code | ❌ |
| Gemini CLI | ❌ |
| Pi.dev | ✅ (native) |
| Qwen Code | ✅ (native) |

### Structure

```
~/.agents/skills/
├── skill-1/
│   └── SKILL.md
├── skill-2/
│   └── SKILL.md
└── skill-3/
    └── SKILL.md
```

### Usage with agent-sync

```bash
# Enable sync
agent-sync enable global-skills

# Add skill
mkdir ~/.agents/skills/my-skill
echo "# My Skill" > ~/.agents/skills/my-skill/SKILL.md

# Sync
agent-sync push
```

---

## agent-sync Paths Summary

```python
# Opencode
config: ~/.config/opencode/opencode.json
skills: ~/.config/opencode/skills/

# Claude Code
config: ~/.claude/settings.json
skills: ~/.claude/commands/

# Gemini CLI
config: ~/.gemini/settings.json
skills: ~/.gemini/tools/

# Pi.dev
config: ~/.pi/settings.json
skills: ~/.pi/agent/skills/

# Qwen Code
config: ~/.qwen/settings.json
skills: ~/.qwen/skills/

# Global
skills: ~/.agents/skills/
```
