# Release Notes: v0.7.0

## 🚀 Major Architectural Evolution: YAML-Driven Registry

We are proud to announce **agent-sync v0.7.0**, featuring a complete rewrite of the agent management system. This update moves from hardcoded Python logic to a flexible, data-driven architecture using a YAML registry.

### 🎯 Key Highlights

- **YAML-Driven Agents**: All AI agent definitions (Opencode, Claude Code, Gemini CLI, etc.) are now defined in `agent_registry.yaml`. This makes it incredibly easy to add support for new agents without changing the core code.
- **Removed Symlink Fallback**: We've removed symlink support to improve cross-platform robustness and avoid permission issues. The new synchronization flow is:
  1. **Native**: Direct read from `~/.agents/skills/`.
  2. **Config**: Update the agent's own config file (e.g., `opencode.json`) with the global path.
  3. **Copy**: Physical copy to the agent's local directory (fallback).
- **User Overrides**: You can now override the `skills_method` for any agent in your `config.yaml`. Want to force Claude Code to use a copy method instead of searching natively? Now you can!
- **Dynamic Config Updates**: For agents using the `config` method, `agent-sync` now uses dot-notation to navigate and update JSON config files dynamically.

### 🛠️ Technical Improvements

- **Refactored `BaseAgent`**: A cleaner, generic base class that implements the logic defined in the registry.
- **Improved CLI**: The `agent-sync agents` command now displays the `Skills Method` being used for each agent.
- **New Documentation**: Added a comprehensive guide on [how to add new agents](docs/adding-agents.md) using the YAML registry.

### 🧹 Migration Guide

If you are upgrading from `v0.6.3`:

1. Update the CLI: `pip install -U agent-sync`.
2. Re-run centralization to apply the new architecture:
   ```bash
   agent-sync skills centralize
   ```
3. Verify your configuration with:
   ```bash
   agent-sync agents
   ```

The system will automatically detect and save the successful synchronization method to your local `config.yaml`.

---
*For the full list of changes, see the [Changelog](CHANGELOG.md).*
