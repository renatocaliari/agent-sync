# Agent Sync for Gemini CLI

Sync your Gemini CLI configurations across machines using agent-sync.

## Quick Start

```bash
# Install
pip install agent-sync

# Initialize (first machine)
agent-sync init --name gemini-configs --agents gemini-cli

# Link (other machines)
agent-sync link https://github.com/username/gemini-configs.git
```

## Commands

```bash
# Pull latest configs
agent-sync pull

# Push changes
agent-sync push -m "updated gemini config"

# Check status
agent-sync status
```

## Integration

Add to your Gemini CLI config:

```json
{
  "tools": {
    "agent-sync": {
      "enabled": true,
      "path": "~/.config/gemini-cli/tools/agent-sync"
    }
  }
}
```
