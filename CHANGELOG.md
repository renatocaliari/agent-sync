# Changelog

All notable changes to this project will be documented in this file.

---

## [0.6.2] - 2026-03-04

### Fixed
- `_stage_skills()` now removes skills deleted from `~/.agents/skills/`
- `_stage_agent_configs()` now removes configs deleted locally (e.g., `.json` vs `.jsonc`)
- `pull()` console import moved to function level (fixes undefined error)

### Changed
- `push --skills-only` now syncs deletions (not just additions)
- `push --configs-only` now syncs deletions (not just additions)

### Use Cases Fixed
- Delete skill locally → removed from repo on push ✅
- Delete config file locally → removed from repo on push ✅
- Example: remove `opencode.json`, keep `opencode.jsonc` → repo updated ✅

---

## [0.6.1] - 2026-03-04

### Added
- `push --skills-only` - Push only skills (not configs)
- `push --configs-only` - Push only configs (not skills)
- `pull --skills-only` - Pull only skills (not configs)
- `pull --configs-only` - Pull only configs (not skills)

### Changed
- Updated README with new push/pull options

---

## [0.5.2] - 2026-03-04

### Fixed
- Critical: repo directory creation with error handling and verification
- Check if repo exists on GitHub before creating
- Security warning for public repos with explicit confirmation
- Default to NO for public repo confirmation (safe by default)

### Changed
- `init_repo()` now links to existing repos automatically (if private)
- Public repos require explicit user confirmation with security warning
- Better error messages for directory creation failures

---

## [0.5.1] - 2026-03-04

### Fixed
- Create repo directory before use (critical error on `init`)
- Filter `.DS_Store` and hidden files in skill scan
- Fix step numbering in wizard (Step 6 was duplicated)
- `get_summary()` counting all files instead of valid skills

### Changed
- Add symlink support for Gemini CLI (was using fallback copy)
- Verify symlink creation before returning success
- Fall through to other methods if symlink fails

---

## [0.5.0] - 2026-03-04

### Added
- `agent-sync config repo` - View/set repository without wizard
- `init --force` - Override existing config

### Security
- `init` blocks if already configured (prevents accidental overwrite)

---

## [0.4.0] - 2026-03-04

### Added
- `skills centralize --distribute` - Copy skills to all agent directories

### Fixed
- Native agents (pi.dev, qwen) receiving duplicate skill copies

---

## [0.3.0] - 2026-03-04

### Added
- Cross-platform paths (Linux, macOS, Windows)
- Pi.dev extensions/prompts/themes sync
- Version management (`--version`, `check-update`)

### Fixed
- Secrets sync UI removed (never implemented)

---

## [0.2.0] - 2026-03-04

### Added
- Initial release
