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
from .rag_engine import RAGEngine

# Initialize RAG engine with session-based storage
rag_engine = RAGEngine()

# Configure logging to stderr to avoid interfering with MCP JSON-RPC communication
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# Create FastMCP server
mcp = FastMCP("Browser Automation Server")

# Define automation best practices as a prompt
AUTOMATION_INSTRUCTIONS = """
# Browser Automation Best Practices

When using this browser automation MCP server, follow these guidelines for reliable automation across ANY website:

## Core Automation Workflow

**Standard Flow**: Navigate → Analyze Page ONCE → Use RAG Tools → Close Popups → Find Elements → Take Action → Verify Result

**CRITICAL - Token Optimization**:
- **Analyze page ONCE** with `analyze_current_page` immediately after navigation
- **Use RAG tools** (`get_detected_popups`, `find_page_context`, `get_smart_element_selector`) to get information from the stored analysis
- **DO NOT** call `get_page_source` or re-analyze unless absolutely necessary
- **Only re-analyze** when page DOM changes significantly (after major actions like page transitions, AJAX loads, tab switches)
- RAG tools retrieve from stored analysis = faster & fewer tokens

## 1. Analyze Once, Query Multiple Times
- Use `analyze_current_page` immediately after navigating to any new page (ONLY ONCE per page)
- **After analysis, use `get_detected_popups`** to see what popups were found automatically
- Use `find_page_context` and `get_smart_element_selector` to find elements from stored analysis
- These RAG queries are lightweight - use them freely instead of re-reading page source
- Check current state using JavaScript for dynamic verification (playback state, form values, etc.)
- **Re-analyze only when**:
  - Page navigates to new URL
  - Major DOM changes (modal opens/closes, new content loads via AJAX)
  - Previous action significantly altered page structure
  - You need fresh data after multiple failed attempts

## 2. Handle Popups & Overlays Proactively
- **ALWAYS** check for and close popups/banners/cookie consents BEFORE interacting with page elements
- **CRITICAL**: Run popup cleanup AFTER every navigation and BEFORE every interaction
- **Use RAG to detect popups**: After `analyze_current_page`, call `get_detected_popups()` to get automatically detected popups with their close buttons
- Common popup types and patterns to close:
  - **Cookie banners**: `button:contains("Reject")`, `button:contains("Accept")`, `[aria-label="Close"]`, `.cookie-banner button`
  - **Login/Signup modals**: `button[aria-label="Close"]`, `button[title="Close"]`, `.modal-close`, `.auth-modal button:first-child`
  - **Announcements**: `.banner__close`, `.announcement-close`, `[class*="banner"] button[class*="close"]`
  - **Newsletter popups**: `.newsletter-close`, `[class*="modal"] [class*="close"]`
  - **Age verification**: Look for "Yes", "I'm 18+", "Enter", "Continue" buttons
  - **Location prompts**: "Not now", "Skip", "Close" buttons
  - **App install prompts**: "No thanks", "Continue in browser", "Close"
- **Multi-step approach**:
  1. First, close ALL visible modals/popups using multiple selectors
  2. Then try ESC key: `document.dispatchEvent(new KeyboardEvent('keydown', {key: 'Escape'}))`
  3. Check for overlay elements blocking interaction: `[class*="overlay"]`, `[class*="backdrop"]`
  4. If popup reappears after action, close it again
- Use JavaScript to close multiple popups at once:
  ```javascript
  // Close all common popup types
  const closeSelectors = [
    'button[aria-label="Close"]',
    'button[title="Close"]', 
    '.modal-close',
    '.banner__close',
    '[class*="modal"] [class*="close"]',
    '[class*="Modal"] button:first-child'
  ];
  
  closeSelectors.forEach(sel => {
    document.querySelectorAll(sel).forEach(el => {
      if (el.offsetParent !== null) el.click();
    });
  });
  
  // Also check for text-based close buttons
  const allButtons = document.querySelectorAll('button');
  allButtons.forEach(btn => {
    const text = btn.textContent.toLowerCase().trim();
    if (btn.offsetParent !== null && (
      text === 'reject all' || text === 'reject' || 
      text === 'close' || text === 'no thanks' ||
      text === 'skip' || text === 'not now'
    )) {
      btn.click();
    }
  });
  ```

## 3. Smart Element Selection & Interaction
- Use `get_smart_element_selector` to find elements with context (labels, nearby text)
- **Important**: Buttons can be disguised as other elements:
  - `<a>` (anchor tags) styled as buttons with `role="button"`
  - `<div>` or `<span>` with click handlers
  - Elements with button-like classes (e.g., `.btn`, `.button`, `[class*="button"]`)
  - When searching for buttons, also check: `a[role="button"]`, `div[role="button"]`, `[class*="button"]`, `[onclick]`
- **CRITICAL - Text-Based Element Search**:
  - **Don't limit search to `<button>` tags only** - search across ALL element types
  - Perform **text content search** across `button`, `a`, `div`, `span`, `li`, and other interactive elements
  - **Prioritize by DOM position**: Top elements in the page hierarchy come first
  - Use this pattern for finding buttons by text:
    ```javascript
    // Search ALL elements, not just buttons
    const allElements = document.querySelectorAll('button, a, div, span, li, [role="button"]');
    const matches = [];
    
    allElements.forEach(el => {
      const text = el.textContent.toLowerCase().trim();
      const ariaLabel = (el.getAttribute('aria-label') || '').toLowerCase();
      
      // Match by text content or aria-label
      if (text.includes('play') || ariaLabel.includes('play')) {
        // Only visible elements
        if (el.offsetParent !== null) {
          matches.push({
            element: el,
            text: text,
            ariaLabel: ariaLabel,
            tag: el.tagName,
            // Calculate DOM depth (lower = higher in hierarchy)
            depth: el.parentElement ? [...document.querySelectorAll('*')].indexOf(el) : 0
          });
        }
      }
    });
    
    // Sort by DOM position (top elements first)
    matches.sort((a, b) => a.depth - b.depth);
    
    // Click the first (topmost) match
    if (matches.length > 0) {
      matches[0].element.click();
    }
    ```
- Understand element hierarchies:
  - Parent containers vs. actual interactive elements
  - List items vs. action buttons within them
  - Nested buttons (e.g., playlist play vs. track play)
  - Anchor tags that act as buttons
  - **Top-level elements should be prioritized** over deeply nested ones
- Before clicking, verify:
  - Element is visible (`offsetParent !== null`)
  - Element is not disabled or has `aria-disabled="true"`
  - No overlay blocking it
  - Check both `<button>` elements AND anchor/div elements with button roles
  - **Search by text content, not just selectors**
- If element not interactable:
  - Scroll into view first
  - Wait for animations to complete
  - Remove blocking overlays
  - Use JavaScript click as fallback

## 4. Context-Aware Actions
- **Forms**: Use `fill_form` for multi-field forms, verify each field filled correctly
- **Searches**: Enter text, wait for suggestions, select correct result
- **Media Players**: Distinguish between playlist/album actions vs. individual item actions
- **Shopping**: Add to cart → verify cart updated → proceed to checkout
- **Authentication**: Fill login → submit → wait for redirect → verify logged in
- **Navigation**: Click links → wait for page load → verify URL changed

## 5. Verification & State Validation
- After every action, verify it worked:
  - Form submitted? Check for success message or redirect
  - Button clicked? Check if modal opened or content changed
  - Media playing? Check playback controls state
  - Item added? Check cart count or confirmation
- Use JavaScript to check dynamic state:
  ```javascript
  // Check if video playing
  !document.querySelector('video').paused
  
  // Check if form submitted
  document.querySelector('.success-message') !== null
  
  // Check element state
  element.classList.contains('active')
  ```

## 6. Progress Tracking & Learning
- Use `track_action_result` after important actions to build session history
- Use `get_session_progress` to review what worked/failed
- **Prefer RAG queries over re-reading page**: Use stored analysis data via RAG tools
- Learn from failures:
  - If selector failed, try alternative approaches
  - If action didn't work, check for blocking elements
  - If verification failed, wait longer or check different state indicators
- Clear session context when starting completely new workflows

## 7. Token Optimization Best Practices
- **One analysis per page**: Call `analyze_current_page` once after navigation
- **Query RAG, don't re-read**: Use `find_page_context`, `get_smart_element_selector`, `get_detected_popups` instead of `get_page_source`
- **Use JavaScript for dynamic checks**: Check playback state, form values, visibility without re-analyzing
- **Batch JavaScript operations**: Combine multiple checks in one `execute_javascript` call
- **Only re-analyze when necessary**: Page navigation, major DOM changes, or repeated failures
- **Example - Good workflow**:
  ```
  1. navigate_to_url("...")
  2. analyze_current_page(...)  // ONCE
  3. popups = get_detected_popups()  // From RAG
  4. close popups via execute_javascript
  5. elements = get_smart_element_selector(...)  // From RAG
  6. click_element(best_element)
  7. verify via execute_javascript (check state)
  // NO re-analysis unless page changed
  ```
- **Example - Avoid**:
  ```
  ❌ analyze_current_page()
  ❌ get_page_source()  // Redundant, already analyzed
  ❌ analyze_current_page() again  // Unless page changed
  ```

## 7. Error Recovery Strategies
- **Element not found**: 
  - Wait longer with `wait_for_element`
  - Try alternative selectors (ID, class, XPath, aria-label)
  - Use `find_page_context` to locate it semantically
- **Element not interactable**:
  - Scroll element into view
  - Close overlays/modals blocking it
  - Wait for animations to complete
  - Use JavaScript click: `element.click()`
- **Action didn't work**:
  - Verify no error messages appeared
  - Check if page state changed
  - Try alternative approach (different button, different flow)
- **Page not loading**:
  - Wait for specific elements with `wait_for_element`
  - Check network state with JavaScript
  - Refresh if necessary

## 8. Common Website Patterns

### E-commerce Sites
1. Navigate → Close cookie banner → Search product → Analyze results
2. Click product (not image) → Verify product page loaded
3. Select options → Add to cart → Verify cart updated
4. Checkout → Fill form → Submit → Verify order placed

### Media/Streaming Sites
1. Navigate → Close popups → Search content → Analyze results
2. Find specific item (not playlist) → Click play button on item
   - **CRITICAL**: Play buttons in search results are often inside list items/containers
   - Find the first result container first, THEN find the play button inside it
   - Example pattern for SoundCloud search results:
     ```javascript
     // Find first search result container with a play button
     const searchResults = [...document.querySelectorAll('li, [class*="searchList"], [class*="trackList"], [class*="result"]')];
     const firstResult = searchResults.find(el => {
       const hasPlayButton = el.querySelector('a[role="button"]');
       return hasPlayButton && el.offsetParent !== null;
     });
     if (firstResult) {
       const playButton = firstResult.querySelector('a[role="button"]');
       if (playButton) playButton.click();
     }
     ```
3. Verify playback started (check player state)
4. Track action for session history

### Social Media Sites
1. Navigate → Handle login prompts → Close notifications
2. Find content → Analyze feed structure → Interact with specific posts
3. Verify interactions (likes, comments, shares) reflected in UI

### Productivity/SaaS Apps
1. Navigate → Login if needed → Close onboarding modals
2. Find tools/features → Analyze interface → Execute tasks
3. Save/submit → Verify changes persisted

## 9. Performance Tips
- **Analyze once per page** - Use RAG queries after initial analysis
- Use direct URLs when possible (e.g., search URLs with query parameters)
- Batch JavaScript operations instead of multiple round trips
- Use `execute_javascript` for complex state checks in one call
- **Prefer RAG tools over page re-reads**: `get_smart_element_selector`, `find_page_context`, `get_detected_popups`
- Clear session context between completely different workflows
- Use `wait_for_element` instead of polling with JavaScript
- Combine multiple element checks in single JavaScript execution

## 10. Security & Privacy
- Never store or log sensitive data (passwords, tokens, personal info)
- Clear cookies/session when done with sensitive sites
- Use headless mode for background automation
- Respect robots.txt and rate limiting

These practices ensure reliable, autonomous automation across all websites and use cases.
"""


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


