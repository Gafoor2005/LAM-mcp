# Browser Automation MCP Server

A Model Context Protocol (MCP) server that provides browser automation capabilities using Selenium WebDriver. This server enables AI assistants to interact with web pages through a standardized interface.

## Features

### Core Browser Automation
- **Web Navigation**: Navigate to URLs, handle redirects, and manage browser history
- **Element Interaction**: Click buttons, links, and other interactive elements
- **Text Input**: Type into form fields, search boxes, and text areas
- **Content Extraction**: Extract text, HTML, and structured data from web pages
- **Screenshot Capture**: Take full-page or element-specific screenshots
- **JavaScript Execution**: Run custom JavaScript code in the browser context

### Advanced Capabilities
- **Form Handling**: Automatically fill out complex web forms
- **Cookie Management**: Get, set, and manage browser cookies
- **Session Persistence**: Maintain browser sessions across operations
- **Multi-Browser Support**: Chrome, Firefox, Edge with automatic driver management
- **Headless/Headed Modes**: Run browsers with or without GUI
- **Element Waiting**: Smart waiting for dynamic content and AJAX loads

## Installation

1. **Install Dependencies**:
   ```bash
   uv add mcp selenium webdriver-manager pillow beautifulsoup4
   ```

2. **Install Browser Drivers** (handled automatically by webdriver-manager):
   - Chrome/Chromium driver
   - Firefox GeckoDriver  
   - Edge WebDriver

## Usage

### Running the Server

```bash
# STDIO transport (for local development)
python -m browser_mcp_server.server

# SSE transport (for web-based clients)
python -m browser_mcp_server.server --transport sse --port 8000
```

### Configuration with Claude Desktop

Add to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "browser-automation": {
      "command": "uv",
      "args": ["run", "python", "-m", "browser_mcp_server.server"],
      "env": {
        "BROWSER_HEADLESS": "true",
        "BROWSER_TYPE": "chrome"
      }
    }
  }
}
```

## Available Tools

### Navigation & Page Control
- **`navigate_to_url`**: Navigate to a specific URL
- **`get_page_source`**: Get the full HTML source of the current page
- **`get_current_url`**: Get the current page URL
- **`refresh_page`**: Refresh the current page
- **`go_back`**: Navigate back in browser history
- **`go_forward`**: Navigate forward in browser history

### Element Interaction
- **`click_element`**: Click on elements by CSS selector or XPath
- **`type_text`**: Type text into input fields
- **`clear_field`**: Clear text from input fields
- **`get_element_text`**: Extract text content from elements
- **`get_element_attribute`**: Get attribute values from elements
- **`is_element_present`**: Check if an element exists on the page

### Content Extraction
- **`extract_links`**: Extract all links from the current page
- **`extract_images`**: Extract all images and their attributes
- **`extract_tables`**: Extract table data as structured JSON
- **`extract_forms`**: Extract form fields and their properties
- **`search_text`**: Search for text patterns on the page

### Form Automation
- **`fill_form`**: Fill out entire forms with structured data
- **`select_dropdown_option`**: Select options from dropdown menus
- **`check_checkbox`**: Check or uncheck checkbox elements
- **`select_radio_button`**: Select radio button options

### Visual & Media
- **`take_screenshot`**: Capture full-page or element screenshots
- **`scroll_page`**: Scroll the page in various directions
- **`hover_element`**: Hover mouse over elements
- **`drag_and_drop`**: Drag and drop elements

### JavaScript & Advanced
- **`execute_javascript`**: Execute custom JavaScript code
- **`wait_for_element`**: Wait for elements to appear or disappear
- **`wait_for_page_load`**: Wait for page load completion
- **`switch_to_frame`**: Switch context to iframes
- **`handle_alert`**: Handle JavaScript alerts and confirmations

### Session & Cookies
- **`get_cookies`**: Retrieve browser cookies
- **`set_cookies`**: Set browser cookies
- **`delete_cookies`**: Delete specific or all cookies
- **`get_local_storage`**: Access browser local storage
- **`set_local_storage`**: Set local storage values

## Environment Variables

- **`BROWSER_TYPE`**: Browser to use (`chrome`, `firefox`, `edge`) - default: `chrome`
- **`BROWSER_HEADLESS`**: Run in headless mode (`true`/`false`) - default: `true`
- **`BROWSER_TIMEOUT`**: Default timeout for operations in seconds - default: `30`
- **`BROWSER_WINDOW_SIZE`**: Browser window size (`1920x1080`) - default: `1920x1080`
- **`BROWSER_USER_AGENT`**: Custom user agent string
- **`BROWSER_DOWNLOAD_DIR`**: Directory for file downloads

## Example Usage Patterns

### Web Scraping
```python
# Navigate to a website and extract data
await navigate_to_url("https://example.com")
await wait_for_element("css:.content")
content = await extract_text("css:.main-content")
links = await extract_links()
```

### Form Automation
```python
# Fill out and submit a contact form
await navigate_to_url("https://example.com/contact")
await fill_form({
    "name": "John Doe",
    "email": "john@example.com",
    "message": "Hello from MCP!"
})
await click_element("css:button[type='submit']")
```

### E-commerce Automation
```python
# Search and interact with e-commerce sites
await navigate_to_url("https://shop.example.com")
await type_text("css:#search-input", "laptop")
await click_element("css:.search-button")
await wait_for_element("css:.product-list")
products = await extract_text("css:.product-item")
```

## Security Considerations

This server provides powerful browser automation capabilities that can:
- Navigate to any website
- Execute arbitrary JavaScript
- Access and modify cookies and local storage
- Take screenshots of web content
- Fill out and submit forms

**Recommendations:**
- Use in controlled environments
- Implement proper authentication for production
- Review and approve automation scripts
- Monitor for suspicious activities
- Use headless mode in production
- Implement rate limiting and timeouts

## Development

### Running Tests
```bash
uv run pytest tests/
```

### Code Formatting
```bash
uv run black browser_mcp_server/
uv run isort browser_mcp_server/
```

### Type Checking
```bash
uv run mypy browser_mcp_server/
```

## License

MIT License - see LICENSE file for details.