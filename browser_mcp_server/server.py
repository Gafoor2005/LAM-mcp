"""
Browser Automation MCP Server

This server provides browser automation capabilities through the Model Context Protocol.
It uses Selenium WebDriver to control browsers and perform web interactions.
"""

import logging
import asyncio
from typing import Any, Dict, List, Sequence
import click
import anyio
from mcp.server.fastmcp import FastMCP
from mcp.server.models import InitializationOptions
import mcp.types as types
from mcp.server import NotificationOptions, Server
from mcp.server.models import InitializationOptions
import mcp.server.stdio

from .browser_utils import browser_manager

# Configure logging to stderr to avoid interfering with MCP JSON-RPC communication
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# Create FastMCP server
mcp = FastMCP("Browser Automation Server")


@mcp.tool()
def navigate_to_url(url: str) -> dict:
    """Navigate to a specific URL.
    
    Args:
        url: The URL to navigate to (must include protocol, e.g., https://)
        
    Returns:
        Dictionary with navigation result including success status, current URL, and page title
    """
    logger.info(f"Navigating to: {url}")
    return browser_manager.navigate_to_url(url)


@mcp.tool()
def click_element(selector: str, by_type: str = "css") -> dict:
    """Click on a web element.
    
    Args:
        selector: CSS selector, XPath, or other identifier for the element
        by_type: Type of selector ('css', 'xpath', 'id', 'class', 'tag', 'name', 'link_text')
        
    Returns:
        Dictionary with click result
    """
    logger.info(f"Clicking element: {selector} (by: {by_type})")
    return browser_manager.click_element(selector, by_type)


@mcp.tool()
def type_text(selector: str, text: str, by_type: str = "css", clear_first: bool = True) -> dict:
    """Type text into an input field.
    
    Args:
        selector: CSS selector or other identifier for the input element
        text: Text to type into the field
        by_type: Type of selector ('css', 'xpath', 'id', 'class', 'tag', 'name')
        clear_first: Whether to clear existing text before typing
        
    Returns:
        Dictionary with typing result
    """
    logger.info(f"Typing text into: {selector}")
    return browser_manager.type_text(selector, text, by_type, clear_first)


@mcp.tool()
def get_element_text(selector: str, by_type: str = "css") -> dict:
    """Extract text content from a web element.
    
    Args:
        selector: CSS selector or other identifier for the element
        by_type: Type of selector ('css', 'xpath', 'id', 'class', 'tag', 'name')
        
    Returns:
        Dictionary with extracted text
    """
    logger.info(f"Getting text from element: {selector}")
    return browser_manager.get_element_text(selector, by_type)


@mcp.tool()
def get_page_source() -> dict:
    """Get the full HTML source code of the current page.
    
    Returns:
        Dictionary with the complete HTML source
    """
    logger.info("Getting page source")
    return browser_manager.get_page_source()


@mcp.tool()
def take_screenshot(element_selector: str = None, by_type: str = "css") -> dict:
    """Take a screenshot of the page or a specific element.
    
    Args:
        element_selector: Optional CSS selector for element-specific screenshot
        by_type: Type of selector if element_selector is provided
        
    Returns:
        Dictionary with base64-encoded screenshot data
    """
    if element_selector:
        logger.info(f"Taking screenshot of element: {element_selector}")
    else:
        logger.info("Taking full page screenshot")
    return browser_manager.take_screenshot(element_selector, by_type)


@mcp.tool()
def execute_javascript(script: str) -> dict:
    """Execute JavaScript code in the browser context.
    
    Args:
        script: JavaScript code to execute
        
    Returns:
        Dictionary with execution result
    """
    logger.info(f"Executing JavaScript: {script[:100]}...")
    return browser_manager.execute_javascript(script)


@mcp.tool()
def wait_for_element(selector: str, by_type: str = "css", timeout: int = 30) -> dict:
    """Wait for an element to appear on the page.
    
    Args:
        selector: CSS selector or other identifier for the element
        by_type: Type of selector ('css', 'xpath', 'id', 'class', 'tag', 'name')
        timeout: Maximum time to wait in seconds
        
    Returns:
        Dictionary with wait result
    """
    logger.info(f"Waiting for element: {selector} (timeout: {timeout}s)")
    return browser_manager.wait_for_element(selector, by_type, timeout)


@mcp.tool()
def get_cookies() -> dict:
    """Get all cookies from the current domain.
    
    Returns:
        Dictionary with all cookies
    """
    logger.info("Getting cookies")
    return browser_manager.get_cookies()


@mcp.tool()
def set_cookie(name: str, value: str, domain: str = None, path: str = "/") -> dict:
    """Set a cookie in the browser.
    
    Args:
        name: Cookie name
        value: Cookie value
        domain: Cookie domain (optional, defaults to current domain)
        path: Cookie path (defaults to "/")
        
    Returns:
        Dictionary with result of cookie setting
    """
    logger.info(f"Setting cookie: {name}")
    return browser_manager.set_cookie(name, value, domain, path)