# ============================================
# RAG Tools - Session Context Analysis
# ============================================

@mcp.tool()
def analyze_current_page(task_context: str, action_history: list = None) -> dict:
    """Analyze current page and store in session context for intelligent element identification.
    
    This enables context-aware element selection by analyzing page structure and
    identifying relevant sections based on your task.
    
    Args:
        task_context: What you're trying to accomplish (e.g., "fill login form")
        action_history: Optional list of actions taken on this page
        
    Returns:
        Dictionary with analysis status, interactive elements found, and forms detected
        
    Example:
        analyze_current_page(
            task_context="User wants to search for products",
            action_history=[{"action": "navigate", "url": "https://example.com"}]
        )
    """
    try:
        # Get current page HTML
        page_result = browser_manager.get_rendered_html(include_head=False, include_scripts=False)
        if not page_result.get('success'):
            return {
                "status": "error",
                "message": "Failed to get page content"
            }
        
        # Get current URL
        current_url = browser_manager.driver.current_url if browser_manager.driver else "unknown"
        
        # Analyze and store in RAG engine
        result = rag_engine.analyze_and_store_page(
            dom_content=page_result['source'],
            current_url=current_url,
            task_context=task_context,
            action_history=action_history or []
        )
        
        logger.info(f"Analyzed page: {result}")
        return result
        
    except Exception as e:
        logger.error(f"Failed to analyze page: {e}")
        return {
            "status": "error",
            "message": str(e)
        }


