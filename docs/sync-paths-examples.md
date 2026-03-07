# Agent Sync - Flexible File Sync

## Overview

The new `sync.paths` feature allows you to backup any files from your agent directories, not just config files.

## Configuration Options

### 1. Default (Configs Only)

```yaml
# ~/.config/agent-sync/config.yaml
agents_config:
  opencode:
    sync:
      configs: true  # Default: only config files
```

### 2. Backup Everything

```yaml
agents_config:
  opencode:
    sync:
      configs: true
      all_files: true  # Copy entire agent directory
      exclude:
        - "**/*.lock"
        - "node_modules/**"
        - ".git/**"
        - "**/*.log"
```

### 3. Specific Paths

```yaml
agents_config:
  opencode:
    sync:
      configs: true
      paths:
        - plugins/
        - commands/
        - .opencode/
```

### 4. Glob Patterns

```yaml
agents_config:
  opencode:
    sync:
      configs: true
      paths:
        - "**/*.js"
        - "**/*.json"
        - "plugins/**"
      exclude:
        - "**/*.test.js"
        - "**/__pycache__/**"
```

## Pattern Syntax

### Directory Patterns
- `plugins/` - Copy entire directory
- `commands/` - Copy entire directory

### Glob Patterns
- `**/*.js` - All .js files recursively
- `**/*.json` - All .json files recursively
- `plugins/*.js` - All .js files directly in plugins/
- `commands/*` - All files directly in commands/

### Simple Paths
- `.opencode/` - Hidden directory
- `ocx.jsonc` - Specific file

## Features

✅ **Preserves symlinks** - Symlinks are copied as symlinks  
✅ **Preserves permissions** - File metadata is preserved  
✅ **Supports hidden files** - .dotfiles are included  
✅ **Exclude patterns** - Glob-based exclusions  
✅ **Backward compatible** - Default behavior unchanged  

## Examples

### Example 1: Backup Opencode Superpowers

```yaml
agents_config:
  opencode:
    sync:
      configs: true
      paths:
        - superpowers/
        - plugins/
```

### Example 2: Full Backup with Exclusions

```yaml
agents_config:
  opencode:
    sync:
      configs: true
      all_files: true
      exclude:
        - "**/*.lock"
        - "node_modules/**"
        - ".git/**"
        - "**/cache/**"
        - "**/*.pyc"
```

### Example 3: Multiple Agents

```yaml
agents_config:
  opencode:
    sync:
      configs: true
      all_files: true
      
  claude-code:
    sync:
      configs: true
      paths:
        - ".claude/"
        
  qwen-code:
    sync:
      configs: true  # Default: configs only
```

## Migration

No migration needed! The default behavior is unchanged:
- Existing configs continue to work
- Only config files are synced by default
- Opt-in to new features with `all_files: true` or `paths: [...]`
