V0.13.0 - EXTENSION SUBDIRECTORY AND SYMLINK SUPPORT

2026-03-06
renatocaliari
v0.13.0
37bad68

----------------------------------------

🎉 NEW FEATURE

Support for agent extensions that create subdirectories with skills (e.g., Opencode Superpowers, Cursor extensions).

BEFORE:

~/.config/opencode/superpowers/skills/  ❌ Not detected
skills/superpowers → symlink             ❌ Removed on centralize

AFTER:

~/.config/opencode/superpowers/skills/  ✅ Auto-detected
skills/superpowers → ../superpowers/skills/  ✅ Preserved

CHANGES

 * Detect extension subdirectories automatically
 * Preserve symlinks pointing to internal extension directories
 * Remove symlinks pointing to external directories (~/.agents/skills/)
 * Create .agent-sync-manifest.json to track extension metadata
 * Restore extension skills and symlinks on pull
 * Support skills with special characters (__, -) without parsing issues
 * Add 16 tests for extension support

IMPACT

 * ✅ Opencode Superpowers skills backed up and synced
 * ✅ Cursor extensions supported
 * ✅ Multiple extensions work simultaneously
 * ✅ No breaking changes to existing workflows

----------------------------------------

Full Changelog: v0.12.4...v0.13.0