@mcp.tool()
def find_page_context(task_description: str, element_type: str = None, top_k: int = 5) -> dict:
    """Find relevant sections of current page for the task.
    
    Uses semantic search to identify the most relevant parts of the page
    based on what you're trying to accomplish.
    
    Args:
        task_description: What you're trying to do (e.g., "submit search query")
        element_type: Optional filter for element type (button, input, link, etc.)
        top_k: Number of relevant sections to return (default: 5)
        
    Returns:
        Dictionary with relevant page sections, elements, and relevance scores
        
    Example:
        find_page_context(
            task_description="find and click the search button",
            element_type="button",
            top_k=3
        )
    """
    try:
        result = rag_engine.find_relevant_context(
            task_description=task_description,
            element_type=element_type,
            top_k=top_k
        )
        
        logger.info(f"Found {result.get('section_count', 0)} relevant sections")
        return result
        
    except Exception as e:
        logger.error(f"Failed to find page context: {e}")
        return {
            "status": "error",
            "message": str(e),
            "relevant_sections": []
        }


@mcp.tool()
def get_smart_element_selector(element_type: str, task_context: str, top_k: int = 5) -> dict:
    """Get element selectors with surrounding context for better identification.
    
    Returns elements that match your criteria along with their surrounding context,
    helping you choose the right element based on labels, nearby text, etc.
    
    Args:
        element_type: Type of element (button, input, link, select, etc.)
        task_context: What you're trying to accomplish
        top_k: Number of element suggestions to return (default: 5)
        
    Returns:
        Dictionary with elements, their selectors, labels, and surrounding context
        
    Example:
        get_smart_element_selector(
            element_type="input",
            task_context="enter search query",
            top_k=3
        )
    """
    try:
        result = rag_engine.get_element_with_context(
            element_type=element_type,
            task_context=task_context,
            top_k=top_k
        )
        
        logger.info(f"Found {result.get('total_found', 0)} elements with context for {element_type}")
        return result
        
    except Exception as e:
        logger.error(f"Failed to get smart element selector: {e}")
        return {
            "status": "error",
            "message": str(e)
        }


