# Browser Automation MCP Server

This project provides a Model Context Protocol (MCP) server for browser automation using Python and Selenium WebDriver, enabling intelligent web interactions with session-based context analysis.

## Features

- Web navigation and page interactions
- Element clicking, typing, and form handling  
- Page content extraction and scraping
- Screenshot capture
- JavaScript execution
- Cookie and session management
- Multi-browser support (Chrome, Firefox, Edge)
- Headless and headed browser modes
- **Session-based context analysis** for smart element identification
- **Semantic search** to find relevant page sections
- **Context-aware element suggestions** with confidence scores
- **Progress tracking** for automation sessions

## Setup

1. Install Python dependencies: `uv add mcp selenium webdriver-manager chromadb sentence-transformers`
2. Install browser drivers automatically via webdriver-manager
3. Configure the server in your MCP client (Claude Desktop, VS Code, etc.)

## Tools Available

### Session Context Intelligence
- `analyze_current_page`: Analyze page structure and store in session context
- `find_page_context`: Find relevant page sections for your task using semantic search
- `get_smart_element_selector`: Get elements with surrounding context for better identification
- `track_action_result`: Track actions and success/failure in current session
- `get_session_progress`: View session statistics, actions taken, and success rate
- `clear_session_context`: Clear session memory and start fresh

### Core Automation
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

## How Session Context Works

### 1. Analyze Pages
After navigating to a page, analyze it to understand its structure:
```python
navigate_to_url("https://example.com/login")
analyze_current_page(task_context="User wants to log in")
```

### 2. Find Elements Intelligently
Get element suggestions based on your task:
```python
get_smart_element_selector(
    element_type="input",
    task_context="enter username",
    top_k=3
)
# Returns elements ranked by confidence with surrounding context
```

### 3. Track Progress
Monitor your automation session:
```python
track_action_result(selector="#username", action="type", success=True)
get_session_progress()  # See actions taken, success rate
```

### Key Benefits
- **No hardcoded selectors**: Find elements by describing what you want
- **Context-aware**: Elements come with labels and surrounding text
- **Confidence scoring**: Know which element is most likely correct
- **Session-only**: Memory clears automatically (no persistent storage)
- **Progress monitoring**: Track what's working and what's not

## Session Lifecycle

- **Start**: Session ID created automatically, in-memory storage initialized
- **During**: Pages analyzed, actions tracked, context builds up
- **End**: Memory cleared when process stops or manually with `clear_session_context()`

## Use Cases

1. **Dynamic pages**: When element IDs/classes change
2. **Complex forms**: Find fields by description ("email for login")
3. **Ambiguous pages**: Multiple similar elements, need context to distinguish
4. **Progress tracking**: Monitor automation workflow success rates

## Security Note

This server provides powerful browser automation capabilities. Ensure proper authentication and authorization when deploying in production environments.