@mcp.tool()
def scroll_page(direction: str = "down", pixels: int = None) -> dict:
    """Scroll the page in the specified direction.
    
    Args:
        direction: Direction to scroll ('up', 'down', 'left', 'right', 'top', 'bottom')
        pixels: Number of pixels to scroll (optional, defaults to full scroll)
        
    Returns:
        Dictionary with scroll result
    """
    logger.info(f"Scrolling page: {direction}")
    return browser_manager.scroll_page(direction, pixels)


@mcp.tool()
def extract_links() -> dict:
    """Extract all links from the current page.
    
    Returns:
        Dictionary with array of links, each containing URL, text, and title
    """
    logger.info("Extracting links from page")
    return browser_manager.extract_links()


@mcp.tool()
def fill_form(form_data: Dict[str, str]) -> dict:
    """Fill out a web form with the provided data.
    
    Args:
        form_data: Dictionary mapping CSS selectors to values
                  e.g., {"#name": "John Doe", "#email": "john@example.com"}
                  
    Returns:
        Dictionary with results for each field
    """
    logger.info(f"Filling form with {len(form_data)} fields")
    return browser_manager.fill_form(form_data)


@mcp.tool()
def get_current_url() -> dict:
    """Get the current page URL and title.
    
    Returns:
        Dictionary with current URL and page title
    """
    logger.info("Getting current URL")
    return browser_manager.get_current_url()


@mcp.tool()
def refresh_page() -> dict:
    """Refresh the current page.
    
    Returns:
        Dictionary with refresh result
    """
    logger.info("Refreshing page")
    try:
        browser_manager.ensure_browser()
        browser_manager.driver.refresh()
        return {
            "success": True,
            "message": "Page refreshed successfully",
            "url": browser_manager.driver.current_url
        }
    except Exception as e:
        logger.error(f"Page refresh failed: {e}")
        return {
            "success": False,
            "error": str(e)
        }


@mcp.tool()
def go_back() -> dict:
    """Navigate back in browser history.
    
    Returns:
        Dictionary with navigation result
    """
    logger.info("Going back in browser history")
    try:
        browser_manager.ensure_browser()
        browser_manager.driver.back()
        return {
            "success": True,
            "message": "Navigated back successfully",
            "url": browser_manager.driver.current_url
        }
    except Exception as e:
        logger.error(f"Going back failed: {e}")
        return {
            "success": False,
            "error": str(e)
        }


@mcp.tool()
def go_forward() -> dict:
    """Navigate forward in browser history.
    
    Returns:
        Dictionary with navigation result
    """
    logger.info("Going forward in browser history")
    try:
        browser_manager.ensure_browser()
        browser_manager.driver.forward()
        return {
            "success": True,
            "message": "Navigated forward successfully",
            "url": browser_manager.driver.current_url
        }
    except Exception as e:
        logger.error(f"Going forward failed: {e}")
        return {
            "success": False,
            "error": str(e)
        }


@mcp.tool()
def is_element_present(selector: str, by_type: str = "css") -> dict:
    """Check if an element is present on the page.
    
    Args:
        selector: CSS selector or other identifier for the element
        by_type: Type of selector ('css', 'xpath', 'id', 'class', 'tag', 'name')
        
    Returns:
        Dictionary with presence check result
    """
    logger.info(f"Checking if element is present: {selector}")
    try:
        browser_manager.ensure_browser()
        elements = browser_manager.find_elements(selector, by_type)
        is_present = len(elements) > 0
        
        return {
            "success": True,
            "is_present": is_present,
            "count": len(elements)
        }
    except Exception as e:
        logger.error(f"Element presence check failed: {e}")
        return {
            "success": False,
            "error": str(e)
        }


@mcp.tool()
def get_element_attribute(selector: str, attribute: str, by_type: str = "css") -> dict:
    """Get an attribute value from an element.
    
    Args:
        selector: CSS selector or other identifier for the element
        attribute: Name of the attribute to get
        by_type: Type of selector ('css', 'xpath', 'id', 'class', 'tag', 'name')
        
    Returns:
        Dictionary with attribute value
    """
    logger.info(f"Getting attribute '{attribute}' from element: {selector}")
    try:
        element = browser_manager.find_element(selector, by_type)
        value = element.get_attribute(attribute)
        
        return {
            "success": True,
            "attribute": attribute,
            "value": value
        }
    except Exception as e:
        logger.error(f"Getting attribute failed: {e}")
        return {
            "success": False,
            "error": str(e)
        }


@mcp.tool()
def clear_field(selector: str, by_type: str = "css") -> dict:
    """Clear text from an input field.
    
    Args:
        selector: CSS selector or other identifier for the input element
        by_type: Type of selector ('css', 'xpath', 'id', 'class', 'tag', 'name')
        
    Returns:
        Dictionary with clear result
    """
    logger.info(f"Clearing field: {selector}")
    try:
        element = browser_manager.find_element(selector, by_type)
        element.clear()
        
        return {
            "success": True,
            "message": f"Successfully cleared field: {selector}"
        }
    except Exception as e:
        logger.error(f"Clearing field failed: {e}")
        return {
            "success": False,
            "error": str(e)
        }


