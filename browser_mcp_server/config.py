"""Configuration and environment utilities for the browser MCP server."""

import os
from typing import Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class BrowserConfig:
    """Configuration for browser automation."""
    
    # Browser settings
    browser_type: str = "chrome"  # chrome, firefox, edge
    headless: bool = False
    timeout: int = 30
    window_size: str = "1920x1080"
    user_agent: Optional[str] = None
    download_dir: str = "/tmp/downloads"
    
    # Server settings
    server_name: str = "Browser Automation MCP Server"
    server_version: str = "0.1.0"
    
    @classmethod
    def from_env(cls) -> 'BrowserConfig':
        """Create configuration from environment variables."""
        return cls(
            browser_type=os.getenv('BROWSER_TYPE', 'chrome').lower(),
            headless=os.getenv('BROWSER_HEADLESS', 'true').lower() == 'true',
            timeout=int(os.getenv('BROWSER_TIMEOUT', '30')),
            window_size=os.getenv('BROWSER_WINDOW_SIZE', '1920x1080'),
            user_agent=os.getenv('BROWSER_USER_AGENT'),
            download_dir=os.getenv('BROWSER_DOWNLOAD_DIR', '/tmp/downloads'),
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        return {
            'browser_type': self.browser_type,
            'headless': self.headless,
            'timeout': self.timeout,
            'window_size': self.window_size,
            'user_agent': self.user_agent,
            'download_dir': self.download_dir,
        }


# Global configuration instance
config = BrowserConfig.from_env()