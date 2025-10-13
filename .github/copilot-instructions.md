# Browser Automation MCP Server

This project provides a Model Context Protocol (MCP) server for browser automation using Python and Selenium WebDriver, enabling Large Action Model capabilities for web interactions.

## Features

- Web navigation and page interactions
- Element clicking, typing, and form handling  
- Page content extraction and scraping
- Screenshot capture
- JavaScript execution
- Cookie and session management
- Multi-browser support (Chrome, Firefox, Edge)
- Headless and headed browser modes

## Setup

1. Install Python dependencies: `uv add mcp selenium webdriver-manager`
2. Install browser drivers automatically via webdriver-manager
3. Configure the server in your MCP client (Claude Desktop, etc.)

## Tools Available

- `navigate_to_url`: Navigate to a specific URL
- `click_element`: Click on page elements by selector
- `type_text`: Type text into input fields
- `extract_text`: Extract text content from elements
- `take_screenshot`: Capture page screenshots
- `execute_javascript`: Run JavaScript code
- `get_page_source`: Get full HTML source
- `fill_form`: Fill out web forms
- `scroll_page`: Scroll the page
- `wait_for_element`: Wait for elements to appear
- `get_cookies`: Retrieve page cookies
- `set_cookies`: Set browser cookies

## Security Note

This server provides powerful browser automation capabilities. Ensure proper authentication and authorization when deploying in production environments.