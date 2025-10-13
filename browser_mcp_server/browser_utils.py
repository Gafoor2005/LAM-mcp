"""Browser automation utilities for the MCP server."""

import os
import io
import logging
from typing import Dict, List, Any, Optional, Union
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.edge.service import Service as EdgeService
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium.common.exceptions import (
    TimeoutException, 
    NoSuchElementException, 
    ElementNotInteractableException,
    WebDriverException
)
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager
from webdriver_manager.microsoft import EdgeChromiumDriverManager
from bs4 import BeautifulSoup
from PIL import Image
import base64

logger = logging.getLogger(__name__)


class BrowserManager:
    """Manages browser instances and automation operations."""
    
    def __init__(self):
        self.driver: Optional[webdriver.Remote] = None
        self.browser_type = os.getenv('BROWSER_TYPE', 'chrome').lower()
        self.headless = os.getenv('BROWSER_HEADLESS', 'false').lower() == 'true'
        self.timeout = int(os.getenv('BROWSER_TIMEOUT', '30'))
        self.window_size = os.getenv('BROWSER_WINDOW_SIZE', '1920x1080')
        self.user_agent = os.getenv('BROWSER_USER_AGENT')
        self.download_dir = os.getenv('BROWSER_DOWNLOAD_DIR', '/tmp/downloads')
        
    def _get_chrome_options(self) -> ChromeOptions:
        """Get Chrome browser options."""
        options = ChromeOptions()
        
        if self.headless:
            # options.add_argument('--headless')
            pass  # Headless mode disabled for visibility
        
        # Common Chrome options for automation
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--disable-web-security')
        options.add_argument('--allow-running-insecure-content')
        options.add_argument(f'--window-size={self.window_size}')
        
        if self.user_agent:
            options.add_argument(f'--user-agent={self.user_agent}')
            
        # Download preferences
        prefs = {
            'download.default_directory': self.download_dir,
            'download.prompt_for_download': False,
            'download.directory_upgrade': True,
            'safebrowsing.enabled': True
        }
        options.add_experimental_option('prefs', prefs)
        
        return options
    
    def _get_firefox_options(self) -> FirefoxOptions:
        """Get Firefox browser options."""
        options = FirefoxOptions()
        
        if self.headless:
            options.add_argument('--headless')
            
        # Firefox preferences
        options.set_preference('browser.download.folderList', 2)
        options.set_preference('browser.download.dir', self.download_dir)
        options.set_preference('browser.helperApps.neverAsk.saveToDisk', 
                             'application/octet-stream,text/csv,application/pdf')
        
        if self.user_agent:
            options.set_preference('general.useragent.override', self.user_agent)
            
        return options
    
    def _get_edge_options(self) -> EdgeOptions:
        """Get Edge browser options."""
        options = EdgeOptions()
        
        if self.headless:
            options.add_argument('--headless')
            
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument(f'--window-size={self.window_size}')
        
        if self.user_agent:
            options.add_argument(f'--user-agent={self.user_agent}')
            
        return options
    
    def start_browser(self) -> None:
        """Start the browser instance."""
        try:
            if self.browser_type == 'chrome':
                service = ChromeService(ChromeDriverManager().install())
                options = self._get_chrome_options()
                self.driver = webdriver.Chrome(service=service, options=options)
                
            elif self.browser_type == 'firefox':
                service = FirefoxService(GeckoDriverManager().install())
                options = self._get_firefox_options()
                self.driver = webdriver.Firefox(service=service, options=options)
                
            elif self.browser_type == 'edge':
                service = EdgeService(EdgeChromiumDriverManager().install())
                options = self._get_edge_options()
                self.driver = webdriver.Edge(service=service, options=options)
                
            else:
                raise ValueError(f"Unsupported browser type: {self.browser_type}")
            
            # Set timeouts
            self.driver.implicitly_wait(10)
            self.driver.set_page_load_timeout(self.timeout)
            
            logger.info(f"Browser {self.browser_type} started successfully")
            
        except Exception as e:
            logger.error(f"Failed to start browser: {e}")
            raise
    
    def stop_browser(self) -> None:
        """Stop the browser instance."""
        if self.driver:
            try:
                self.driver.quit()
                logger.info("Browser stopped successfully")
            except Exception as e:
                logger.error(f"Error stopping browser: {e}")
            finally:
                self.driver = None
    
    def ensure_browser(self) -> None:
        """Ensure browser is running."""
        if not self.driver:
            self.start_browser()
    
    def navigate_to_url(self, url: str) -> Dict[str, Any]:
        """Navigate to a specific URL."""
        self.ensure_browser()
        try:
            self.driver.get(url)
            return {
                "success": True,
                "url": self.driver.current_url,
                "title": self.driver.title
            }
        except Exception as e:
            logger.error(f"Navigation failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def find_element(self, selector: str, by_type: str = "css") -> Any:
        """Find element by selector."""
        self.ensure_browser()
        
        by_mapping = {
            "css": By.CSS_SELECTOR,
            "xpath": By.XPATH,
            "id": By.ID,
            "class": By.CLASS_NAME,
            "tag": By.TAG_NAME,
            "name": By.NAME,
            "link_text": By.LINK_TEXT,
            "partial_link_text": By.PARTIAL_LINK_TEXT
        }
        
        by = by_mapping.get(by_type.lower(), By.CSS_SELECTOR)
        return self.driver.find_element(by, selector)
    
    def find_elements(self, selector: str, by_type: str = "css") -> List[Any]:
        """Find multiple elements by selector."""
        self.ensure_browser()
        
        by_mapping = {
            "css": By.CSS_SELECTOR,
            "xpath": By.XPATH,
            "id": By.ID,
            "class": By.CLASS_NAME,
            "tag": By.TAG_NAME,
            "name": By.NAME,
            "link_text": By.LINK_TEXT,
            "partial_link_text": By.PARTIAL_LINK_TEXT
        }
        
        by = by_mapping.get(by_type.lower(), By.CSS_SELECTOR)
        return self.driver.find_elements(by, selector)
    
    def click_element(self, selector: str, by_type: str = "css") -> Dict[str, Any]:
        """Click an element."""
        try:
            element = self.find_element(selector, by_type)
            
            # Scroll to element if needed
            self.driver.execute_script("arguments[0].scrollIntoView(true);", element)
            
            # Wait for element to be clickable
            WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR if by_type == "css" else By.XPATH, selector))
            )
            
            element.click()
            
            return {
                "success": True,
                "message": f"Successfully clicked element: {selector}"
            }
            
        except Exception as e:
            logger.error(f"Click failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def type_text(self, selector: str, text: str, by_type: str = "css", clear_first: bool = True) -> Dict[str, Any]:
        """Type text into an element."""
        try:
            element = self.find_element(selector, by_type)
            
            if clear_first:
                element.clear()
                
            element.send_keys(text)
            
            return {
                "success": True,
                "message": f"Successfully typed text into: {selector}"
            }
            
        except Exception as e:
            logger.error(f"Typing failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_element_text(self, selector: str, by_type: str = "css") -> Dict[str, Any]:
        """Get text content from an element."""
        try:
            element = self.find_element(selector, by_type)
            text = element.text
            
            return {
                "success": True,
                "text": text
            }
            
        except Exception as e:
            logger.error(f"Getting text failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_page_source(self) -> Dict[str, Any]:
        """Get the full HTML source of the current page (dynamically rendered DOM)."""
        self.ensure_browser()
        try:
            # Get the actual rendered DOM using JavaScript instead of raw page_source
            # This captures the HTML after all JavaScript modifications
            source = self.driver.execute_script("return document.documentElement.outerHTML;")
            
            return {
                "success": True,
                "source": source,
                "method": "rendered_dom"  # Indicate this is the rendered DOM
            }
        except Exception as e:
            logger.error(f"Getting rendered DOM failed, falling back to page_source: {e}")
            try:
                # Fallback to original method if JavaScript execution fails
                source = self.driver.page_source
                return {
                    "success": True,
                    "source": source,
                    "method": "page_source_fallback"  # Indicate this is fallback
                }
            except Exception as e2:
                logger.error(f"Getting page source failed: {e2}")
                return {
                    "success": False,
                    "error": str(e2)
                }
    
    def get_rendered_html(self, include_head: bool = True, include_scripts: bool = False) -> Dict[str, Any]:
        """
        Get the rendered HTML with more control over what to include.
        
        Args:
            include_head: Whether to include the <head> section
            include_scripts: Whether to include <script> tags
        
        Returns:
            Dict with success status and the rendered HTML
        """
        self.ensure_browser()
        try:
            if include_head:
                # Get the complete rendered document
                html = self.driver.execute_script("return document.documentElement.outerHTML;")
            else:
                # Get only the body content
                html = self.driver.execute_script("return document.body.outerHTML;")
            
            # Remove scripts if requested
            if not include_scripts and include_head:
                from bs4 import BeautifulSoup
                soup = BeautifulSoup(html, 'html.parser')
                
                # Remove all script tags
                for script in soup.find_all('script'):
                    script.decompose()
                
                html = str(soup)
            
            return {
                "success": True,
                "source": html,
                "method": "rendered_html_custom",
                "options": {
                    "include_head": include_head,
                    "include_scripts": include_scripts
                }
            }
            
        except Exception as e:
            logger.error(f"Getting rendered HTML failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_page_content_comparison(self) -> Dict[str, Any]:
        """
        Get both the raw page source and rendered DOM for comparison.
        Useful for debugging dynamic content issues.
        """
        self.ensure_browser()
        try:
            # Get raw page source (server response)
            raw_source = self.driver.page_source
            
            # Get rendered DOM (after JavaScript)
            rendered_source = self.driver.execute_script("return document.documentElement.outerHTML;")
            
            # Calculate size difference
            raw_size = len(raw_source)
            rendered_size = len(rendered_source)
            size_diff = rendered_size - raw_size
            
            return {
                "success": True,
                "raw_source": raw_source,
                "rendered_source": rendered_source,
                "comparison": {
                    "raw_size": raw_size,
                    "rendered_size": rendered_size,
                    "size_difference": size_diff,
                    "percentage_change": (size_diff / raw_size * 100) if raw_size > 0 else 0
                }
            }
            
        except Exception as e:
            logger.error(f"Getting page content comparison failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def take_screenshot(self, element_selector: str = None, by_type: str = "css") -> Dict[str, Any]:
        """Take a screenshot of the page or specific element."""
        self.ensure_browser()
        try:
            if element_selector:
                # Screenshot of specific element
                element = self.find_element(element_selector, by_type)
                screenshot = element.screenshot_as_png
            else:
                # Full page screenshot
                screenshot = self.driver.get_screenshot_as_png()
            
            # Convert to base64 for easy transmission
            screenshot_b64 = base64.b64encode(screenshot).decode('utf-8')
            
            return {
                "success": True,
                "screenshot": screenshot_b64,
                "format": "png"
            }
            
        except Exception as e:
            logger.error(f"Screenshot failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def execute_javascript(self, script: str, *args) -> Dict[str, Any]:
        """Execute JavaScript code in the browser."""
        self.ensure_browser()
        try:
            result = self.driver.execute_script(script, *args)
            return {
                "success": True,
                "result": result
            }
        except Exception as e:
            logger.error(f"JavaScript execution failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def wait_for_element(self, selector: str, by_type: str = "css", timeout: int = None) -> Dict[str, Any]:
        """Wait for an element to appear."""
        self.ensure_browser()
        
        if timeout is None:
            timeout = self.timeout
            
        try:
            by_mapping = {
                "css": By.CSS_SELECTOR,
                "xpath": By.XPATH,
                "id": By.ID,
                "class": By.CLASS_NAME,
                "tag": By.TAG_NAME,
                "name": By.NAME
            }
            
            by = by_mapping.get(by_type.lower(), By.CSS_SELECTOR)
            
            WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((by, selector))
            )
            
            return {
                "success": True,
                "message": f"Element found: {selector}"
            }
            
        except TimeoutException:
            return {
                "success": False,
                "error": f"Element not found within {timeout} seconds: {selector}"
            }
        except Exception as e:
            logger.error(f"Wait for element failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_cookies(self) -> Dict[str, Any]:
        """Get all cookies from the current domain."""
        self.ensure_browser()
        try:
            cookies = self.driver.get_cookies()
            return {
                "success": True,
                "cookies": cookies
            }
        except Exception as e:
            logger.error(f"Getting cookies failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def set_cookie(self, name: str, value: str, domain: str = None, path: str = "/") -> Dict[str, Any]:
        """Set a cookie."""
        self.ensure_browser()
        try:
            cookie_dict = {
                'name': name,
                'value': value,
                'path': path
            }
            
            if domain:
                cookie_dict['domain'] = domain
                
            self.driver.add_cookie(cookie_dict)
            
            return {
                "success": True,
                "message": f"Cookie '{name}' set successfully"
            }
            
        except Exception as e:
            logger.error(f"Setting cookie failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def scroll_page(self, direction: str = "down", pixels: int = None) -> Dict[str, Any]:
        """Scroll the page."""
        self.ensure_browser()
        try:
            if pixels:
                if direction.lower() == "down":
                    script = f"window.scrollBy(0, {pixels});"
                elif direction.lower() == "up":
                    script = f"window.scrollBy(0, -{pixels});"
                elif direction.lower() == "left":
                    script = f"window.scrollBy(-{pixels}, 0);"
                elif direction.lower() == "right":
                    script = f"window.scrollBy({pixels}, 0);"
                else:
                    return {"success": False, "error": "Invalid direction"}
            else:
                if direction.lower() == "down":
                    script = "window.scrollBy(0, document.body.scrollHeight);"
                elif direction.lower() == "up":
                    script = "window.scrollBy(0, -document.body.scrollHeight);"
                elif direction.lower() == "top":
                    script = "window.scrollTo(0, 0);"
                elif direction.lower() == "bottom":
                    script = "window.scrollTo(0, document.body.scrollHeight);"
                else:
                    return {"success": False, "error": "Invalid direction"}
            
            self.driver.execute_script(script)
            
            return {
                "success": True,
                "message": f"Scrolled {direction}"
            }
            
        except Exception as e:
            logger.error(f"Scrolling failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def extract_links(self) -> Dict[str, Any]:
        """Extract all links from the current page."""
        self.ensure_browser()
        try:
            links = []
            link_elements = self.find_elements("a", "tag")
            
            for link in link_elements:
                href = link.get_attribute("href")
                text = link.text.strip()
                title = link.get_attribute("title")
                
                if href:  # Only include links with href
                    links.append({
                        "url": href,
                        "text": text,
                        "title": title
                    })
            
            return {
                "success": True,
                "links": links,
                "count": len(links)
            }
            
        except Exception as e:
            logger.error(f"Extracting links failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def fill_form(self, form_data: Dict[str, str]) -> Dict[str, Any]:
        """Fill out a form with provided data."""
        self.ensure_browser()
        results = []
        
        for field_selector, value in form_data.items():
            try:
                # Try to find the element
                element = self.find_element(field_selector, "css")
                
                # Handle different input types
                tag_name = element.tag_name.lower()
                input_type = element.get_attribute("type")
                
                if tag_name == "select":
                    # Dropdown selection
                    select = Select(element)
                    select.select_by_visible_text(value)
                elif input_type in ["checkbox", "radio"]:
                    # Checkbox or radio button
                    if str(value).lower() in ["true", "1", "yes", "on"]:
                        if not element.is_selected():
                            element.click()
                elif tag_name == "textarea" or input_type == "text":
                    # Text input
                    element.clear()
                    element.send_keys(value)
                else:
                    # Default: try to send keys
                    element.clear()
                    element.send_keys(value)
                
                results.append({
                    "field": field_selector,
                    "success": True,
                    "message": f"Successfully filled field: {field_selector}"
                })
                
            except Exception as e:
                results.append({
                    "field": field_selector,
                    "success": False,
                    "error": str(e)
                })
        
        success_count = len([r for r in results if r["success"]])
        
        return {
            "success": success_count == len(form_data),
            "results": results,
            "filled_fields": success_count,
            "total_fields": len(form_data)
        }
    
    def get_current_url(self) -> Dict[str, Any]:
        """Get the current page URL."""
        self.ensure_browser()
        try:
            return {
                "success": True,
                "url": self.driver.current_url,
                "title": self.driver.title
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }


# Global browser manager instance
browser_manager = BrowserManager()