@mcp.tool() 
def select_dropdown_option(selector: str, option_text: str = None, option_value: str = None, by_type: str = "css") -> dict:
    """Select an option from a dropdown menu.
    
    Args:
        selector: CSS selector for the dropdown/select element
        option_text: Text of the option to select (either this or option_value required)
        option_value: Value of the option to select (either this or option_text required)
        by_type: Type of selector ('css', 'xpath', 'id', 'class', 'tag', 'name')
        
    Returns:
        Dictionary with selection result
    """
    logger.info(f"Selecting dropdown option in: {selector}")
    try:
        from selenium.webdriver.support.ui import Select
        
        element = browser_manager.find_element(selector, by_type)
        select = Select(element)
        
        if option_text:
            select.select_by_visible_text(option_text)
            message = f"Selected option by text: {option_text}"
        elif option_value:
            select.select_by_value(option_value)
            message = f"Selected option by value: {option_value}"
        else:
            return {
                "success": False,
                "error": "Either option_text or option_value must be provided"
            }
        
        return {
            "success": True,
            "message": message
        }
    except Exception as e:
        logger.error(f"Dropdown selection failed: {e}")
        return {
            "success": False,
            "error": str(e)
        }


@mcp.tool()
def hover_element(selector: str, by_type: str = "css") -> dict:
    """Hover mouse over an element.
    
    Args:
        selector: CSS selector or other identifier for the element
        by_type: Type of selector ('css', 'xpath', 'id', 'class', 'tag', 'name')
        
    Returns:
        Dictionary with hover result
    """
    logger.info(f"Hovering over element: {selector}")
    try:
        from selenium.webdriver.common.action_chains import ActionChains
        
        browser_manager.ensure_browser()
        element = browser_manager.find_element(selector, by_type)
        
        actions = ActionChains(browser_manager.driver)
        actions.move_to_element(element).perform()
        
        return {
            "success": True,
            "message": f"Successfully hovered over element: {selector}"
        }
    except Exception as e:
        logger.error(f"Hovering failed: {e}")
        return {
            "success": False,
            "error": str(e)
        }


@mcp.tool()
def extract_table_data(selector: str = "table", by_type: str = "css") -> dict:
    """Extract data from HTML tables.
    
    Args:
        selector: CSS selector for the table element (defaults to "table")
        by_type: Type of selector ('css', 'xpath', 'id', 'class', 'tag', 'name')
        
    Returns:
        Dictionary with table data as arrays
    """
    logger.info(f"Extracting table data from: {selector}")
    try:
        browser_manager.ensure_browser()
        
        # Get table HTML
        table_element = browser_manager.find_element(selector, by_type)
        table_html = table_element.get_attribute('outerHTML')
        
        # Parse with BeautifulSoup
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(table_html, 'html.parser')
        table = soup.find('table')
        
        if not table:
            return {
                "success": False,
                "error": "No table found with the given selector"
            }
        
        # Extract headers
        headers = []
        header_row = table.find('thead')
        if header_row:
            for th in header_row.find_all(['th', 'td']):
                headers.append(th.get_text(strip=True))
        
        # Extract rows
        rows = []
        tbody = table.find('tbody') or table
        for tr in tbody.find_all('tr'):
            row_data = []
            for td in tr.find_all(['td', 'th']):
                row_data.append(td.get_text(strip=True))
            if row_data:  # Skip empty rows
                rows.append(row_data)
        
        return {
            "success": True,
            "headers": headers,
            "rows": rows,
            "row_count": len(rows)
        }
        
    except Exception as e:
        logger.error(f"Table extraction failed: {e}")
        return {
            "success": False,
            "error": str(e)
        }


# Cleanup function to be called on server shutdown
def cleanup_browser():
    """Clean up browser resources."""
    try:
        browser_manager.stop_browser()
        logger.info("Browser cleanup completed")
    except Exception as e:
        logger.error(f"Browser cleanup failed: {e}")


@click.command()
@click.option("--port", default=8000, help="Port to listen on for SSE transport")
@click.option(
    "--transport",
    type=click.Choice(["stdio", "sse", "streamable-http"]),
    default="stdio",
    help="Transport type to use",
)
def main(port: int, transport: str) -> int:
    """Run the Browser Automation MCP Server."""
    
    # Set up logging
    logging.basicConfig(level=logging.INFO)
    logger.info(f"Starting Browser Automation MCP Server with {transport} transport")
    
    try:
        # Register cleanup function
        import atexit
        atexit.register(cleanup_browser)
        
        # Run the server based on transport type
        if transport == "stdio":
            # STDIO transport - most common for MCP
            mcp.run(transport="stdio")
        elif transport == "sse":
            # Server-Sent Events transport
            logger.info(f"Starting SSE server on port {port}")
            mcp.run(transport="sse", port=port)
        elif transport == "streamable-http":
            # Streamable HTTP transport
            logger.info(f"Starting Streamable HTTP server on port {port}")
            mcp.run(transport="streamable-http", port=port)
            
    except KeyboardInterrupt:
        logger.info("Received interrupt signal")
    except Exception as e:
        logger.error(f"Server error: {e}")
        return 1
    finally:
        cleanup_browser()
    
    return 0


if __name__ == "__main__":
    main()