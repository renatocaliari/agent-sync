# Changelog

All notable changes to this project will be documented in this file.

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
