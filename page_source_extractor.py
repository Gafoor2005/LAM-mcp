#!/usr/bin/env python3
"""
Configurable Page Source Extractor

This script provides a flexible way to extract page sources from websites
using the browser automation utilities. It supports:

- Multiple URLs
- Custom output directories
- Different file naming schemes
- Error handling and retry logic
- Detailed logging

Configuration can be done via:
1. Command line arguments
2. Configuration file (JSON)
3. Environment variables
"""

import os
import sys
import json
import argparse
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any
import time


class PageSourceExtractor:
    """Main class for extracting page sources."""
    
    def __init__(self, config: Dict[str, Any] = None):
        """Initialize with configuration."""
        self.config = config or {}
        self.browser_manager = None
        self.results = []
        
    def setup_browser(self):
        """Setup browser manager."""
        try:
            from browser_mcp_server.browser_utils import browser_manager
            self.browser_manager = browser_manager
            print("✅ Browser manager initialized")
            return True
        except ImportError as e:
            print(f"❌ Failed to import browser manager: {e}")
            print("Make sure you're running this script from the LAM-mcp directory")
            return False
    
    def extract_page_source(self, url: str, output_file: str = None) -> Dict[str, Any]:
        """Extract page source from a single URL."""
        
        if not self.browser_manager:
            return {"success": False, "error": "Browser manager not initialized"}
        
        try:
            print(f"🔗 Processing: {url}")
            
            # Navigate to URL
            nav_result = self.browser_manager.navigate_to_url(url)
            if not nav_result.get('success', False):
                return {
                    "success": False,
                    "url": url,
                    "error": f"Navigation failed: {nav_result.get('error')}"
                }
            
            # Add delay if configured
            delay = self.config.get('delay_between_requests', 0)
            if delay > 0:
                print(f"⏳ Waiting {delay} seconds...")
                time.sleep(delay)
            
            # Get page source
            source_result = self.browser_manager.get_page_source()
            if not source_result.get('success', False):
                return {
                    "success": False,
                    "url": url,
                    "error": f"Source extraction failed: {source_result.get('error')}"
                }
            
            # Generate output filename if not provided
            if not output_file:
                output_file = self.generate_filename(url)
            
            # Ensure output directory exists
            output_path = Path(output_file)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Save to file
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(source_result['source'])
            
            file_size = os.path.getsize(output_file)
            
            result = {
                "success": True,
                "url": url,
                "output_file": output_file,
                "file_size": file_size,
                "page_title": nav_result.get('title', 'N/A'),
                "timestamp": datetime.now().isoformat()
            }
            
            print(f"✅ Saved: {output_file} ({file_size:,} bytes)")
            return result
            
        except Exception as e:
            return {
                "success": False,
                "url": url,
                "error": f"Unexpected error: {str(e)}"
            }
    
    def generate_filename(self, url: str) -> str:
        """Generate output filename based on URL and configuration."""
        
        # Clean URL for filename
        safe_name = (url.replace('https://', '')
                        .replace('http://', '')
                        .replace('/', '_')
                        .replace(':', '_')
                        .replace('?', '_')
                        .replace('&', '_')
                        .replace('=', '_'))
        
        # Limit length
        if len(safe_name) > 100:
            safe_name = safe_name[:100]
        
        # Add timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Get output directory
        output_dir = self.config.get('output_directory', 'page_sources')
        
        # Choose naming scheme
        naming_scheme = self.config.get('naming_scheme', 'url_timestamp')
        
        if naming_scheme == 'timestamp_only':
            filename = f"page_source_{timestamp}.html"
        elif naming_scheme == 'url_only':
            filename = f"{safe_name}.html"
        else:  # url_timestamp (default)
            filename = f"{safe_name}_{timestamp}.html"
        
        return os.path.join(output_dir, filename)
    
    def extract_multiple(self, urls: List[str]) -> List[Dict[str, Any]]:
        """Extract page sources from multiple URLs."""
        
        results = []
        total = len(urls)
        
        print(f"🚀 Starting extraction for {total} URLs")
        print("=" * 60)
        
        for i, url in enumerate(urls, 1):
            print(f"\n📍 Processing {i}/{total}: {url}")
            
            result = self.extract_page_source(url)
            results.append(result)
            self.results.append(result)
            
            if not result['success']:
                print(f"❌ Failed: {result['error']}")
            
            # Add delay between requests if configured
            if i < total:
                delay = self.config.get('delay_between_requests', 0)
                if delay > 0:
                    print(f"⏳ Waiting {delay} seconds before next request...")
                    time.sleep(delay)
        
        return results
    
    def save_report(self, results: List[Dict[str, Any]]) -> str:
        """Save extraction report to JSON file."""
        
        report = {
            "extraction_date": datetime.now().isoformat(),
            "total_urls": len(results),
            "successful": len([r for r in results if r['success']]),
            "failed": len([r for r in results if not r['success']]),
            "config": self.config,
            "results": results
        }
        
        report_file = f"extraction_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"📊 Report saved: {report_file}")
        return report_file
    
    def cleanup(self):
        """Clean up resources."""
        if self.browser_manager:
            try:
                self.browser_manager.stop_browser()
                print("🔧 Browser closed")
            except Exception as e:
                print(f"⚠️  Warning: Error closing browser: {e}")


