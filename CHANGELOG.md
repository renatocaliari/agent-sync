# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [0.4.0] - 2026-03-04

### ✨ Added
- **`agent-sync config repo` command** - View/set repository URL without wizard
  - View: `agent-sync config repo`
  - Set: `agent-sync config repo https://github.com/user/repo.git`
  - Remove: `agent-sync config repo --remove`
- **Safety check on `init`** - Prevents accidental overwrite of existing config
  - Detects existing repository and shows helpful options
  - `--force` flag to override and re-initialize
  - Clear error messages with suggested commands

### 🔧 Changed
- **`init` command** - Now requires `--force` if already configured
- **Documentation** - Updated README with `config repo` and `init --help` examples

### 🛡️ Security
- **Prevents accidental repository overwrite** - `init` won't overwrite without explicit `--force`
- **Clear separation of concerns** - `config repo` for linking, `init` for creating new

---

## [0.3.0] - 2026-03-04

### ✨ Added
- **`--distribute` option for `skills centralize` command**
  - Copy all skills from `~/.agents/skills/` to ALL agent directories
  - Use cases:
    - **Backup**: Local copies in each agent directory
    - **Testing**: Verify agents read from local vs global
    - **Debug**: Troubleshoot symlink/config issues
  - Idempotent: Skips existing skills unless they differ
  - Works with all agents (including native pi.dev, qwen-code)

### 🐛 Fixed
- **Native agents (pi.dev, qwen-code) receiving duplicate skill copies**
  - BUG: `_configure_agent()` was not checking `supports_native()` before fallback copy
  - IMPACT: Skills were duplicated in `~/.pi/agent/skills/` and `~/.qwen/skills/` (24 skills each)
  - FIX: Added `supports_native()` check before fallback in `_configure_agent()`
  - FIX: Added `_cleanup_native_agents_skills()` to remove previously copied duplicates
  - RESULT: Native agents now correctly use `~/.agents/skills/` directly without local copies

### 🔧 Changed
- **`configure_agents()` output** - Now shows method used per agent:
  - `symlink` - Claude Code
  - `config` - Opencode
  - `native` - Pi.dev, Qwen Code (no copy needed)
  - `fallback` - Gemini CLI (only agent requiring copy)
- **Documentation** - Added `--distribute` option to README and CLI help

---

## [0.2.1] - 2026-03-04

### 🐛 Fixed
- **Native agents (pi.dev, qwen-code) receiving duplicate skill copies**
  - BUG: `_configure_agent()` was not checking `supports_native()` before applying fallback copy
  - IMPACT: Skills were duplicated in `~/.pi/agent/skills/` and `~/.qwen/skills/` (24 skills each)
  - FIX: Added `supports_native()` check before fallback in `_configure_agent()`
  - FIX: Added `_cleanup_native_agents_skills()` to remove previously copied duplicates
  - RESULT: Native agents now correctly use `~/.agents/skills/` directly without local copies

### 🔧 Changed
- **`configure_agents()` output** - Now shows method used per agent:
  - `symlink` - Claude Code
  - `config` - Opencode
  - `native` - Pi.dev, Qwen Code (no copy needed)
  - `fallback` - Gemini CLI (only agent requiring copy)

---

## [0.2.0] - 2026-03-04

### ✨ Added
- **Cross-platform support** - Proper paths for Linux, macOS, and Windows using `platformdirs`
  - Linux: `~/.local/share/agent-sync/`, `~/.config/agent-sync/`
  - macOS: `~/Library/Application Support/agent-sync/`
  - Windows: `~\AppData\Roaming\agent-sync\`, `~\AppData\Local\agent-sync\`
- **`skills centralize` command** with new options:
  - `--copy` - Copy skills instead of moving
  - `--push` - Automatically push to GitHub after centralizing
- **Pi.dev full support**:
  - Sync extensions (`~/.pi/agent/extensions/` and `~/.pi/extensions/`)
  - Sync prompts (`~/.pi/agent/prompts/`)
  - Sync themes (`~/.pi/agent/themes/`)
- **Version management**:
  - `agent-sync --version` - Show current version
  - `agent-sync check-update` - Check for available updates
  - Async update notifications on `push` and `pull` commands
- **Private repository support** for update checks with `GITHUB_TOKEN`
- **Detailed centralize reports** showing:
  - Skills moved/copied count
  - Conflicts resolved with agent prefix renaming
  - User symlinks cleaned up from agent directories

### 🔧 Changed
- **Setup wizard streamlined** - Removed unused secrets sync UI (step 7)
  - Secrets sync was never implemented, configs sync as-is
  - Wizard now has 7 steps instead of 8
- **Documentation consolidated**:
  - Removed `/docs` directory (1160 lines)
  - Added CLI `--help` output to README
  - Added "Most Used Commands" section to README
  - Added "Agent Configuration Paths" section to README
  - Added "Reconfiguration" section to README
- **Config display simplified** - Removed secrets section from `agent-sync config show`
- **Skills flow improved**:
  - Default behavior is now `--move` (not `--copy`)
  - Automatic conflict detection and resolution
  - Idempotent centralization (skip if already exists)

### 🐛 Fixed
- **Claude Code fallback symlink path** - Correct handling when symlink not supported
- **Pi.dev config path** - Changed from `~/.pi/` to `~/.pi/agent/`
- **Secret scrubber** - Only scrub MCP secrets, not native agent API keys
- **Secrets with hyphens** - Proper handling of environment variable names with hyphens

### 📚 Documentation
- Translated all documentation to English
- Updated README with progressive disclosure and visual improvements
- Added detailed config file paths per agent
- Removed unnecessary PyPI installation note (GitHub only for now)
- Clarified CLI vs skill installation (skill is documentation only)

### 🧹 Removed
- **Secrets sync UI** - Removed unused `include_secrets` and `include_mcp_secrets` options
- **Scrubber logic** - Configs now sync as-is (users should use private repos)
- **`/docs` directory** - Content moved to README for better discoverability
- **Unnecessary agent skill directories** - Only `agent-sync` skill needed

---

## [0.1.0] - 2024-01-01

### Added
- Initial release
- Basic sync functionality
- Multi-agent support
- Secrets protection
