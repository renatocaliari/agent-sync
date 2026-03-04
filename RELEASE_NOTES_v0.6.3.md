# Release Notes v0.6.3

## 🎯 Major Refactor: Centralized Skills Architecture

### Philosophy Change

**Before:** Skills could exist in multiple places (agent directories + central location)
**After:** Skills exist ONLY in `~/.agents/skills/` (single source of truth)

### Changes

#### 1. `centralize()` now follows strict centralized approach

**What happens:**
1. ✅ Moves ALL skills from ALL agents to `~/.agents/skills/`
2. ✅ Removes ALL local skills from agent directories
3. ✅ Configures agents to use centralized skills via:
   - **Native support** (pi.dev, qwen-code) - reads directly from `~/.agents/skills/`
   - **Config update** (opencode) - adds path to config (PREFERRED method)
   - **Symlink** (claude-code, gemini-cli) - creates `_global` symlink (FALLBACK)
   - **No fallback copy** - agents must use one of the above methods

#### 2. Config is now preferred over symlink

**New priority order:**
1. **Native support** (pi.dev, qwen-code) - fastest, no setup needed
2. **Config update** (opencode) - PREFERRED for explicit configuration
3. **Symlink** (claude-code, gemini-cli) - FALLBACK if config not supported
4. **Error** - no supported method

**Why config is preferred:**
- ✅ **Explicit** - configuration is visible in config file
- ✅ **Debuggable** - easy to see which path is configured
- ✅ **Robust** - survives reinstalls, doesn't break when moving directories
- ✅ **Cross-platform** - works on Windows (symlinks require admin)
- ✅ **Versionable** - can be committed to repo, reproducible
- ✅ **Flexible** - can add multiple paths, mix local + centralized skills

**Fallback behavior:**
- If config fails, automatically tries symlink
- If symlink also fails, returns error
- No silent failures

#### 3. Removed fallback copy behavior

**Old behavior (v0.6.2):**
```python
# If agent doesn't support symlink/config/native, copy skills as fallback
_copy_skills(agent)  # ❌ Creates duplicates!
```

**New behavior (v0.6.3):**
```python
# No fallback - agents must use proper method
# Config preferred, symlink fallback
# Returns error if both fail
```

#### 4. Unified cleanup logic

**Old:**
- `_cleanup_user_symlinks()` - removed user symlinks
- `_cleanup_native_agents_skills()` - removed native agent duplicates
- Scattered cleanup logic

**New:**
- `_cleanup_agent_local_skills()` - unified cleanup for ALL agents
- Called once per agent during configuration
- Ensures no local skills remain

### Migration Guide

**If you have v0.6.2 or earlier:**

```bash
# Option 1: Re-run centralize (recommended)
agent-sync skills centralize

# Option 2: Manual cleanup
rm -rf ~/.qwen/skills/*
rm -rf ~/.pi/agent/skills/*
rm -rf ~/.claude/commands/*  # (except _global symlink)
rm -rf ~/.gemini/tools/*    # (except _global symlink)

# Option 3: Use cleanup script
./scripts/cleanup-duplicates.sh
```

### Technical Details

#### Modified Methods

1. **`_configure_agent()`** - Complete rewrite with new priority
   ```python
   # New priority order
   if agent.supports_native():
       return native_config
   
   if agent.supports_config():
       try:
           update_config()  # Try config first
           return success
       except:
           pass  # Continue to symlink fallback
   
   if agent.supports_symlink():
       try:
           create_symlink()  # Fallback
           return success
       except:
           return error
   
   return error  # No method worked
   ```

2. **`_cleanup_agent_local_skills()`** - NEW
   - Removes all local skills from agent directory
   - Preserves symlinks (like `_global`)
   - Called before configuration

3. **Removed Methods**
   - `_copy_skills()` - no longer needed
   - `_cleanup_native_agents_skills()` - replaced by unified cleanup

#### Agent Configuration Matrix

| Agent | Method | Priority | Fallback? | Local Skills? |
|-------|--------|----------|-----------|---------------|
| opencode | Config | 1st choice | → Symlink (if fails) | ❌ None |
| claude-code | Symlink | 2nd choice | (no config support) | ❌ None |
| gemini-cli | Symlink | 2nd choice | (no config support) | ❌ None |
| pi.dev | Native | 1st choice | N/A | ❌ None |
| qwen-code | Native | 1st choice | N/A | ❌ None |

**Note:** Currently only opencode supports config-based skills paths. Other agents fall back to symlink.

### Breaking Changes

- **No fallback copy**: Agents without native/config/symlink support will error
- **All local skills removed**: Skills only exist in `~/.agents/skills/`
- **Clean agent directories**: No skills in agent-specific paths
- **Config preferred over symlink**: Order changed, but both still work

### Benefits

✅ **Single source of truth** - All skills in one place
✅ **No duplicates** - Saves disk space
✅ **Easier management** - Update once, all agents see changes
✅ **Clear architecture** - Explicit configuration methods with fallback
✅ **Better debugging** - Know exactly where skills are
✅ **Config preferred** - More robust, explicit, cross-platform
✅ **Graceful fallback** - Config fails → tries symlink → error

### Files Changed

- `src/agent_sync/skills.py` - Refactored configuration logic with new priority
- `scripts/cleanup-duplicates.sh` - Cleanup script for migration
- `CHANGELOG.md` - Updated with v0.6.3 changes

### Version

- **Version**: 0.6.3
- **Type**: Major refactor (breaking change)
- **Migration**: Required if upgrading from v0.6.2 or earlier
