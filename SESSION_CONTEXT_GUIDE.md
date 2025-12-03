# Session Context Guide

## Overview

The session-based context system helps you find the right elements on a web page by analyzing its structure and identifying relevant sections based on your task description. Unlike persistent learning systems, this stores information **only for the current session** and clears when you're done.

## How It Works

### 1. **Page Analysis** 
When you analyze a page, the system:
- Extracts all interactive elements (buttons, inputs, links)
- Identifies forms and their fields
- Creates semantic chunks of the page content
- Stores everything in temporary in-memory storage

### 2. **Smart Element Finding**
When you ask for an element, the system:
- Uses semantic search to find relevant page sections
- Ranks elements by confidence based on your task description
- Returns elements with surrounding context (labels, nearby text)
- Helps you identify the right element even without knowing the exact selector

### 3. **Progress Tracking**
As you interact with pages, the system:
- Tracks each action you take
- Records success/failure rates
- Maintains navigation history
- Provides session statistics

## Workflow Example

### Step 1: Navigate and Analyze
```python
# Navigate to a page
navigate_to_url("https://example.com/login")

# Analyze the page for login task
analyze_current_page(
    task_context="User wants to log in to their account"
)
```

**What happens**: The system scans the page and identifies:
- Input fields (username, password)
- Submit button
- "Forgot password" link
- Any forms present

### Step 2: Find Elements with Context
```python
# Find the username input field
get_smart_element_selector(
    element_type="input",
    task_context="enter username",
    top_k=3
)
```

**Response**:
```json
{
  "status": "success",
  "elements": [
    {
      "selector": "#username",
      "label": "Username:",
      "type": "input",
      "confidence": 0.89,
      "surrounding_context": "Username: [input field] Password: [input field]"
    },
    {
      "selector": "#email",
      "label": "Email:",
      "type": "input",
      "confidence": 0.67,
      "surrounding_context": "Email: [input field] for account recovery"
    }
  ]
}
```

**What this tells you**:
- The `#username` field is the most relevant (89% confidence)
- It's labeled "Username:" and is near the password field
- The `#email` field is less relevant (67% confidence) and relates to recovery

### Step 3: Take Action and Track
```python
# Use the suggested selector
type_text(selector="#username", text="john_doe")

# Track that it worked
track_action_result(
    selector="#username",
    action="type",
    success=True,
    element_type="input",
    context="entered username"
)
```

### Step 4: Find Next Element
```python
# Find the password field
get_smart_element_selector(
    element_type="input",
    task_context="enter password",
    top_k=2
)

# Type password
type_text(selector="#password", text="mypassword")
track_action_result(selector="#password", action="type", success=True)
```

### Step 5: Submit Form
```python
# Find submit button
get_smart_element_selector(
    element_type="button",
    task_context="submit login form",
    top_k=3
)

# Click it
click_element(selector="#login-btn")
track_action_result(selector="#login-btn", action="click", success=True)
```

### Step 6: Check Progress
```python
# Get session statistics
get_session_progress()
```

**Response**:
```json
{
  "session_id": "session_20241202_120000",
  "pages_visited": 1,
  "actions_taken": 3,
  "successful_actions": 3,
  "success_rate": 1.0,
  "navigation_history": [
    {
      "url": "https://example.com/login",
      "task": "User wants to log in",
      "actions": [
        {"action": "type", "selector": "#username", "success": true},
        {"action": "type", "selector": "#password", "success": true},
        {"action": "click", "selector": "#login-btn", "success": true}
      ]
    }
  ]
}
```

## Finding Relevant Page Context

Sometimes you want to understand what's on the page before taking action:

```python
# Find sections related to search
find_page_context(
    task_description="search for products",
    element_type="input",
    top_k=3
)
```

**Response**:
```json
{
  "status": "success",
  "relevant_sections": [
    {
      "section_type": "interactive",
      "relevance_score": 0.82,
      "content_preview": "Search Products: [input] [Search Button]",
      "relevant_elements": [
        {"selector": "#search-input", "type": "input", "label": "Search Products"}
      ]
    },
    {
      "section_type": "forms",
      "relevance_score": 0.75,
      "content_preview": "Advanced Search Form: Category [...] Price Range [...]",
      "relevant_elements": [
        {"selector": "#category", "type": "select"},
        {"selector": "#price-min", "type": "input"}
      ]
    }
  ]
}
```

