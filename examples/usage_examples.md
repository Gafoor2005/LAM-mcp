# Basic Usage Examples for Browser MCP Server

This file contains practical examples of how to use the browser automation tools.

## Example 1: Web Scraping

### Navigate and Extract Data

```
User: "Navigate to example.com and extract all the links on the page"

MCP Response: 
1. Uses navigate_to_url tool with "https://example.com"
2. Uses extract_links tool to get all links
3. Returns structured data with link text and URLs
```

### Screenshot Capture

```
User: "Take a screenshot of the current page and save it"

MCP Response:
1. Uses take_screenshot tool
2. Returns path to saved screenshot file
3. Image is saved in configured screenshot directory
```

## Example 2: Form Automation

### Login Flow

```
User: "Go to login page, enter username 'testuser' and password 'testpass', then click submit"

MCP Response:
1. Uses navigate_to_url for login page
2. Uses type_text to fill username field: selector="input[name='username']", text="testuser"
3. Uses type_text to fill password field: selector="input[name='password']", text="testpass" 
4. Uses click_element to submit: selector="button[type='submit']"
```

### Multi-Step Form

```
User: "Fill out the contact form with name 'John Doe', email 'john@example.com', and message 'Hello World'"

MCP Response:
1. Uses fill_form tool with form data:
   - selector: "form.contact-form"
   - form_data: {
       "name": "John Doe",
       "email": "john@example.com", 
       "message": "Hello World"
     }
2. Optionally uses click_element to submit
```

## Example 3: JavaScript Execution

### Dynamic Content Interaction

```
User: "Execute JavaScript to scroll to bottom of page and click the 'Load More' button"

MCP Response:
1. Uses execute_javascript: "window.scrollTo(0, document.body.scrollHeight)"
2. Uses wait_for_element: selector="button.load-more", timeout=10
3. Uses click_element: selector="button.load-more"
```

### Data Extraction with JavaScript

```
User: "Get the text content of all product titles on this e-commerce page"

MCP Response:
1. Uses execute_javascript with code:
   "return Array.from(document.querySelectorAll('.product-title')).map(el => el.textContent)"
2. Returns array of product titles
```

## Example 4: Page Analysis

### Content Search

```
User: "Find all elements containing the word 'pricing' and extract their text"

MCP Response:
1. Uses extract_text with selector matching elements containing 'pricing'
2. Returns structured data with element text and locations
```

### Page Structure Analysis

```
User: "Get the page source and analyze the form structure"

MCP Response:
1. Uses get_page_source to retrieve full HTML
2. Parses and identifies form elements, inputs, and structure
3. Provides summary of form fields and requirements
```

## Example 5: Multi-Page Workflows

### Site Navigation

```
User: "Navigate through the site menu: Home -> Products -> Category A -> View first product"

MCP Response:
1. Uses navigate_to_url for home page
2. Uses click_element for "Products" menu item
3. Uses click_element for "Category A" link
4. Uses click_element for first product (e.g., "div.product-grid .product-item:first-child")
5. Uses take_screenshot to capture final product page
```

### Data Collection Workflow

```
User: "Go through pagination and collect all product names from pages 1-3"

MCP Response:
1. Uses extract_text to get product names from current page
2. Uses click_element to go to next page (e.g., "a.next-page")
3. Repeats extraction and navigation for specified pages
4. Returns consolidated list of all product names
```

## Example 6: Cookie and Session Management

### Login and Session Maintenance

```
User: "Login to the site and then navigate to protected dashboard area"

MCP Response:
1. Uses navigate_to_url for login page
2. Uses fill_form for login credentials
3. Uses get_cookies to capture session cookies
4. Uses navigate_to_url for dashboard (session maintained)
5. Confirms access by checking page content
```

## Example 7: Error Handling and Retries

### Robust Element Interaction

```
User: "Click the submit button, but wait for it to become clickable first"

MCP Response:
1. Uses wait_for_element with selector="button[type='submit']" and timeout=15
2. Uses click_element once element is ready
3. Handles any timeout or element not found errors gracefully
```

## Example 8: Advanced Automation

### File Upload Simulation

```
User: "Simulate uploading a file to the file input field"

MCP Response:
1. Uses type_text with file input selector and file path
2. Note: Actual file must exist on system running the browser
```

### Modal Dialog Handling

```
User: "Handle the confirmation dialog that appears after clicking delete"

MCP Response:
1. Uses click_element for delete button
2. Uses execute_javascript to handle alert: "window.confirm = function() { return true; }"
3. Waits for page update or navigation
```

## Best Practices

### Timing and Waits

- Always use `wait_for_element` before interacting with dynamically loaded content
- Set appropriate timeouts based on page loading expectations
- Use `scroll_page` to ensure elements are in viewport before clicking

### Selector Strategy

- Prefer specific selectors (IDs, data attributes) over generic ones
- Use CSS selectors or XPath based on page structure
- Test selectors in browser dev tools first

### Error Recovery

- Handle element not found gracefully
- Retry logic for transient failures
- Take screenshots when errors occur for debugging

### Performance

- Use headless mode for faster execution
- Minimize unnecessary page loads
- Batch operations when possible

## Testing Your Automation

1. Start with simple navigation tests
2. Test individual tools before complex workflows
3. Use non-headless mode for debugging
4. Verify screenshots and extracted data
5. Test error conditions and edge cases