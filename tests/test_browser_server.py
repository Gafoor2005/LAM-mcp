"""Basic tests for the browser MCP server."""

import pytest
import asyncio
from unittest.mock import Mock, patch
import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from browser_mcp_server.browser_utils import BrowserManager
from browser_mcp_server.config import BrowserConfig


class TestBrowserManager:
    """Test the BrowserManager class."""
    
    def test_browser_config_creation(self):
        """Test browser configuration creation."""
        config = BrowserConfig()
        assert config.browser_type == "chrome"
        assert config.headless is True
        assert config.timeout == 30
    
    def test_config_from_env(self):
        """Test configuration from environment variables."""
        with patch.dict(os.environ, {
            'BROWSER_TYPE': 'firefox',
            'BROWSER_HEADLESS': 'false',
            'BROWSER_TIMEOUT': '45'
        }):
            config = BrowserConfig.from_env()
            assert config.browser_type == "firefox"
            assert config.headless is False
            assert config.timeout == 45
    
    def test_browser_manager_init(self):
        """Test BrowserManager initialization."""
        manager = BrowserManager()
        assert manager.driver is None
        assert manager.browser_type in ["chrome", "firefox", "edge"]
    
    @patch('browser_mcp_server.browser_utils.ChromeDriverManager')
    @patch('browser_mcp_server.browser_utils.webdriver.Chrome')
    def test_chrome_browser_start(self, mock_chrome, mock_driver_manager):
        """Test Chrome browser startup."""
        # Mock the driver manager
        mock_driver_manager.return_value.install.return_value = "/path/to/chromedriver"
        
        # Mock the WebDriver
        mock_driver = Mock()
        mock_chrome.return_value = mock_driver
        
        manager = BrowserManager()
        manager.browser_type = "chrome"
        manager.start_browser()
        
        assert manager.driver is not None
        mock_chrome.assert_called_once()


class TestServerFunctions:
    """Test the MCP server tool functions."""
    
    def test_navigate_to_url_validation(self):
        """Test URL navigation input validation."""
        from browser_mcp_server.server import navigate_to_url
        
        # Mock the browser manager
        with patch('browser_mcp_server.server.browser_manager') as mock_manager:
            mock_manager.navigate_to_url.return_value = {
                "success": True,
                "url": "https://example.com",
                "title": "Example Domain"
            }
            
            result = navigate_to_url("https://example.com")
            
            assert result["success"] is True
            assert "url" in result
            assert "title" in result
    
    def test_click_element_function(self):
        """Test click element functionality."""
        from browser_mcp_server.server import click_element
        
        with patch('browser_mcp_server.server.browser_manager') as mock_manager:
            mock_manager.click_element.return_value = {
                "success": True,
                "message": "Successfully clicked element"
            }
            
            result = click_element("#submit-button", "css")
            
            assert result["success"] is True
            mock_manager.click_element.assert_called_once_with("#submit-button", "css")
    
    def test_type_text_function(self):
        """Test text typing functionality."""
        from browser_mcp_server.server import type_text
        
        with patch('browser_mcp_server.server.browser_manager') as mock_manager:
            mock_manager.type_text.return_value = {
                "success": True,
                "message": "Successfully typed text"
            }
            
            result = type_text("#username", "testuser", "css", True)
            
            assert result["success"] is True
            mock_manager.type_text.assert_called_once_with("#username", "testuser", "css", True)


if __name__ == "__main__":
    pytest.main([__file__])