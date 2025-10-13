#!/usr/bin/env python3
"""
Setup script for Browser Automation MCP Server
This script helps users get started quickly with the browser automation server.
"""

import os
import sys
import subprocess
import json
from pathlib import Path


def run_command(cmd, description):
    """Run a command and handle errors."""
    print(f"🔧 {description}...")
    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        if e.stdout:
            print(f"   stdout: {e.stdout}")
        if e.stderr:
            print(f"   stderr: {e.stderr}")
        return False


def check_uv():
    """Check if uv is installed."""
    try:
        subprocess.run(["uv", "--version"], check=True, capture_output=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def install_dependencies():
    """Install Python dependencies using uv."""
    print("📦 Installing dependencies...")
    
    if not check_uv():
        print("❌ uv is not installed. Please install it first:")
        print("   curl -LsSf https://astral.sh/uv/install.sh | sh")
        print("   Or visit: https://docs.astral.sh/uv/getting-started/installation/")
        return False
    
    # Install the project and dependencies
    if not run_command("uv sync", "Installing project dependencies"):
        return False
        
    print("✅ Dependencies installed successfully!")
    return True


def setup_claude_desktop():
    """Set up Claude Desktop configuration."""
    print("\n🤖 Setting up Claude Desktop configuration...")
    
    # Determine the Claude Desktop config path
    if sys.platform == "darwin":  # macOS
        config_dir = Path.home() / "Library/Application Support/Claude"
    elif sys.platform == "win32":  # Windows
        config_dir = Path.home() / "AppData/Roaming/Claude"
    else:  # Linux
        config_dir = Path.home() / ".config/claude"
    
    config_file = config_dir / "claude_desktop_config.json"
    
    # Create the config directory if it doesn't exist
    config_dir.mkdir(parents=True, exist_ok=True)
    
    # Get the current working directory
    cwd = Path.cwd()
    
    # Create the MCP server configuration
    server_config = {
        "mcpServers": {
            "browser-automation": {
                "command": "uv",
                "args": ["run", "python", "-m", "browser_mcp_server.server"],
                "cwd": str(cwd),
                "env": {
                    "BROWSER_HEADLESS": "false",
                    "BROWSER_TYPE": "chrome",
                    "BROWSER_TIMEOUT": "30"
                }
            }
        }
    }
    
    # Read existing config or create new one
    if config_file.exists():
        try:
            with open(config_file, 'r') as f:
                existing_config = json.load(f)
            
            # Merge the configurations
            if "mcpServers" not in existing_config:
                existing_config["mcpServers"] = {}
            
            existing_config["mcpServers"]["browser-automation"] = server_config["mcpServers"]["browser-automation"]
            
            final_config = existing_config
            print("📝 Updated existing Claude Desktop configuration")
        except json.JSONDecodeError:
            print("⚠️  Existing config file is invalid, creating new one")
            final_config = server_config
    else:
        final_config = server_config
        print("📝 Created new Claude Desktop configuration")
    
    # Write the configuration
    try:
        with open(config_file, 'w') as f:
            json.dump(final_config, f, indent=2)
        
        print(f"✅ Claude Desktop configuration saved to: {config_file}")
        print("\n📋 Configuration details:")
        print(f"   Server name: browser-automation")
        print(f"   Working directory: {cwd}")
        print(f"   Browser type: Chrome (headless)")
        print("\n🔄 Please restart Claude Desktop to load the new configuration")
        
        return True
    except Exception as e:
        print(f"❌ Failed to write configuration: {e}")
        return False


def test_server():
    """Test the server installation."""
    print("\n🧪 Testing server installation...")
    
    # Test import
    try:
        import browser_mcp_server
        print("✅ Server package imports successfully")
    except ImportError as e:
        print(f"❌ Failed to import server package: {e}")
        return False
    
    # Test running server with --help
    if not run_command("uv run python -m browser_mcp_server.server --help", 
                      "Testing server command"):
        return False
    
    print("✅ Server installation test passed!")
    return True


def main():
    """Main setup function."""
    print("🚀 Browser Automation MCP Server Setup")
    print("=" * 50)
    
    # Step 1: Install dependencies
    if not install_dependencies():
        print("\n❌ Setup failed at dependency installation")
        return 1
    
    # Step 2: Test server
    if not test_server():
        print("\n❌ Setup failed at server testing")
        return 1
    
    # Step 3: Set up Claude Desktop (optional)
    setup_claude = input("\n🤖 Set up Claude Desktop configuration? (y/n): ").lower().strip()
    if setup_claude in ['y', 'yes']:
        if not setup_claude_desktop():
            print("\n⚠️  Claude Desktop setup failed, but server is ready to use manually")
    else:
        print("\n📝 Skipping Claude Desktop setup")
    
    # Final instructions
    print("\n" + "=" * 50)
    print("🎉 Setup completed successfully!")
    print("\n📖 Next steps:")
    print("   1. To run the server manually:")
    print("      uv run python -m browser_mcp_server.server")
    print("\n   2. To use with Claude Desktop:")
    print("      - Restart Claude Desktop if you configured it")
    print("      - The 'browser-automation' server should appear in Claude")
    print("\n   3. Available environment variables:")
    print("      - BROWSER_TYPE=chrome|firefox|edge")
    print("      - BROWSER_HEADLESS=true|false") 
    print("      - BROWSER_TIMEOUT=30")
    print("\n   4. Check the README.md and USAGE.md files for detailed documentation")
    print("\n🔒 Security reminder: This server can control browsers and access websites.")
    print("    Use responsibly and in compliance with website terms of service.")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())