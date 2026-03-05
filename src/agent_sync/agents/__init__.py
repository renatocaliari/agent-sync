"""Agent-specific configurations and handlers (YAML-driven)."""

from typing import Optional, List
from .base import BaseAgent, GLOBAL_SKILLS_DIR
from .registry_loader import load_registry


def get_all_agents() -> List[BaseAgent]:
    """Get all available agent integrations from YAML registry."""
    registry = load_registry()
    agents = []
    for name, data in registry.items():
        agents.append(BaseAgent(name, data))
    return agents


def get_agent(name: str) -> Optional[BaseAgent]:
    """Get a specific agent by name."""
    registry = load_registry()
    if name in registry:
        return BaseAgent(name, registry[name])
    return None


def get_enabled_agents() -> List[BaseAgent]:
    """Get only enabled agent integrations."""
    # Note: currently 'enabled' is a runtime state, 
    # but the config could override this in the future.
    return [agent for agent in get_all_agents() if agent.is_enabled()]
