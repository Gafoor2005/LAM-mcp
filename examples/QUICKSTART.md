# Quick Start Guide

This guide will help you get your browser MCP server up and running quickly.

## Prerequisites

- Python 3.8+
- uv package manager (recommended) or pip
- A supported browser (Chrome, Firefox, or Edge)

## Installation

### 1. Clone or Download

```bash
git clone <repository-url>
cd LAM-mcp
```

### 2. Install Dependencies

Using uv (recommended):
```bash
uv sync
```

Using pip:
```bash
pip install -e .
```

### 3. Test Installation

```bash
uv run python examples/test_setup.py
```

## Configuration

### For Claude Desktop

1. Copy the configuration:
   ```bash
   cp examples/claude_desktop_config.json ~/Library/Application\ Support/Claude/claude_desktop_config.json
   ```
   
   On Windows:
   ```powershell
   Copy-Item examples\claude_desktop_config.json $env:APPDATA\Claude\claude_desktop_config.json
   ```

2. Update the configuration file with the correct path to your project.

3. Restart Claude Desktop.

### For Other MCP Clients

See `examples/README.md` for detailed configuration instructions.

## First Test

### 1. Manual Test

Start the server manually:
```bash
uv run python -m browser_mcp_server.server
```

You should see initialization messages.

### 2. With MCP Inspector (Optional)

```bash
npm install -g @modelcontextprotocol/inspector
npx @modelcontextprotocol/inspector uv run python -m browser_mcp_server.server
```

This opens a web interface to test your MCP server.

### 3. In Claude Desktop

Ask Claude to:
- "Navigate to example.com"
- "Take a screenshot"  
- "Extract all links from the page"

## Available Tools

Your MCP server provides these tools:

| Tool | Purpose |
|------|---------|
| `navigate_to_url` | Go to a specific URL |
| `click_element` | Click on page elements |
| `type_text` | Type into input fields |
| `take_screenshot` | Capture page screenshots |
| `extract_text` | Get text from elements |
| `extract_links` | Get all links from page |
| `fill_form` | Fill out web forms |
| `execute_javascript` | Run custom JavaScript |
| `scroll_page` | Scroll the page |
| `wait_for_element` | Wait for elements to appear |
| `get_cookies` | Retrieve cookies |
| `set_cookies` | Set browser cookies |
| `get_page_source` | Get full HTML |

## Example Usage

### Simple Navigation
```
User: "Go to google.com and search for 'python selenium'"
```

The MCP server will:
1. Navigate to google.com
2. Find the search box
3. Type "python selenium"
4. Click search or press enter
5. Return results

### Web Scraping
```
User: "Go to news.ycombinator.com and get the titles of the top 10 stories"
```

The server will:
1. Navigate to Hacker News
2. Extract story titles
3. Return the list of titles

### Form Automation
```
User: "Fill out the contact form on example.com/contact with name 'John' and email 'john@test.com'"
```

The server will:
1. Navigate to the contact page
2. Find form fields
3. Fill in the information
4. Optionally submit the form

## Troubleshooting

### Common Issues

1. **Browser won't start**
   - Try headless mode: Set `BROWSER_HEADLESS=true`
   - Check browser installation
   - Try different browser: `BROWSER_TYPE=firefox`

2. **Import errors**
   - Run `uv sync` to install dependencies
   - Check Python version (3.8+ required)

3. **Permission errors**
   - Check file permissions
   - Run with appropriate user privileges

4. **Claude Desktop not connecting**
   - Verify config file location
   - Check JSON syntax
   - Restart Claude Desktop
   - Check logs in Claude Desktop settings

### Getting Help

1. Check the logs when running manually
2. Use non-headless mode to see what's happening
3. Test individual components with `examples/test_setup.py`
4. Review `examples/usage_examples.md` for patterns

## Environment Configuration

Create a `.env` file in the project root:

```bash
cp examples/.env.template .env
```

Edit `.env` to customize:
- Browser type (chrome, firefox, edge)
- Headless mode (true/false)
- Window size
- Timeouts
- Download directory

## Next Steps

1. Read `examples/usage_examples.md` for detailed usage patterns
2. Review `USAGE.md` for comprehensive documentation
3. Explore the available tools and their parameters
4. Start building your own automation workflows!

## Security Notes

- The server can control your browser and access any website
- Use headless mode in production
- Be mindful of the websites you automate
- Respect robots.txt and rate limits
- Consider running in a sandboxed environment

## Performance Tips

- Use headless mode for better performance
- Set appropriate timeouts
- Batch operations when possible
- Use explicit waits instead of sleep
- Close browsers when done (handled automatically)

Happy automating! 🚀