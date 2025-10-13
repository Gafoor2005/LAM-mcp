#!/usr/bin/env python3
"""
VS Code MCP Integration Test
This script tests the MCP server integration with VS Code's native MCP support.
"""

import json
import subprocess
import sys
import os
from pathlib import Path

def test_mcp_server():
    """Test MCP server startup and basic functionality"""
    print("🧪 Testing VS Code MCP Integration...")
    
    # Get the project root
    project_root = Path(__file__).parent.parent
    python_exe = project_root / ".venv" / "Scripts" / "python.exe"
    
    if not python_exe.exists():
        print("❌ Virtual environment not found. Please run: python -m venv .venv")
        return False
    
    print(f"📁 Project root: {project_root}")
    print(f"🐍 Python executable: {python_exe}")
    
    # Test server import
    try:
        cmd = [str(python_exe), "-c", "import browser_mcp_server.server; print('✅ Server module imported successfully')"]
        result = subprocess.run(cmd, cwd=str(project_root), capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            print(result.stdout.strip())
        else:
            print(f"❌ Import failed: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Import test failed: {e}")
        return False
    
    # Test MCP protocol initialization
    try:
        print("🔄 Testing MCP protocol initialization...")
        
        # Start server process
        server_cmd = [str(python_exe), "-m", "browser_mcp_server.server"]
        process = subprocess.Popen(
            server_cmd,
            cwd=str(project_root),
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            env={**os.environ, "BROWSER_HEADLESS": "true"}
        )
        
        # Send initialize request
        init_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {
                    "name": "vscode-test",
                    "version": "1.0.0"
                }
            }
        }
        
        request_json = json.dumps(init_request) + "\n"
        process.stdin.write(request_json)
        process.stdin.flush()
        
        # Wait for response with timeout
        try:
            stdout, stderr = process.communicate(timeout=5)
            
            if stdout and "result" in stdout:
                print("✅ MCP server initialized successfully")
                print(f"📝 Response preview: {stdout[:100]}...")
                return True
            else:
                print(f"❌ No valid response. Stderr: {stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            process.kill()
            print("❌ Server initialization timed out")
            return False
            
    except Exception as e:
        print(f"❌ MCP protocol test failed: {e}")
        return False

def create_vscode_test_workspace():
    """Create a test workspace configuration"""
    print("📝 Creating VS Code test workspace...")
    
    workspace_config = {
        "folders": [
            {
                "name": "Browser MCP Server",
                "path": "."
            }
        ],
        "settings": {
            "languageModels.mcpServers": {
                "browser-automation": {
                    "command": "${workspaceFolder}/.venv/Scripts/python.exe",
                    "args": ["-m", "browser_mcp_server.server"],
                    "env": {
                        "BROWSER_HEADLESS": "true",
                        "BROWSER_TYPE": "chrome",
                        "BROWSER_TIMEOUT": "30"
                    }
                }
            }
        },
        "tasks": {
            "version": "2.0.0",
            "tasks": [
                {
                    "label": "Start MCP Server",
                    "type": "shell",
                    "command": "${workspaceFolder}/.venv/Scripts/python.exe",
                    "args": ["-m", "browser_mcp_server.server"],
                    "group": "build",
                    "presentation": {
                        "reveal": "always"
                    }
                }
            ]
        }
    }
    
    # Save workspace file
    workspace_file = Path(__file__).parent.parent / "browser-mcp-server.code-workspace"
    
    with open(workspace_file, 'w') as f:
        json.dump(workspace_config, f, indent=2)
    
    print(f"✅ Workspace file created: {workspace_file}")
    return workspace_file

def main():
    """Main test function"""
    print("🚀 VS Code MCP Integration Test\n")
    
    success = True
    
    # Test MCP server
    if not test_mcp_server():
        success = False
    
    # Create workspace
    try:
        workspace_file = create_vscode_test_workspace()
        print(f"\n📂 Open in VS Code: code \"{workspace_file}\"")
    except Exception as e:
        print(f"❌ Workspace creation failed: {e}")
        success = False
    
    print("\n" + "="*50)
    if success:
        print("🎉 VS Code MCP integration test completed successfully!")
        print("\n📋 Next steps:")
        print("1. Open the workspace file in VS Code")
        print("2. Install GitHub Copilot extension if not already installed")
        print("3. Open Copilot Chat (Ctrl+Shift+I)")
        print("4. The browser-automation MCP server should be available")
        print("\n💡 Test commands in Copilot Chat:")
        print("- 'What MCP servers are available?'")
        print("- 'Use the browser automation tools to navigate to example.com'")
        return 0
    else:
        print("❌ Some tests failed. Please check the errors above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())