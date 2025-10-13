#!/usr/bin/env python3
"""
Script to get page source from a website and save it to a file.

This script uses the browser automation utilities to:
1. Navigate to a specified URL
2. Get the page source HTML
3. Save the HTML content to a file

Usage:
    python get_page_source_script.py [URL] [OUTPUT_FILE]
    
Example:
    python get_page_source_script.py https://example.com page_source.html
"""

import sys
import os
from datetime import datetime
from pathlib import Path

# Add the browser_mcp_server directory to Python path
script_dir = os.path.dirname(os.path.abspath(__file__))
browser_server_dir = os.path.join(script_dir, 'browser_mcp_server')
sys.path.insert(0, browser_server_dir)

try:
    from browser_utils import browser_manager
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    import time
except ImportError:
    print("Error: Could not import browser_utils. Make sure you're running this script from the LAM-mcp directory.")
    print(f"Script directory: {script_dir}")
    print(f"Looking for browser_utils in: {browser_server_dir}")
    sys.exit(1)


def wait_for_page_complete(driver, timeout=30):
    """
    Wait for page to be completely loaded including all network requests.
    
    Args:
        driver: Selenium WebDriver instance
        timeout: Maximum time to wait in seconds
    
    Returns:
        bool: True if page loaded completely, False if timeout
    """
    try:
        # Wait for document ready state
        WebDriverWait(driver, timeout).until(
            lambda d: d.execute_script("return document.readyState") == "complete"
        )
        print("✓ Document ready state: complete")
        
        # Wait for jQuery to finish if it exists
        try:
            WebDriverWait(driver, 5).until(
                lambda d: d.execute_script("return typeof jQuery === 'undefined' || jQuery.active == 0")
            )
            print("✓ jQuery requests completed")
        except:
            print("✓ No jQuery detected")
        
        # Wait for any pending network requests to finish
        # This uses a JavaScript technique to monitor network activity
        driver.execute_script("""
            window.networkActive = window.networkActive || 0;
            window.originalFetch = window.originalFetch || window.fetch;
            window.originalXHROpen = window.originalXHROpen || XMLHttpRequest.prototype.open;
            
            if (!window.networkMonitorSetup) {
                // Monitor fetch requests
                window.fetch = function(...args) {
                    window.networkActive++;
                    return window.originalFetch.apply(this, args).finally(() => {
                        window.networkActive--;
                    });
                };
                
                // Monitor XMLHttpRequest
                XMLHttpRequest.prototype.open = function(...args) {
                    window.networkActive++;
                    this.addEventListener('loadend', () => window.networkActive--);
                    return window.originalXHROpen.apply(this, args);
                };
                
                window.networkMonitorSetup = true;
            }
        """)
        
        # Wait a bit for any immediate network requests to start
        time.sleep(2)
        
        # Wait for network activity to settle
        network_timeout = 10  # seconds
        stable_time = 0
        check_interval = 0.5
        
        while stable_time < 3:  # Wait for 3 seconds of no network activity
            active_requests = driver.execute_script("return window.networkActive || 0")
            if active_requests == 0:
                stable_time += check_interval
            else:
                stable_time = 0
                print(f"⏳ Waiting for {active_requests} network requests to complete...")
            
            time.sleep(check_interval)
            network_timeout -= check_interval
            
            if network_timeout <= 0:
                print("⚠️ Network timeout reached, proceeding anyway")
                break
        
        print("✓ Network requests completed")
        
        # Additional wait for dynamic content rendering
        time.sleep(2)
        print("✓ Additional rendering time completed")
        
        return True
        
    except Exception as e:
        print(f"⚠️ Error waiting for page completion: {e}")
        return False


