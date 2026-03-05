"""
agent-sync: Unified CLI to sync configs and skills across multiple AI agents.

Supports: opencode, claude-code, gemini-cli, pi.dev, qwen-code
"""

import importlib.metadata

try:
    __version__ = importlib.metadata.version("agent-sync")
except importlib.metadata.PackageNotFoundError:
    # fallback for development without installation
    __version__ = "0.0.0-dev"
