# Agent Sync for Qwen Code

Synchronize Qwen Code configurations and skills using agent-sync.

## Setup

```bash
# Install agent-sync
pip install agent-sync

# Initialize (first machine)
agent-sync init --name qwen-configs --agents qwen-code

# Or link to existing repo
agent-sync link https://github.com/username/qwen-configs.git
```

## Commands

### Sync Operations

```bash
# Download latest configs
agent-sync pull

# Upload your changes
agent-sync push -m "added new skills"

# Check sync status
agent-sync status

# List all agents
agent-sync agents
```

### Secrets Management

```bash
# Enable secrets (use private repo!)
agent-sync secrets enable

# Disable secrets
agent-sync secrets disable
```

## File Structure

Your Qwen Code configs will be synced to:

```
repo/
└── configs/
    └── qwen-code/
        ├── qwen.json
        └── settings.json
└── skills/
    └── qwen-code/
        ├── custom-skill-1.py
        └── custom-skill-2.py
```

## Local Overrides

For machine-specific settings, create `~/.config/agent-sync/overrides.yaml`:

```yaml
qwen-code:
  custom_path: /opt/qwen/custom
  local_setting: true
```

These overrides are never synced.
