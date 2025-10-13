"""Entry point for running the browser MCP server as a module."""

import sys
from browser_mcp_server.server import main

if __name__ == "__main__":
    sys.exit(main())