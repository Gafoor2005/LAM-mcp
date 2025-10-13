# Example Configurations for Different MCP Clients

This directory contains example configurations for various MCP clients.

## Claude Desktop Configuration

### Basic Configuration (`claude_desktop_config.json`)

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

### Advanced Configuration with Custom Settings

```json
{
  "mcpServers": {
    "browser-automation": {
      "command": "uv", 
      "args": ["run", "python", "-m", "browser_mcp_server.server"],
      "cwd": "/path/to/LAM-mcp",
      "env": {
        "BROWSER_HEADLESS": "false",
        "BROWSER_TYPE": "firefox",
        "BROWSER_TIMEOUT": "45",
        "BROWSER_WINDOW_SIZE": "1366x768",
        "BROWSER_DOWNLOAD_DIR": "/Users/username/Downloads/automation"
      }
    }
  }
}
```

### Configuration File Locations

- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`  
- **Linux**: `~/.config/claude/claude_desktop_config.json`

## VS Code MCP Extension

For VS Code with MCP support, add to your MCP configuration:

```json
{
  "mcp": {
    "servers": {
      "browser-automation": {
        "type": "stdio",
        "command": "uv",
        "args": ["run", "python", "-m", "browser_mcp_server.server"],
        "cwd": "/path/to/LAM-mcp"
      }
    }
  }
}
```

## Other MCP Clients

### Generic STDIO Configuration

Most MCP clients support stdio transport. Use these parameters:

- **Command**: `uv`
- **Arguments**: `["run", "python", "-m", "browser_mcp_server.server"]`
- **Working Directory**: `/path/to/LAM-mcp`
- **Transport**: `stdio`

### SSE/HTTP Configuration  

For web-based clients or those supporting HTTP transport:

1. Start the server with SSE transport:
   ```bash
   uv run python -m browser_mcp_server.server --transport sse --port 8000
   ```

2. Connect to: `http://localhost:8000/sse`

### Environment Variables Reference

Set these in your MCP client configuration:

```json
{
  "env": {
    "BROWSER_TYPE": "chrome",           // chrome, firefox, edge
    "BROWSER_HEADLESS": "true",         // true, false  
    "BROWSER_TIMEOUT": "30",            // seconds
    "BROWSER_WINDOW_SIZE": "1920x1080", // WxH format
    "BROWSER_USER_AGENT": "Custom Agent String",
    "BROWSER_DOWNLOAD_DIR": "/path/to/downloads"
  }
}
```

## Testing Configuration

To test if your configuration works:

1. **Manual Test**:
   ```bash
   cd /path/to/LAM-mcp
   uv run python -m browser_mcp_server.server --transport stdio
   ```

2. **With MCP Inspector**:
   ```bash
   npx @modelcontextprotocol/inspector uv run python -m browser_mcp_server.server
   ```

3. **Check Available Tools**:
   The server should expose tools like:
   - `navigate_to_url`
   - `click_element` 
   - `type_text`
   - `take_screenshot`
   - And many more...

## Troubleshooting

### Common Issues

1. **Command not found**: 
   - Ensure `uv` is installed and in PATH
   - Use full path to uv: `/usr/local/bin/uv`

2. **Permission errors**:
   - Check file permissions on the project directory
   - Ensure browser drivers can be downloaded

3. **Browser won't start**:
   - Try different browser: `"BROWSER_TYPE": "firefox"`
   - Check if browser is installed
   - Try headless mode: `"BROWSER_HEADLESS": "true"`

4. **Module not found**:
   - Ensure working directory is set correctly
   - Run `uv sync` in the project directory

### Debug Mode

Enable verbose logging:

```json
{
  "env": {
    "PYTHONPATH": "/path/to/LAM-mcp",
    "BROWSER_HEADLESS": "false"
  }
}
```

## Security Considerations

When configuring for production:

1. **Use headless mode**: `"BROWSER_HEADLESS": "true"`
2. **Set download restrictions**: Specify safe download directory
3. **Network isolation**: Run in sandboxed environment
4. **Monitor activities**: Enable logging and monitoring
5. **Rate limiting**: Consider timeout and usage limits