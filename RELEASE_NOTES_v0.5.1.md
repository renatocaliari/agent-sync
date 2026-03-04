# agent-sync v0.5.1

**Released:** March 4, 2026

---

## Bug Fixes

### Critical: Repo Directory Not Created
**Error:** `[Errno 2] No such file or directory: ~/Library/Application Support/agent-sync/repo`

**Fix:** Create repo directory before use
```python
self.repo_dir.mkdir(parents=True, exist_ok=True)
```

---

### .DS_Store Appearing in Skill Scan
**Error:** `⚠ .DS_Store differs in gemini-cli, skipping`

**Fix:** Filter hidden files in `scan_all_agents()`
```python
if item.name.startswith("."):
    continue
```

---

### Summary Showing Wrong Skill Count
**Error:** Summary showed 3 skills when 25+ existed

**Fix:** Count only valid skills (directories with SKILL.md)
```python
# Before: Counted ALL files
skill_count = len(list(self.global_skills_dir.glob("*")))

# After: Count only valid skills
for item in self.global_skills_dir.iterdir():
    if item.is_dir() and (item / "SKILL.md").exists():
        skill_count += 1
```

---

### Step Numbering in Wizard
**Error:** Step 6 was duplicated (two Step 5s)

**Fix:** Corrected step numbers
- Step 5: Configure agents
- Step 6: Repository settings
- Step 7: Summary

---

## Improvements

### Gemini CLI Symlink Support
**Before:** Used fallback (copy) method

**After:** Uses symlink (more efficient)
- Creates `~/.gemini/tools/_global` → `~/.agents/skills/`
- Verifies symlink was created successfully
- Falls back to copy if symlink fails

**Agents with symlink support:**
- Claude Code ✅
- Gemini CLI ✅ (new)

---

## Installation

```bash
pipx upgrade agent-sync
```

---

## What's Synced

| Agent | Method | Status |
|-------|--------|--------|
| claude-code | Symlink | ✅ |
| gemini-cli | Symlink | ✅ (new) |
| opencode | Config | ✅ |
| pi.dev | Native | ✅ |
| qwen-code | Native | ✅ |

---

## Full Changelog

See [CHANGELOG.md](https://github.com/renatocaliari/agent-sync/blob/main/CHANGELOG.md)