@mcp.tool()
def track_action_result(selector: str, action: str, success: bool, element_type: str = None, context: str = None) -> dict:
    """Track action result in current session for progress monitoring.
    
    Records what actions were taken and whether they succeeded, helping to
    maintain a history of the current automation session.
    
    Args:
        selector: CSS selector that was used
        action: Action that was performed (e.g., "click", "fill", "scroll")
        success: Whether the action succeeded
        element_type: Optional type of element (e.g., "button", "input")
        context: Optional additional context about the action
        
    Returns:
        Dictionary with tracking status
        
    Example:
        track_action_result(
            selector="#search-input",
            action="type",
            success=True,
            element_type="input",
            context="entered search query"
        )
    """
    try:
        # Get current URL
        current_url = browser_manager.driver.current_url if browser_manager.driver else "unknown"
        
        result = rag_engine.track_action(
            page_url=current_url,
            selector=selector,
            action=action,
            success=success,
            element_type=element_type,
            context=context
        )
        
        logger.info(f"Tracked action: {action} on {selector} - {'success' if success else 'failed'}")
        return result
        
    except Exception as e:
        logger.error(f"Failed to track action result: {e}")
        return {
            "status": "error",
            "message": str(e)
        }


@mcp.tool()
def get_session_progress() -> dict:
    """Get current session progress, action history, and statistics.
    
    Returns a summary of the current automation session including pages visited,
    actions taken, success rate, and navigation history.
    
    Returns:
        Dictionary with session statistics and recent navigation history
    """
    try:
        stats = rag_engine.get_session_progress()
        logger.info(f"Session progress: {stats.get('actions_taken', 0)} actions taken")
        return stats
        
    except Exception as e:
        logger.error(f"Failed to get session progress: {e}")
        return {
            "status": "error",
            "message": str(e)
        }


