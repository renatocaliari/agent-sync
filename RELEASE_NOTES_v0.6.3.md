# Release Notes v0.6.3

## 🐛 Bug Fixes

### Fixed: Native agents keeping duplicate skills after centralize

**Problem:**
- Running `agent-sync skills centralize` would move skills to `~/.agents/skills/`
- BUT native agents (qwen-code, pi.dev) would still have duplicate copies in their local directories
- These agents already read from `~/.agents/skills/` natively, so local copies are unnecessary

**Solution:**
- `centralize()` now automatically calls `configure_agents()` after moving skills
- This ensures native agents have their local skill copies cleaned up
- Native agents now correctly use only `~/.agents/skills/` (single source of truth)

**Affected Commands:**
- `agent-sync skills centralize`
- `agent-sync skills centralize --copy`

**Impact:**
- ✅ Native agents (qwen-code, pi.dev) will have cleaner directories
- ✅ No more duplicate skills wasting disk space
- ✅ Single source of truth maintained in `~/.agents/skills/`

**Migration:**
If you already ran `centralize` and have duplicates, run:
```bash
# Clean up existing duplicates
rm -rf ~/.qwen/skills/*
rm -rf ~/.pi/agent/skills/*

# Or re-run centralize (it's idempotent)
agent-sync skills centralize
```

## 📝 Technical Details

### Changes
- Modified `skills.py::centralize()` to call `configure_agents()` after centralization
- Ensures `_cleanup_native_agents_skills()` is always executed
- Maintains consistency across all agent types

### Files Changed
- `src/agent_sync/skills.py` - Added `configure_agents()` call in `centralize()` method

## 🔗 Related
- Issue: Native agents keeping duplicate skills
- Commit: fix: clean up native agent skills after centralize