def get_page_source_and_save(url: str, output_file: str = None, encoding: str = 'utf-8', wait_for_complete: bool = True, save_comparison: bool = False):
    """
    Get page source from a URL and save it to a file.
    
    Args:
        url (str): The URL to navigate to
        output_file (str, optional): Path to save the HTML file. 
                                   If not provided, generates a filename based on URL and timestamp.
        encoding (str): File encoding (default: utf-8)
        wait_for_complete (bool): Whether to wait for complete page loading including network requests
        save_comparison (bool): Whether to save both raw and rendered versions for comparison
    
    Returns:
        dict: Result with success status, file path, and any error messages
    """
    try:
        print(f"Starting browser and navigating to: {url}")
        
        # Navigate to the URL
        nav_result = browser_manager.navigate_to_url(url)
        if not nav_result.get('success', False):
            return {
                'success': False,
                'error': f"Navigation failed: {nav_result.get('error', 'Unknown error')}"
            }
        
        print(f"Successfully navigated to: {nav_result.get('url')}")
        print(f"Page title: {nav_result.get('title')}")
        
        # Wait for complete page loading if requested
        if wait_for_complete:
            print("\n⏳ Waiting for complete page loading (including network requests)...")
            print("This ensures we get the final, fully-loaded page source.")
            wait_for_page_complete(browser_manager.driver)
            print("✅ Page loading completed!\n")
        
        # Get page source (now uses rendered DOM instead of raw page_source)
        print("Retrieving final page source (rendered DOM)...")
        source_result = browser_manager.get_rendered_html()
        
        if not source_result.get('success', False):
            return {
                'success': False,
                'error': f"Failed to get page source: {source_result.get('error', 'Unknown error')}"
            }
        
        # Show which method was used
        method_used = source_result.get('method', 'unknown')
        if method_used == 'rendered_dom':
            print("✅ Using rendered DOM (captures JavaScript-modified content)")
        elif method_used == 'page_source_fallback':
            print("⚠️ Using fallback page_source (may miss dynamic content)")
        else:
            print(f"ℹ️ Method used: {method_used}")
        
        # Generate output filename if not provided
        if output_file is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            domain = url.replace('https://', '').replace('http://', '').replace('/', '_').replace(':', '_')
            output_file = f"page_source_{domain.split('.')[0]}_{timestamp}.html"
        
        # Ensure output directory exists
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Save to file
        print(f"Saving page source to: {output_file}")
        with open(output_file, 'w', encoding=encoding) as f:
            f.write(source_result['source'])
        
        # Get file size for confirmation
        file_size = os.path.getsize(output_file)
        
        # Save comparison files if requested
        comparison_files = []
        if save_comparison:
            print("\n🔍 Saving comparison files (raw vs rendered)...")
            try:
                comparison_result = browser_manager.get_page_content_comparison()
                if comparison_result.get('success'):
                    # Generate comparison filenames
                    base_name = output_file.rsplit('.', 1)[0] if '.' in output_file else output_file
                    raw_file = f"{base_name}_raw.html"
                    rendered_file = f"{base_name}_rendered.html"
                    
                    # Save raw version
                    with open(raw_file, 'w', encoding=encoding) as f:
                        f.write(comparison_result['raw_source'])
                    
                    # Save rendered version  
                    with open(rendered_file, 'w', encoding=encoding) as f:
                        f.write(comparison_result['rendered_source'])
                    
                    comparison_files = [raw_file, rendered_file]
                    
                    # Print comparison stats
                    comp = comparison_result['comparison']
                    print(f"  📊 Raw HTML size: {comp['raw_size']:,} bytes")
                    print(f"  📊 Rendered HTML size: {comp['rendered_size']:,} bytes")
                    print(f"  📊 Size difference: {comp['size_difference']:+,} bytes ({comp['percentage_change']:+.1f}%)")
                    print(f"  💾 Saved: {raw_file}")
                    print(f"  💾 Saved: {rendered_file}")
                else:
                    print("  ⚠️ Could not generate comparison files")
            except Exception as e:
                print(f"  ⚠️ Error generating comparison: {e}")
        
        print(f"✅ Successfully saved page source!")
        print(f"   File: {output_file}")
        print(f"   Size: {file_size:,} bytes")
        
        return {
            'success': True,
            'file_path': output_file,
            'file_size': file_size,
            'page_title': nav_result.get('title'),
            'page_url': nav_result.get('url'),
            'method_used': source_result.get('method'),
            'comparison_files': comparison_files
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': f"Unexpected error: {str(e)}"
        }
    
    finally:
        # Clean up browser
        try:
            browser_manager.stop_browser()
            print("Browser closed.")
        except Exception as e:
            print(f"Error closing browser: {e}")


def main():
    """Main function to handle command line arguments and run the script."""
    
    # Default values
    default_url = "https://soundcloud.com/search?q=confession%20jason"
    default_output = None
    
    # Parse command line arguments
    wait_for_complete = True  # Default to waiting for complete loading
    save_comparison = False   # Default to not saving comparison
    
    if len(sys.argv) < 2:
        print("Usage: python get_page_source_script.py [URL] [OUTPUT_FILE] [--fast] [--compare]")
        print(f"Example: python get_page_source_script.py {default_url}")
        print("  --fast: Skip waiting for complete page loading (faster but may miss dynamic content)")
        print("  --compare: Save both raw and rendered HTML for comparison")
        print("\nUsing default URL for demonstration...")
        url = default_url
    else:
        url = sys.argv[1]
    
    if len(sys.argv) >= 3 and not sys.argv[2].startswith('--'):
        output_file = sys.argv[2]
    else:
        output_file = default_output
    
    # Check for flags
    if '--fast' in sys.argv:
        wait_for_complete = False
        print("⚡ Fast mode enabled - skipping complete page loading wait")
    
    if '--compare' in sys.argv:
        save_comparison = True
        print("🔍 Comparison mode enabled - will save both raw and rendered HTML")
    
    print("=" * 60)
    print("Page Source Extractor Script")
    print("=" * 60)
    print(f"URL: {url}")
    print(f"Output file: {output_file or 'Auto-generated'}")
    print(f"Complete loading: {'Yes' if wait_for_complete else 'No (fast mode)'}")
    print(f"Save comparison: {'Yes' if save_comparison else 'No'}")
    print("=" * 60)
    
    # Run the extraction
    result = get_page_source_and_save(url, output_file, wait_for_complete=wait_for_complete, save_comparison=save_comparison)
    
    # Print results
    if result['success']:
        print("\n🎉 SUCCESS!")
        print(f"Page source saved successfully to: {result['file_path']}")
        print(f"Page title: {result.get('page_title', 'N/A')}")
        print(f"File size: {result.get('file_size', 0):,} bytes")
        print(f"Method used: {result.get('method_used', 'unknown')}")
        
        if result.get('comparison_files'):
            print(f"Comparison files: {len(result['comparison_files'])} additional files saved")
    else:
        print("\n❌ FAILED!")
        print(f"Error: {result['error']}")
        sys.exit(1)


if __name__ == "__main__":
    main()