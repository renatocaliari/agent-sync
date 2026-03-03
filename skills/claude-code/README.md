# Agent Sync for Claude Code

Use `agent-sync` commands directly in Claude Code to sync your configurations.

## Setup

```bash
# Install agent-sync CLI
pip install agent-sync

# Link your sync repository
agent-sync link https://github.com/username/my-agent-configs.git
```

## Usage in Claude Code

### Initialize Sync (First Machine)

```
/agent-sync init --name my-configs --private
```

### Link to Existing Repository

```
/agent-sync link https://github.com/username/my-configs.git
```

### Pull Latest Configs

```
/agent-sync pull
```

### Push Your Changes

```
/agent-sync push -m "feat: add new command"
```

### Check Status

```
/agent-sync status
```

## Available Commands

| Command | Description |
|---------|-------------|
| `/agent-sync init` | Create new sync repo |
| `/agent-sync link` | Link to existing repo |
| `/agent-sync pull` | Download configs |
| `/agent-sync push` | Upload changes |
| `/agent-sync status` | Show sync status |
| `/agent-sync agents` | List supported agents |
| `/agent-sync secrets enable` | Enable secrets sync |

## MCP Server Configuration

Add to your `claude.json`:

```json
{
  "mcpServers": {
    "agent-sync": {
      "command": "agent-sync",
      "args": ["mcp-server"]
    }
  }
}
```
