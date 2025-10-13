#!/usr/bin/env python3
"""
Simple script to test the get_page_source functionality.

This script demonstrates how to use the browser automation to:
1. Navigate to a website
2. Get the page source
3. Save it to a file

Run this from the LAM-mcp directory.
"""

import os
import sys
from datetime import datetime
from pathlib import Path


def test_page_source_extraction():
    """Test function that uses the browser manager to get page source."""
    
    # Import the browser manager from the local module
    from browser_mcp_server.browser_utils import browser_manager
    
    # Configuration
    url = "https://httpbin.org/html"  # Simple test page
    output_dir = "page_sources"
    
    try:
        print("🚀 Starting page source extraction test...")
        print(f"URL: {url}")
        
        # Navigate to the URL
        print("\n📍 Navigating to URL...")
        nav_result = browser_manager.navigate_to_url(url)
        
        if not nav_result.get('success', False):
            print(f"❌ Navigation failed: {nav_result.get('error')}")
            return False
        
        print(f"✅ Successfully navigated to: {nav_result.get('url')}")
        print(f"📄 Page title: {nav_result.get('title')}")
        
        # Get page source
        print("\n📥 Retrieving page source...")
        source_result = browser_manager.get_page_source()
        
        if not source_result.get('success', False):
            print(f"❌ Failed to get page source: {source_result.get('error')}")
            return False
        
        # Prepare output file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"{output_dir}/page_source_test_{timestamp}.html"
        
        # Create output directory
        Path(output_dir).mkdir(exist_ok=True)
        
        # Save page source to file
        print(f"\n💾 Saving page source to: {output_file}")
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(source_result['source'])
        
        # Get file info
        file_size = os.path.getsize(output_file)
        
        print(f"✅ Page source saved successfully!")
        print(f"   📁 File: {output_file}")
        print(f"   📊 Size: {file_size:,} bytes")
        
        # Show a preview of the content
        lines = source_result['source'].split('\n')
        print(f"\n📖 Content preview (first 5 lines):")
        for i, line in enumerate(lines[:5]):
            print(f"   {i+1}: {line[:80]}{'...' if len(line) > 80 else ''}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during extraction: {str(e)}")
        return False
    
    finally:
        # Clean up browser
        try:
            print("\n🔧 Closing browser...")
            browser_manager.stop_browser()
            print("✅ Browser closed successfully.")
        except Exception as e:
            print(f"⚠️  Warning: Error closing browser: {e}")


def advanced_extraction_example():
    """Advanced example with multiple pages."""
    
    from browser_mcp_server.browser_utils import browser_manager
    
    urls = [
        "https://httpbin.org/html",
        "https://httpbin.org/json",
        "https://example.com"
    ]
    
    output_dir = "page_sources"
    Path(output_dir).mkdir(exist_ok=True)
    
    print("🔄 Advanced extraction: Multiple pages")
    print("=" * 50)
    
    for i, url in enumerate(urls, 1):
        print(f"\n📍 Processing {i}/{len(urls)}: {url}")
        
        try:
            # Navigate
            nav_result = browser_manager.navigate_to_url(url)
            if not nav_result.get('success'):
                print(f"❌ Navigation failed: {nav_result.get('error')}")
                continue
            
            # Get source
            source_result = browser_manager.get_page_source()
            if not source_result.get('success'):
                print(f"❌ Source extraction failed: {source_result.get('error')}")
                continue
            
            # Save to file
            safe_name = url.replace('https://', '').replace('http://', '').replace('/', '_').replace(':', '_')
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"{output_dir}/{safe_name}_{timestamp}.html"
            
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(source_result['source'])
            
            file_size = os.path.getsize(output_file)
            print(f"✅ Saved: {output_file} ({file_size:,} bytes)")
            
        except Exception as e:
            print(f"❌ Error with {url}: {str(e)}")
    
    print("\n🎉 Advanced extraction completed!")


def main():
    """Main function."""
    print("=" * 60)
    print("Page Source Extraction Test Script")
    print("=" * 60)
    
    if len(sys.argv) > 1 and sys.argv[1] == "advanced":
        advanced_extraction_example()
    else:
        print("Running basic test (use 'advanced' argument for multiple pages)")
        test_page_source_extraction()
    
    print("\n✨ Script completed!")


if __name__ == "__main__":
    main()