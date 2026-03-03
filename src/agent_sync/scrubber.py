"""Secret scrubbing for agent-sync.

Automatically detects and removes sensitive data from config files
before syncing to GitHub.
"""

import re
import os
from pathlib import Path
from typing import Optional
from dotenv import set_key, load_dotenv


class SecretScrubber:
    """Automatically scrubs secrets from config content."""
    
    # Patterns that indicate sensitive data
    SECRET_PATTERNS = [
        # Bearer tokens
        (r'("Authorization"\s*:\s*"Bearer\s+)([^"]+)(")', "BEARER_TOKEN"),
        # API keys
        (r'("api[_-]?key"\s*:\s*")([^"]+)(")', "API_KEY"),
        (r'("apiKey"\s*:\s*")([^"]+)(")', "API_KEY"),
        # Tokens
        (r'("token"\s*:\s*")([^"]+)(")', "TOKEN"),
        (r'("access[_-]?token"\s*:\s*")([^"]+)(")', "ACCESS_TOKEN"),
        (r'("refresh[_-]?token"\s*:\s*")([^"]+)(")', "REFRESH_TOKEN"),
        # Secrets
        (r'("secret"\s*:\s*")([^"]+)(")', "SECRET"),
        (r'("client[_-]?secret"\s*:\s*")([^"]+)(")', "CLIENT_SECRET"),
        # Passwords
        (r'("password"\s*:\s*")([^"]+)(")', "PASSWORD"),
        # Private keys (partial match)
        (r'("private[_-]?key"\s*:\s*")([^"]{20,})(")', "PRIVATE_KEY"),
        # Generic keys
        (r'("key"\s*:\s*")([^"]{16,})(")', "KEY"),
    ]
    
    def __init__(self):
        self.env_file = Path.home() / ".config" / "agent-sync" / ".env"
        self.env_file.parent.mkdir(parents=True, exist_ok=True)
        self.scrubbed_secrets: dict[str, str] = {}
    
    def scrub(self, content: str, agent_name: str = "unknown") -> tuple[str, dict[str, str]]:
        """Scrub secrets from content.
        
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
                
                # Generate unique env var name
                env_name = f"AGENT_SYNC_{agent_name.upper()}_{secret_type}_{counter}"
                counter += 1
                
                # Store secret
                secrets[env_name] = secret_value
                
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
        for key, value in secrets.items():
            set_key(self.env_file, key, value)
    
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
