# Browser Automation MCP Server

A powerful Model Context Protocol (MCP) server that provides comprehensive browser automation capabilities through Selenium WebDriver. This server enables AI assistants to interact with web pages, extract data, and perform complex web automation tasks.

## Quick Start

1. **Install the server:**
   ```bash
   cd LAM-mcp
   uv install
   ```

2. **Run the server:**
   ```bash
   # STDIO transport (recommended for most MCP clients)
   uv run python -m browser_mcp_server.server
   
   # Or with SSE transport
   uv run python -m browser_mcp_server.server --transport sse --port 8000
   ```

3. **Configure with Claude Desktop:**
   Add to your `claude_desktop_config.json`:
   ```json
   {
     "mcpServers": {
       "browser-automation": {
         "command": "uv",
         "args": ["run", "python", "-m", "browser_mcp_server.server"],
         "env": {
           "BROWSER_HEADLESS": "true"
         }
       }
     }
   }
   ```

## Available Tools

### Core Navigation
- `navigate_to_url(url)` - Navigate to any website
- `get_current_url()` - Get current page URL and title
- `refresh_page()` - Refresh the current page
- `go_back()` - Navigate back in history
- `go_forward()` - Navigate forward in history

### Element Interaction  
- `click_element(selector, by_type="css")` - Click buttons, links, etc.
- `type_text(selector, text, by_type="css")` - Type into input fields
- `clear_field(selector, by_type="css")` - Clear input fields
- `hover_element(selector, by_type="css")` - Hover over elements

### Content Extraction
- `get_element_text(selector, by_type="css")` - Extract text from elements
- `get_page_source()` - Get full HTML source
- `extract_links()` - Get all links on the page
- `extract_table_data(selector="table")` - Extract structured table data

### Form Automation
- `fill_form(form_data)` - Fill entire forms with data dictionary
- `select_dropdown_option(selector, option_text=None, option_value=None)` - Select dropdown options

### Advanced Features
- `take_screenshot(element_selector=None)` - Capture page or element screenshots
- `execute_javascript(script)` - Run custom JavaScript
- `wait_for_element(selector, timeout=30)` - Wait for dynamic content
- `scroll_page(direction="down", pixels=None)` - Scroll in any direction

### Utility Functions
- `is_element_present(selector, by_type="css")` - Check element existence
- `get_element_attribute(selector, attribute, by_type="css")` - Get element attributes
- `get_cookies()` - Retrieve browser cookies
- `set_cookie(name, value, domain=None, path="/")` - Set cookies

## Environment Variables

Configure the server behavior with these environment variables:

```bash
# Browser type (chrome, firefox, edge)
BROWSER_TYPE=chrome

# Run in headless mode
BROWSER_HEADLESS=true

# Default timeout in seconds
BROWSER_TIMEOUT=30

# Browser window size
BROWSER_WINDOW_SIZE=1920x1080

# Custom user agent
BROWSER_USER_AGENT="Custom Agent String"

# Download directory
BROWSER_DOWNLOAD_DIR=/path/to/downloads
```

## Example Usage Scenarios

### Web Scraping
```python
# Navigate and extract data
await navigate_to_url("https://news.ycombinator.com")
await wait_for_element(".storylink")
links = await extract_links()
headlines = await get_element_text(".storylink")
```

### E-commerce Automation
```python
# Search for products
await navigate_to_url("https://amazon.com")
await type_text("#twotabsearchtextbox", "laptop")
await click_element("#nav-search-submit-button")
await wait_for_element("[data-component-type='s-search-result']")
results = await extract_text("[data-component-type='s-search-result'] h2")
```

### Form Filling
```python
# Contact form automation
await navigate_to_url("https://example.com/contact")
await fill_form({
    "#name": "John Doe",
    "#email": "john@example.com", 
    "#message": "Hello from automation!"
})
await click_element("#submit")
```

### Social Media Automation
```python
# Login and post (be mindful of terms of service)
await navigate_to_url("https://twitter.com/login")
await type_text("[name='text']", "username")
await click_element("[role='button']:has-text('Next')")
await wait_for_element("[name='password']")
await type_text("[name='password']", "password")
await click_element("[data-testid='LoginForm_Login_Button']")
```

## Security Best Practices

⚠️ **Important Security Considerations:**

1. **Controlled Environment**: Use in secure, isolated environments
2. **Authentication**: Implement proper authentication for production use
3. **Input Validation**: Always validate URLs and selectors
4. **Rate Limiting**: Implement delays between requests
5. **Monitoring**: Log all automation activities
6. **Compliance**: Respect robots.txt and website terms of service

## Browser Support

- **Chrome/Chromium**: Full support with automatic driver management
- **Firefox**: Full support with GeckoDriver auto-installation  
- **Microsoft Edge**: Full support with Edge WebDriver
- **Headless Mode**: All browsers support headless operation

## Error Handling

The server provides comprehensive error handling:

```json
{
  "success": false,
  "error": "Element not found: #invalid-selector",
  "details": "NoSuchElementException details..."
}
```

Common error types:
- `TimeoutException`: Element not found within timeout
- `NoSuchElementException`: Invalid selector or missing element
- `ElementNotInteractableException`: Element not clickable/visible
- `WebDriverException`: Browser communication issues

## Development

### Running Tests
```bash
uv run pytest tests/
```

### Code Quality
```bash
# Format code
uv run black browser_mcp_server/

# Sort imports  
uv run isort browser_mcp_server/

# Type checking
uv run mypy browser_mcp_server/
```

### Adding New Tools

To add new browser automation tools:

1. Add the function to `browser_utils.py`
2. Create an MCP tool wrapper in `server.py` using `@mcp.tool()`
3. Add comprehensive docstrings and type hints
4. Include error handling and logging
5. Add tests in `tests/`

## Troubleshooting

### Common Issues

**Browser won't start:**
- Check if Chrome/Firefox is installed
- Verify driver permissions
- Try different browser type: `BROWSER_TYPE=firefox`

**Elements not found:**
- Use `wait_for_element()` for dynamic content
- Check selector syntax (CSS vs XPath)
- Verify element is visible and interactable

**Timeout errors:**
- Increase timeout: `BROWSER_TIMEOUT=60`
- Check network connectivity
- Ensure page is fully loaded

**Permission issues:**
- Run with appropriate user permissions
- Check download directory write access
- Verify browser installation location

### Debug Mode

Enable debug logging:
```bash
export PYTHONPATH=$PYTHONPATH:$(pwd)
python -m browser_mcp_server.server --transport stdio
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## License

MIT License - see LICENSE file for details.

## Disclaimer

This tool provides powerful browser automation capabilities. Users are responsible for:
- Complying with website terms of service
- Respecting rate limits and robots.txt
- Ensuring ethical use of automation
- Protecting user privacy and data security

Use responsibly and in accordance with applicable laws and regulations.