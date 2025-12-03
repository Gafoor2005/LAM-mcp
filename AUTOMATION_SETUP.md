# Browser Automation MCP - Best Practices Integration

## What Was Added

The MCP server now includes **automation best practices** as a built-in prompt that any MCP client can access. This ensures consistent, reliable automation behavior across all clients (Claude Desktop, VS Code, etc.).

## How It Works

### 1. Server-Side (Already Implemented)

The server now exposes:
- **Prompt**: `automation_best_practices` - Contains all the automation guidelines
- **Instructions constant**: `AUTOMATION_INSTRUCTIONS` - The actual best practices text

### 2. Client-Side Usage

#### Option A: Claude Desktop (Automatic)

Claude Desktop can automatically load prompts. Add to your conversation:

```
Please load the automation_best_practices prompt and follow those guidelines for all browser automation tasks.
```

Or in your `claude_desktop_config.json`, you can reference it in a custom instruction.

#### Option B: VS Code Copilot (Manual Reference)

In VS Code, you can create a `.github/copilot-instructions.md` file that references the MCP's guidelines:

```markdown
# Browser Automation Instructions

When using the Browser Automation MCP server, always follow these practices:
- Load and follow the automation_best_practices prompt from the MCP server
- Check page state before actions
- Handle popups proactively
- Verify all actions
- Track progress
```

#### Option C: Programmatic Access

Any MCP client can call:
```python
# Get the prompt
result = mcp_client.get_prompt("automation_best_practices")
instructions = result.messages[0].content
```

## Best Practices Summary

The prompt includes:

1. **Check Page State First** - Always analyze before acting
2. **Handle Popups Proactively** - Close banners/modals before interaction
3. **Smart Element Selection** - Use context-aware selectors
4. **Track Progress** - Monitor what works/fails
5. **Verify Actions** - Confirm results after each step
6. **Session Context Flow** - Proper workflow sequence
7. **Error Recovery** - Fallback strategies

## Example Workflow (Baked Into Instructions)

```
Navigate → Close Popups → Analyze Page → Find Elements → Take Action → Verify Result
```

## Testing the Integration

1. Start your MCP server
2. In your MCP client, request: "Show me the automation_best_practices prompt"
3. The client should display the full guidelines
4. Future automation requests will automatically follow these practices

## Benefits

- ✅ **Consistency**: Same behavior across all clients
- ✅ **Reliability**: Fewer automation failures
- ✅ **Autonomy**: Less need for manual intervention
- ✅ **Learning**: Server "remembers" best practices
- ✅ **Scalability**: Works for any automation task

## For AI Agents

When an AI agent (like Claude or Copilot) connects to this MCP server, it should:

1. Load the `automation_best_practices` prompt at the start
2. Follow the guidelines for all automation tasks
3. Reference specific practices when encountering issues
4. Use the session tracking tools to learn and adapt

This makes the automation truly autonomous and reliable!
