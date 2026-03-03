# Agent Sync for Pi.dev

Keep your Pi.dev skills and configs in sync across all your machines.

## Installation

```bash
pip install agent-sync
```

## Usage

### First Time Setup

```bash
# Initialize sync repository
agent-sync init --name pi-configs --agents pi.dev --private

# Push your current configs
agent-sync push
```

### On Other Machines

```bash
# Link to your repo
agent-sync link https://github.com/username/pi-configs.git

# Download configs
agent-sync pull
```

### Daily Workflow

```bash
# Before working: pull latest
agent-sync pull

# After changes: push updates
agent-sync push -m "updated pi skills"
```

## What Gets Synced

- `~/.config/pi.dev/pi.json` - Main configuration
- `~/.config/pi.dev/skills/` - Custom skills
- `~/.config/pi.dev/prompts/` - Saved prompts (if enabled)

## Secrets Protection

Pi.dev auth tokens are automatically protected:

```json
{
  "auth": {
    "token": "{{env:AGENT_SYNC_PI_TOKEN}}"
  }
}
```

Real value stored locally in `~/.config/agent-sync/.env`.