@mcp.tool()
def get_detected_popups() -> dict:
    """Get popups and modals detected during page analysis.
    
    Returns information about all popups/modals detected when the page was analyzed,
    including their types (cookie_consent, auth_modal, newsletter, etc.), close buttons,
    and recommended selectors for closing them.
    
    This is useful for automatically handling popups before interacting with page elements.
    
    Returns:
        Dictionary with detected popups, close buttons, and popup action buttons
        
    Example:
        result = get_detected_popups()
        for popup in result['popups']:
            if popup['close_button']:
                # Close the popup using the detected selector
                click_element(popup['close_button']['selector'])
    """
    try:
        popups = rag_engine.get_detected_popups()
        logger.info(f"Retrieved {popups.get('total_popups', 0)} detected popups")
        return popups
        
    except Exception as e:
        logger.error(f"Failed to get detected popups: {e}")
        return {
            "status": "error",
            "message": str(e),
            "popups": []
        }


@mcp.tool()
def clear_session_context() -> dict:
    """Clear current session context and start fresh.
    
    Removes all stored page analysis and action history from the current session,
    effectively resetting the context memory.
    
    Returns:
        Dictionary with clear status
    """
    try:
        result = rag_engine.clear_session()
        logger.info(f"Cleared session: {result.get('session_id')}")
        return result
        
    except Exception as e:
        logger.error(f"Failed to clear session: {e}")
        return {
            "status": "error",
            "message": str(e)
        }


@mcp.prompt()
def automation_best_practices() -> str:
    """Browser automation best practices and guidelines.
    
    This prompt provides essential instructions for reliable browser automation
    that should be followed across all automation tasks.
    """
    return AUTOMATION_INSTRUCTIONS


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