## Use Cases

### 1. **Complex Forms**
When you need to fill a multi-field form:
```python
analyze_current_page(task_context="complete registration form")
get_smart_element_selector(element_type="input", task_context="first name")
get_smart_element_selector(element_type="input", task_context="email address")
get_smart_element_selector(element_type="select", task_context="country selection")
```

### 2. **Dynamic Pages**
When element IDs/classes change frequently:
```python
# Instead of hardcoding selectors, use context
get_smart_element_selector(
    element_type="button",
    task_context="add item to shopping cart"
)
# Returns the most relevant "Add to Cart" button based on context
```

### 3. **Ambiguous Pages**
When multiple similar elements exist:
```python
# Find the correct search button among many
get_smart_element_selector(
    element_type="button",
    task_context="search products in main navigation"
)
# Uses surrounding context to identify the right one
```

### 4. **Progress Monitoring**
Track your automation workflow:
```python
# After each major step
track_action_result(...)
get_session_progress()  # Check if everything is working
```

## Session Lifecycle

### Start of Session
- Session ID is automatically created
- In-memory storage is initialized
- No data from previous sessions

### During Session
- Pages are analyzed as you navigate
- Actions are tracked
- Context builds up for better suggestions

### End of Session
```python
# Manually clear if needed
clear_session_context()
```

Or just stop - memory is automatically cleared when the process ends.

## Key Differences from Persistent RAG

| Feature | Session Context | Persistent RAG |
|---------|----------------|----------------|
| Storage | In-memory only | Disk-based database |
| Lifetime | Current session | Across sessions |
| Purpose | Find elements on current pages | Learn from history |
| Use case | Smart element selection | Pattern learning |
| Memory | Cleared when done | Persists forever |

## Best Practices

### 1. **Analyze Early**
Call `analyze_current_page()` right after navigating:
```python
navigate_to_url("https://example.com")
analyze_current_page(task_context="browse products")
```

### 2. **Be Specific with Task Context**
Better:
```python
task_context="enter email address for login"
```

Less effective:
```python
task_context="fill form"
```

### 3. **Use Element Type Filters**
Narrow down results:
```python
get_smart_element_selector(
    element_type="button",  # Not just any element
    task_context="submit search query"
)
```

### 4. **Track Important Actions**
Track actions that matter for debugging:
```python
track_action_result(
    selector="#submit",
    action="click",
    success=True,
    context="submitted checkout form with 3 items"
)
```

### 5. **Check Progress Regularly**
Monitor success rates:
```python
progress = get_session_progress()
if progress['success_rate'] < 0.8:
    # Something might be wrong
    print("Low success rate detected!")
```

## Troubleshooting

### Element Not Found
If `get_smart_element_selector()` doesn't find what you need:

1. **Re-analyze the page**: Maybe it changed
   ```python
   analyze_current_page(task_context="updated task")
   ```

2. **Adjust your task description**: Be more specific
   ```python
   # Instead of "submit"
   task_context="submit payment form in checkout"
   ```

3. **Increase top_k**: Get more suggestions
   ```python
   get_smart_element_selector(..., top_k=10)
   ```

### Low Confidence Scores
If all elements have low confidence:
- Your task description might not match page content
- Try finding page context first: `find_page_context()`
- Verify the page actually has the elements you're looking for

### Session Memory Issues
If you want to start fresh:
```python
clear_session_context()
# Then re-analyze current page
analyze_current_page(task_context="new task")
```

## Summary

The session context system helps you:
- ✅ Find elements without knowing exact selectors
- ✅ Understand page structure semantically
- ✅ Get confidence scores for element selection
- ✅ Track your automation progress
- ✅ Work with dynamic/changing pages

It does NOT:
- ❌ Store data across sessions
- ❌ Learn from past experiences
- ❌ Persist to disk
- ❌ Share data between different automation runs
