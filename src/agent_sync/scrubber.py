"""Secret scrubbing for agent-sync.

Automatically detects and removes sensitive data from config files
before syncing to GitHub.

Only scrubs:
- MCP server Authorization headers (Bearer tokens)
- Generic API keys in MCP configs

Does NOT scrub:
- Native agent API keys (each agent manages their own)
- OAuth tokens (machine-specific)
"""

import re
import os
from pathlib import Path
from typing import Optional
from dotenv import set_key, load_dotenv


class SecretScrubber:
    """Automatically scrubs secrets from config content."""
    
    # Patterns that indicate sensitive data in MCP configs
    # We ONLY scrub MCP-related secrets, not native agent keys
    SECRET_PATTERNS = [
        # MCP Authorization headers (Bearer tokens)
        (r'("Authorization"\s*:\s*"Bearer\s+)([^"]+)(")', "BEARER_TOKEN"),
        # MCP API keys (only in mcpServers context)
        (r'("mcpApiKey"\s*:\s*")([^"]+)(")', "MCP_API_KEY"),
        (r'("mcp_secret"\s*:\s*")([^"]+)(")', "MCP_SECRET"),
    ]
    
    def __init__(self):
        self.env_file = Path.home() / ".config" / "agent-sync" / ".env"
        self.env_file.parent.mkdir(parents=True, exist_ok=True)
        self.scrubbed_secrets: dict[str, str] = {}
    
    def scrub(self, content: str, agent_name: str = "unknown") -> tuple[str, dict[str, str]]:
        """Scrub ONLY MCP-related secrets from content.
        
        Native agent API keys are NOT scrubbed (each agent manages their own).
        
        Args:
            content: Original content with potential secrets
            agent_name: Name of agent (for env var naming)
        
        Returns:
            tuple: (scrubbed_content, secrets_dict)
        """
        scrubbed = content
        secrets = {}
        counter = 0
        
        for pattern, secret_type in self.SECRET_PATTERNS:
            matches = list(re.finditer(pattern, scrubbed, re.IGNORECASE))
            
            for match in reversed(matches):
                prefix = match.group(1)
                secret_value = match.group(2)
                suffix = match.group(3)
                
                # Skip if this looks like a placeholder value (already scrubbed)
                if secret_value.startswith("{{env:") or secret_value.startswith("__PLACEHOLDER_"):
                    continue
                
                # Generate unique env var name
                env_name = f"AGENT_SYNC_{agent_name.upper()}_{secret_type}_{counter}"
                counter += 1
                
                # Store secret (just the value, no quotes)
                secrets[env_name] = secret_value.strip("'\"")
                
                # Replace with placeholder
                replacement = f"{prefix}{{{{env:{env_name}}}}}{suffix}"
                scrubbed = scrubbed[:match.start()] + replacement + scrubbed[match.end():]
        
        self.scrubbed_secrets.update(secrets)
        return scrubbed, secrets
    
    def restore(self, content: str) -> str:
        """Restore secrets from env vars.
        
        Replaces {{env:VAR_NAME}} with actual values from .env file.
        """
        load_dotenv(self.env_file)
        restored = content
        
        # Find all placeholders (support hyphens in env names)
        placeholders = re.findall(r'\{\{env:(AGENT_SYNC_[\w-]+)\}\}', content)
        
        for env_name in set(placeholders):
            value = os.environ.get(env_name)
            if value:
                # Remove quotes if present
                value = value.strip("'\"")
                restored = restored.replace(f"{{{{env:{env_name}}}}}", value)
        
        return restored
    
    def save_secrets(self, secrets: dict[str, str]) -> None:
        """Save secrets to local .env file (never synced)."""
        if not secrets:
            return
        
        # Check if .env already exists
        env_existed = self.env_file.exists()
        
        for key, value in secrets.items():
            set_key(self.env_file, key, value)
        
        # Show warning if this is the first time creating .env
        if not env_existed:
            from rich.console import Console
            console = Console()
            console.print("\n[yellow]⚠️  Secrets saved to ~/.config/agent-sync/.env[/yellow]")
            console.print("  • This file is [bold]NOT synced[/bold] to GitHub")
            console.print("  • [bold]Backup this file[/bold] to avoid losing secrets")
            console.print("  • Use [green]`agent-sync secrets export`[/green] to backup\n")
    
    def scrub_file(self, file_path: Path, agent_name: str = "unknown") -> Optional[dict[str, str]]:
        """Scrub secrets from a file.
        
        Returns:
            dict of secrets found, or None if no secrets
        """
        if not file_path.exists():
            return None
        
        content = file_path.read_text()
        scrubbed, secrets = self.scrub(content, agent_name)
        
        if secrets:
            # Save secrets to .env
            self.save_secrets(secrets)
            
            # Write scrubbed content back
            file_path.write_text(scrubbed)
            
            return secrets
        
        return None
