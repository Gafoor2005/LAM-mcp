# Session Context Quick Reference

## 🚀 Quick Start

```python
# 1. Navigate to page
navigate_to_url("https://example.com/login")

# 2. Analyze page structure
analyze_current_page(task_context="login to account")

# 3. Find elements by description
result = get_smart_element_selector(
    element_type="input",
    task_context="enter username"
)

# 4. Use the suggested selector
selector = result['elements'][0]['selector']
type_text(selector, "my_username")

# 5. Track your action
track_action_result(selector=selector, action="type", success=True)
```

## 📋 Core Tools

### analyze_current_page
Analyze and store page context
```python
analyze_current_page(
    task_context="what user is trying to do"
)
```

### get_smart_element_selector  
Find elements with context and confidence scores
```python
get_smart_element_selector(
    element_type="button",  # or "input", "link", "select"
    task_context="submit login form",
    top_k=5  # number of suggestions
)
```

### find_page_context
Search for relevant page sections
```python
find_page_context(
    task_description="fill out registration form",
    element_type="input",  # optional filter
    top_k=5
)
```

### track_action_result
Record actions for progress monitoring
```python
track_action_result(
    selector="#username",
    action="type",  # or "click", "select", etc.
    success=True,
    context="entered username 'john_doe'"  # optional
)
```

### get_session_progress
View session statistics
```python
get_session_progress()
# Returns: pages visited, actions taken, success rate, history
```

### clear_session_context
Start fresh
```python
clear_session_context()
```

## 💡 Common Patterns

### Login Flow
```python
navigate_to_url("https://site.com/login")
analyze_current_page(task_context="user login")

# Username
user = get_smart_element_selector(element_type="input", task_context="username")['elements'][0]
type_text(user['selector'], "john")
track_action_result(user['selector'], "type", True)

# Password
pwd = get_smart_element_selector(element_type="input", task_context="password")['elements'][0]
type_text(pwd['selector'], "secret")
track_action_result(pwd['selector'], "type", True)

# Submit
btn = get_smart_element_selector(element_type="button", task_context="login")['elements'][0]
click_element(btn['selector'])
track_action_result(btn['selector'], "click", True)
```

### Form Filling
```python
navigate_to_url("https://site.com/register")
analyze_current_page(task_context="registration")

fields = [
    ("input", "first name", "John"),
    ("input", "last name", "Doe"),
    ("input", "email address", "john@example.com"),
    ("select", "country", "United States")
]

for elem_type, task, value in fields:
    result = get_smart_element_selector(elem_type, task)['elements'][0]
    if elem_type == "select":
        select_dropdown_option(result['selector'], option_text=value)
    else:
        type_text(result['selector'], value)
    track_action_result(result['selector'], elem_type, True)
```

### Product Search & Add to Cart
```python
# Search page
navigate_to_url("https://shop.com")
analyze_current_page(task_context="search for products")

search = get_smart_element_selector("input", "product search")['elements'][0]
type_text(search['selector'], "laptop")

search_btn = get_smart_element_selector("button", "submit search")['elements'][0]
click_element(search_btn['selector'])

# Results page
analyze_current_page(task_context="add specific laptop to cart")

# Find the right "Add to Cart" button
cart_btn = get_smart_element_selector(
    "button", 
    "add gaming laptop pro to cart"
)['elements'][0]

print(f"Confidence: {cart_btn['confidence']:.0%}")
print(f"Context: {cart_btn['context']}")

click_element(cart_btn['selector'])
track_action_result(cart_btn['selector'], "click", True)
```

## 🎯 Best Practices

### ✅ DO
- Analyze page after navigation
- Be specific in task descriptions
- Use element type filters
- Check confidence scores before using
- Track important actions
- Review context when confidence is low
- Use top_k to see multiple options

### ❌ DON'T
- Use without analyzing page first
- Use vague task descriptions like "click button"
- Ignore confidence scores
- Forget to filter by element type
- Track every single action (only important ones)
- Assume first result is always right

## 🔍 Debugging

### Low Confidence?
```python
# Get more options
result = get_smart_element_selector(
    element_type="button",
    task_context="your task here",
    top_k=10  # See more suggestions
)

# Review all options
for i, elem in enumerate(result['elements'], 1):
    print(f"{i}. {elem['selector']}")
    print(f"   Confidence: {elem['confidence']:.0%}")
    print(f"   Label: {elem['label']}")
    print(f"   Context: {elem['context'][:100]}...")
```

### Element Not Found?
```python
# 1. Re-analyze page
analyze_current_page(task_context="updated task description")

# 2. Search page context first
context = find_page_context(
    task_description="what you're looking for",
    element_type="button"
)

# 3. Review what's on the page
for section in context['relevant_sections']:
    print(f"Section: {section['section_type']}")
    print(f"Relevance: {section['relevance_score']:.0%}")
    print(f"Preview: {section['content_preview']}")
```

### Check Session Progress
```python
progress = get_session_progress()
print(f"Success rate: {progress['success_rate']:.0%}")

# If low success rate
if progress['success_rate'] < 0.8:
    print("Recent actions:")
    for nav in progress['navigation_history'][-3:]:
        print(f"  Page: {nav['url']}")
        for action in nav.get('actions', []):
            print(f"    {action['action']} - {'✅' if action['success'] else '❌'}")
```

## 📊 Response Format

### get_smart_element_selector Response
```json
{
  "status": "success",
  "element_type": "input",
  "elements": [
    {
      "selector": "#username",
      "label": "Username",
      "type": "input",
      "confidence": 0.89,
      "surrounding_context": "Username: [input] Password: [input]"
    }
  ],
  "total_found": 2,
  "task_context": "enter username"
}
```

### get_session_progress Response
```json
{
  "session_id": "session_20241202_120000",
  "pages_visited": 3,
  "actions_taken": 8,
  "successful_actions": 7,
  "success_rate": 0.875,
  "navigation_history": [
    {
      "url": "https://example.com/login",
      "task": "user login",
      "timestamp": "2024-12-02T12:00:00",
      "actions": [
        {"action": "type", "selector": "#username", "success": true}
      ]
    }
  ]
}
```

## ⏱️ Typical Performance

- Page analysis: 200-500ms
- Element search: 50-150ms
- Context retrieval: 100-200ms
- Session clearing: <10ms

## 📝 Notes

- Session data is **ephemeral** (in-memory only)
- Automatically cleared when process ends
- No persistent storage or learning across sessions
- Designed for single-session automation workflows
- Memory usage scales with pages visited
- Recommend clearing session after 50+ pages

## 🔗 See Also

- `SESSION_CONTEXT_GUIDE.md` - Detailed usage guide
- `SESSION_CONTEXT_SUMMARY.md` - Technical summary
- `BEFORE_AFTER_COMPARISON.md` - Comparison with traditional approach
- `README.md` - Full documentation
