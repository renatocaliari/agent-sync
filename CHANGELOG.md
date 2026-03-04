# Changelog

All notable changes to this project will be documented in this file.

---

## [0.5.0] - 2026-03-04

### Added
- `agent-sync skills publish` - Publish skills to public GitHub repository
  - Interactive TUI to select skills
  - Dry-run mode (`--dry-run`)
  - Separate config (`~/.config/agent-sync/publish.yaml`)
  - Auto-creates public GitHub repo
  - Generates README with install instructions

### Security
- Only SKILL.md files published (no configs, no API keys)
- Explicit confirmation required (default: NO)
- Warns if repo is private
- Auto .gitignore blocks configs/secrets

---

## [0.4.0] - 2026-03-04

### Added
- `agent-sync config repo` - View/set repository without wizard
- `init --force` - Override existing config

### Security
- `init` blocks if already configured (prevents accidental overwrite)

---

## [0.3.0] - 2026-03-04

### Added
- `skills centralize --distribute` - Copy skills to all agent directories

### Fixed
- Native agents (pi.dev, qwen) receiving duplicate skill copies

---

## [0.2.0] - 2026-03-04

### Added
- Cross-platform paths (Linux, macOS, Windows)
- Pi.dev extensions/prompts/themes sync
- Version management (`--version`, `check-update`)

### Fixed
- Secrets sync UI removed (never implemented)

---

## [0.1.0] - 2024-01-01

### Added
- Initial release
