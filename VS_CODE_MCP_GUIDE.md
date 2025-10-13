# 🚀 VS Code MCP Setup Guide

Your browser automation MCP server is now configured for VS Code with multiple integration options.

## 🔌 Extensions Installed

The following extensions provide MCP integration:

1. **Cline (Claude Dev)** - Autonomous coding agent with MCP support
2. **Copilot MCP** - Search and manage MCP servers  
3. **VSCode MCP Server** - Native VS Code MCP integration
4. **MCP Server Runner** - Manage and run MCP servers locally

## ⚙️ Configuration Files Added

### `.vscode/settings.json`
- MCP server configuration for multiple extensions
- Environment variables for browser automation
- Working directory and Python path settings

### `.vscode/tasks.json` 
- **Start Browser MCP Server**: Launch the server manually
- **Test Browser MCP Server**: Run comprehensive tests
- **Install MCP Dependencies**: Reinstall dependencies

### `.vscode/launch.json`
- Debug configuration for the MCP server
- Integrated terminal support
- Environment variable configuration

### `.vscode/extensions.json`
- Recommended extensions for MCP development
- Python and debugging support extensions

## 🎯 How to Use

### Option 1: Cline (Claude Dev) Extension

1. **Install the extension** (should prompt automatically)
2. **Open Command Palette** (`Ctrl+Shift+P`)
3. **Run**: `Cline: Open Cline`
4. **Configure API**: Add your Claude API key
5. **MCP Server**: Should auto-detect your `browser-automation` server

**Test with Cline:**
```
"Navigate to example.com and take a screenshot"
"Search Google for 'VS Code extensions' and extract the top 5 results"
"Fill out a contact form on a website"
```

### Option 2: GitHub Copilot + MCP Extensions

1. **Install Copilot MCP extension**
2. **Open Chat** (`Ctrl+Shift+I`)
3. **Type**: `@mcp` to see available MCP servers
4. **Use browser automation tools** through Copilot Chat

### Option 3: MCP Server Runner

1. **Install MCP Server Runner**
2. **Open Command Palette**
3. **Run**: `MCP: Start Server`
4. **Select**: `browser-automation`
5. **Monitor status** in the status bar

### Option 4: VS Code Tasks (Manual)

**Start the server:**
- `Ctrl+Shift+P` → `Tasks: Run Task` → `Start Browser MCP Server`

**Test the server:**
- `Ctrl+Shift+P` → `Tasks: Run Task` → `Test Browser MCP Server`

**Debug the server:**
- `F5` or `Ctrl+F5` to launch with debugger

## 🔧 Available Tools in VS Code

Your MCP server provides these tools for AI assistants:

| Tool | Purpose | VS Code Usage |
|------|---------|---------------|
| `navigate_to_url` | Navigate to websites | "Go to example.com" |
| `click_element` | Click page elements | "Click the login button" |
| `type_text` | Fill input fields | "Type 'hello' in the search box" |
| `take_screenshot` | Capture screenshots | "Take a screenshot of this page" |
| `extract_text` | Get page content | "Extract all headings from this page" |
| `extract_links` | Get all page links | "Get all links from this website" |
| `fill_form` | Automated form filling | "Fill out this contact form" |
| `execute_javascript` | Run custom JS | "Execute: alert('Hello World')" |
| `scroll_page` | Page scrolling | "Scroll to the bottom of the page" |
| `wait_for_element` | Wait for content | "Wait for the modal to appear" |
| `get_cookies` | Retrieve cookies | "Get all cookies from this site" |
| `set_cookies` | Set browser cookies | "Set authentication cookies" |
| `get_page_source` | Get HTML source | "Get the page source code" |

## 💡 Example Workflows

### Web Scraping with Cline
```
"I need to scrape product information from an e-commerce site. 
Navigate to the products page, extract all product names and prices, 
and save the data to a CSV file."
```

### Automated Testing
```
"Create a test script that navigates to our login page, 
enters test credentials, verifies successful login, 
and takes screenshots at each step."
```

### Form Automation
```
"Go to the contact form on example.com and fill it out with 
test data: name 'John Doe', email 'john@test.com', 
message 'This is a test message'."
```

## 🐛 Troubleshooting

### Server Not Starting
1. Check Python path in VS Code settings
2. Verify virtual environment is activated
3. Run the "Test Browser MCP Server" task

### Extension Not Detecting Server
1. Reload VS Code window (`Ctrl+Shift+P` → `Developer: Reload Window`)
2. Check `.vscode/settings.json` configuration
3. Verify MCP extensions are installed and enabled

### Browser Issues
1. Set `BROWSER_HEADLESS=false` in settings for debugging
2. Try different browser: `BROWSER_TYPE=firefox`
3. Check if browser is installed and accessible

### Permission Errors
1. Run VS Code as administrator
2. Check file permissions in the project directory
3. Verify Python virtual environment permissions

## 📚 Additional Resources

- **MCP Documentation**: [Model Context Protocol](https://modelcontextprotocol.io/)
- **Cline Documentation**: Check extension documentation in VS Code
- **Browser Automation**: See `examples/usage_examples.md`
- **Configuration**: See `examples/.env.template`

## 🔐 Security Notes

- The MCP server can control browsers and access websites
- Always review automation scripts before execution
- Use headless mode in production environments
- Be mindful of website terms of service and rate limits
- Consider running in sandboxed environments for security

## 🚀 Next Steps

1. **Install recommended extensions** when prompted
2. **Test the basic functionality** with simple commands
3. **Explore advanced workflows** in `examples/usage_examples.md`
4. **Customize environment variables** in `.vscode/settings.json`
5. **Build complex automation workflows** with your AI assistant

Your browser automation MCP server is now fully integrated with VS Code! 🎉