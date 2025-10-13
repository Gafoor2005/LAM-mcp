#!/usr/bin/env python3
"""
Test script to verify browser MCP server is working correctly.
Run this script to test basic functionality.
"""

import sys
import os
import subprocess
import json
import time

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from browser_mcp_server.browser_utils import BrowserManager

def test_browser_manager():
    """Test the BrowserManager class directly."""
    print("🧪 Testing BrowserManager...")
    
    try:
        # Set environment variable for headless mode
        os.environ['BROWSER_HEADLESS'] = 'true'
        
        # Test browser initialization
        browser_manager = BrowserManager()
        print("✅ BrowserManager created successfully")
        
        # Test browser startup
        browser_manager.start_browser()
        print("✅ Browser started successfully")
        
        # Test navigation
        browser_manager.navigate_to_url("https://example.com")
        print("✅ Navigation to example.com successful")
        
        # Test screenshot
        screenshot_result = browser_manager.take_screenshot()
        if screenshot_result.get("success"):
            print("✅ Screenshot captured successfully")
        else:
            print(f"❌ Screenshot failed: {screenshot_result.get('error')}")
            
        # Test text extraction
        title_result = browser_manager.get_element_text("h1")
        if title_result.get("success"):
            print(f"✅ Page title extracted: {title_result.get('text')}")
        else:
            print(f"❌ Text extraction failed: {title_result.get('error')}")
        
        # Test page source
        source_result = browser_manager.get_page_source()
        if source_result.get("success") and source_result.get("source"):
            print("✅ Page source retrieved successfully")
        else:
            print("❌ Page source not retrieved")
            
        # Cleanup
        browser_manager.stop_browser()
        print("✅ Browser closed successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ BrowserManager test failed: {e}")
        return False

def test_mcp_server():
    """Test the MCP server via subprocess."""
    print("\n🧪 Testing MCP Server...")
    
    try:
        # Start the server
        cmd = [sys.executable, "-m", "browser_mcp_server.server"]
        process = subprocess.Popen(
            cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        )
        
        # Send initialize request
        initialize_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {
                    "name": "test-client",
                    "version": "1.0.0"
                }
            }
        }
        
        # Send the request
        request_str = json.dumps(initialize_request) + "\n"
        process.stdin.write(request_str)
        process.stdin.flush()
        
        # Wait a moment for response
        time.sleep(2)
        
        # Try to read response
        try:
            process.stdin.close()
            stdout, stderr = process.communicate(timeout=5)
            
            if stdout:
                print("✅ MCP Server responded successfully")
                print(f"Response preview: {stdout[:200]}...")
            else:
                print(f"❌ No response from MCP Server. Stderr: {stderr}")
                
        except subprocess.TimeoutExpired:
            process.kill()
            print("❌ MCP Server test timed out")
            return False
            
        return True
        
    except Exception as e:
        print(f"❌ MCP Server test failed: {e}")
        return False

def test_dependencies():
    """Test that all required dependencies are installed."""
    print("\n🧪 Testing Dependencies...")
    
    required_packages = [
        "selenium",
        "webdriver_manager", 
        "mcp",
        "PIL",  # Pillow imports as PIL
        "bs4"   # beautifulsoup4 imports as bs4
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package} is installed")
        except ImportError:
            print(f"❌ {package} is missing")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n❌ Missing packages: {missing_packages}")
        print("Run: uv add " + " ".join(missing_packages))
        return False
    
    return True

def test_browser_drivers():
    """Test that browser drivers can be downloaded."""
    print("\n🧪 Testing Browser Drivers...")
    
    try:
        from selenium import webdriver
        from webdriver_manager.chrome import ChromeDriverManager
        from selenium.webdriver.chrome.service import Service
        
        # Test Chrome driver download
        chrome_driver_path = ChromeDriverManager().install()
        print(f"✅ Chrome driver available: {chrome_driver_path}")
        
        return True
        
    except Exception as e:
        print(f"❌ Browser driver test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("🚀 Starting Browser MCP Server Tests\n")
    
    tests = [
        ("Dependencies", test_dependencies),
        ("Browser Drivers", test_browser_drivers),
        ("Browser Manager", test_browser_manager),
        ("MCP Server", test_mcp_server)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{'='*50}")
        print(f"Running {test_name} Test")
        print(f"{'='*50}")
        
        if test_func():
            passed += 1
            print(f"✅ {test_name} test PASSED")
        else:
            print(f"❌ {test_name} test FAILED")
    
    print(f"\n{'='*50}")
    print(f"Test Summary: {passed}/{total} tests passed")
    print(f"{'='*50}")
    
    if passed == total:
        print("🎉 All tests passed! Your browser MCP server is ready to use.")
        return 0
    else:
        print("⚠️  Some tests failed. Please fix the issues before using the server.")
        return 1

if __name__ == "__main__":
    sys.exit(main())