def load_config_file(config_path: str) -> Dict[str, Any]:
    """Load configuration from JSON file."""
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"❌ Error loading config file {config_path}: {e}")
        return {}


def create_sample_config():
    """Create a sample configuration file."""
    
    sample_config = {
        "urls": [
            "https://httpbin.org/html",
            "https://example.com",
            "https://httpbin.org/json"
        ],
        "output_directory": "extracted_pages",
        "naming_scheme": "url_timestamp",
        "delay_between_requests": 1,
        "generate_report": True,
        "browser_config": {
            "headless": False,
            "timeout": 30
        }
    }
    
    config_file = "page_source_config.json"
    with open(config_file, 'w', encoding='utf-8') as f:
        json.dump(sample_config, f, indent=2, ensure_ascii=False)
    
    print(f"📁 Sample configuration created: {config_file}")
    return config_file


def main():
    """Main function with command line interface."""
    
    parser = argparse.ArgumentParser(description="Extract page sources from websites")
    parser.add_argument("urls", nargs="*", help="URLs to extract (or use --config)")
    parser.add_argument("--config", "-c", help="Configuration file (JSON)")
    parser.add_argument("--output-dir", "-o", default="page_sources", help="Output directory")
    parser.add_argument("--delay", "-d", type=float, default=0, help="Delay between requests (seconds)")
    parser.add_argument("--create-config", action="store_true", help="Create sample configuration file")
    parser.add_argument("--report", action="store_true", help="Generate extraction report")
    
    args = parser.parse_args()
    
    # Create sample config if requested
    if args.create_config:
        create_sample_config()
        return
    
    # Load configuration
    config = {}
    if args.config:
        config = load_config_file(args.config)
    
    # Override with command line arguments
    if args.output_dir:
        config['output_directory'] = args.output_dir
    if args.delay:
        config['delay_between_requests'] = args.delay
    if args.report:
        config['generate_report'] = True
    
    # Get URLs
    urls = args.urls or config.get('urls', [])
    
    if not urls:
        print("❌ No URLs provided. Use --help for usage info or --create-config for a sample.")
        print("Example: python page_source_extractor.py https://example.com")
        return
    
    # Create extractor
    extractor = PageSourceExtractor(config)
    
    # Setup browser
    if not extractor.setup_browser():
        return
    
    try:
        # Extract page sources
        results = extractor.extract_multiple(urls)
        
        # Print summary
        successful = len([r for r in results if r['success']])
        failed = len([r for r in results if not r['success']])
        
        print("\n" + "=" * 60)
        print("📊 EXTRACTION SUMMARY")
        print("=" * 60)
        print(f"Total URLs: {len(results)}")
        print(f"Successful: {successful}")
        print(f"Failed: {failed}")
        
        if failed > 0:
            print("\n❌ Failed URLs:")
            for result in results:
                if not result['success']:
                    print(f"   • {result['url']}: {result['error']}")
        
        # Generate report if requested
        if config.get('generate_report', False):
            extractor.save_report(results)
        
        print("\n✨ Extraction completed!")
        
    finally:
        extractor.cleanup()


if __name__ == "__main__":
    main()