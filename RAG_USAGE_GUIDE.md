# 🧠 RAG-Enhanced Browser Automation Guide

Your browser automation MCP server now has **Retrieval Augmented Generation (RAG)** capabilities! This enables persistent learning from web interactions and intelligent action planning based on past experiences.

## 🎯 What RAG Adds

### Before RAG
```
Navigate → Observe DOM → Plan Action → Execute
```

### With RAG
```
Navigate → Observe DOM → Retrieve Similar Pages → Plan with Context → Execute → Store & Learn
```

## 🔧 New RAG Tools

### 1. **store_current_page** - Save Page Interactions
Stores the current page state, task context, and actions taken for future retrieval.

**When to use:**
- After completing a task on a page
- After successful form submission
- When navigating away from an important page

**Example:**
```python
store_current_page(
    task_context="Searched for gaming laptops on Amazon",
    action_history=[
        {"action": "fill", "selector": "#twotabsearchtextbox", "success": True},
        {"action": "click", "selector": ".nav-search-submit", "success": True}
    ]
)
```

### 2. **retrieve_similar_pages** - Find Related Experiences
Retrieves pages where similar tasks were performed, ranked by similarity.

**When to use:**
- Before planning an action on a new page
- When you need proven selector patterns
- To understand common workflows

**Example:**
```python
retrieve_similar_pages(
    task_description="search for electronics products",
    top_k=5,
    domain_filter="amazon.com"  # Optional
)
```

**Returns:**
```json
{
  "similar_pages": [
    {
      "url": "https://amazon.com/s",
      "task_context": "User searched for iPhone 15",
      "similarity_score": 0.87,
      "page_data": {...},
      "action_history": [...]
    }
  ]
}
```

### 3. **get_proven_selectors** - Get What Works
Retrieves CSS selectors that successfully worked for similar tasks, ranked by success rate.

**When to use:**
- Before clicking/filling an element
- When current selectors fail
- To find the most reliable selector

**Example:**
```python
get_proven_selectors(
    element_type="button",
    task_context="submit search query",
    top_k=3
)
```

**Returns:**
```json
{
  "proven_selectors": [
    {
      "selector": "#nav-search-submit-button",
      "frequency": 15,
      "success_count": 14,
      "success_rate": 0.93
    }
  ]
}
```

### 4. **update_action_result** - Track Success/Failure
Updates the knowledge base with action outcomes to improve future recommendations.

**When to use:**
- After every action (click, fill, etc.)
- To build feedback loop
- Track what works and what doesn't

**Example:**
```python
# After a successful click
update_action_result(
    selector="#search-button",
    action="click",
    success=True,
    element_type="button"
)

# After a failed interaction
update_action_result(
    selector=".old-selector",
    action="click",
    success=False,
    element_type="button"
)
```

### 5. **plan_next_action_with_context** - AI-Powered Planning
Combines current page state with learned patterns to recommend the best next action.

**When to use:**
- When unsure which action to take
- For complex multi-step workflows
- To leverage all stored knowledge

**Example:**
```python
plan_next_action_with_context(
    task_description="search for gaming laptops under $1000",
    current_element_type="input"  # Optional
)
```

**Returns:**
```json
{
  "planning_context": {
    "current_page": {"url": "...", "title": "..."},
    "similar_pages": [...],
    "proven_selectors": [...],
    "recommendations": [
      {
        "action": "use_proven_selector",
        "selector": "#twotabsearchtextbox",
        "confidence": 0.95,
        "reasoning": "This selector has 95% success rate in similar contexts"
      }
    ]
  }
}
```

### 6. **get_rag_statistics** - Monitor Learning Progress
Get statistics about stored knowledge.

**Example:**
```python
get_rag_statistics()
```

**Returns:**
```json
{
  "total_chunks": 145,
  "total_pages": 32,
  "domains": {
    "amazon.com": 15,
    "ebay.com": 8,
    "example.com": 9
  },
  "embedding_model": "all-MiniLM-L6-v2",
  "embedding_dimension": 384
}
```

## 📚 Complete Workflow Example

### Scenario: Search Products on E-commerce Site

```python
# 1. Navigate to website
navigate_to_url("https://amazon.com")

# 2. Plan next action with context
planning = plan_next_action_with_context(
    task_description="search for gaming laptops",
    current_element_type="input"
)

# 3. Use recommended selector from RAG
recommended = planning['planning_context']['recommendations'][0]
type_text(
    selector=recommended['selector'],
    text="gaming laptop 16GB RAM"
)

# 4. Update that it worked
update_action_result(
    selector=recommended['selector'],
    action="fill",
    success=True,
    element_type="input"
)

# 5. Get proven button selector for search
button_selectors = get_proven_selectors(
    element_type="button",
    task_context="submit search query"
)

# 6. Click the search button
search_button = button_selectors['proven_selectors'][0]['selector']
click_element(selector=search_button)

# 7. Update the result
update_action_result(
    selector=search_button,
    action="click",
    success=True,
    element_type="button"
)

# 8. Store this successful interaction
store_current_page(
    task_context="Searched for gaming laptops on Amazon",
    action_history=[
        {"action": "fill", "selector": "#twotabsearchtextbox", "success": True, "element_type": "input"},
        {"action": "click", "selector": ".nav-search-submit", "success": True, "element_type": "button"}
    ]
)
```

## 🎓 Best Practices

### 1. **Always Store Successful Workflows**
```python
# After completing a task
store_current_page(
    task_context="Clear description of what was accomplished",
    action_history=[...]
)
```

### 2. **Update Every Action Result**
```python
# Good feedback loop
result = click_element("#submit-btn")
update_action_result(
    selector="#submit-btn",
    action="click",
    success=result.get('success', False),
    element_type="button"
)
```

### 3. **Use Context for Planning**
```python
# Before each major action
planning = plan_next_action_with_context(
    task_description="what you're trying to do",
    current_element_type="button"  # or "input", "link", etc.
)

# Use recommendations
for rec in planning['planning_context']['recommendations']:
    if rec['confidence'] > 0.8:
        # Use this high-confidence selector
        use_selector(rec['selector'])
```

### 4. **Retrieve Before Retrying**
```python
# If an action fails
if not result['success']:
    # Get proven alternatives
    alternatives = get_proven_selectors(
        element_type="button",
        task_context="submit form"
    )
    # Try the next best selector
    for alt in alternatives['proven_selectors']:
        result = click_element(alt['selector'])
        if result['success']:
            break
```

### 5. **Monitor Your Knowledge Base**
```python
# Periodically check stats
stats = get_rag_statistics()
print(f"Learning from {stats['total_pages']} pages across {len(stats['domains'])} domains")
```

## 🔍 How It Works

### Vector Database (ChromaDB)
- Stores page snapshots as semantic embeddings
- Uses cosine similarity for retrieval
- Persistent storage in `./chroma_data/`

### Embedding Model
- **Model**: all-MiniLM-L6-v2
- **Dimensions**: 384
- **Speed**: Fast (good for real-time retrieval)
- **Quality**: Excellent for web content

### Semantic Chunking
Pages are split into meaningful chunks:
1. **Header**: URL, title, task context
2. **Interactive Elements**: Buttons, inputs, links
3. **Forms**: Form fields and structure
4. **Content**: Page sections and text
5. **History**: Actions taken

### Learning Loop
```
Action → Success/Fail → Update Vector DB → Better Recommendations Next Time
```

## 🚀 Advanced Use Cases

### 1. **Multi-Domain Learning**
```python
# Learn from Amazon
navigate_to_url("https://amazon.com")
# ... perform actions ...
store_current_page(task_context="product search on Amazon")

# Apply to eBay
navigate_to_url("https://ebay.com")
similar = retrieve_similar_pages("product search", domain_filter="amazon.com")
# Use patterns from Amazon on eBay
```

### 2. **Form Automation Across Sites**
```python
# Store successful form fill
store_current_page(
    task_context="filled contact form",
    action_history=[
        {"action": "fill", "selector": "#name", "success": True},
        {"action": "fill", "selector": "#email", "success": True}
    ]
)

# On new site, get proven form selectors
selectors = get_proven_selectors("input", "contact form submission")
```

### 3. **Adaptive Navigation**
```python
# Build knowledge of site navigation
pages = retrieve_similar_pages("navigate to product category")

# See common patterns
for page in pages:
    print(page['action_history'])  # See navigation sequences
```

## 📊 Performance Tips

### Optimize Retrieval
- Use `domain_filter` when possible
- Keep `top_k` between 3-5 for speed
- Store only successful interactions

### Manage Storage
- Vector DB grows with usage
- Each page ~1-5 KB
- Monitor with `get_rag_statistics()`

### Improve Accuracy
- Provide detailed `task_context`
- Update action results consistently
- Use specific element types

## 🐛 Troubleshooting

### No Similar Pages Found
```python
stats = get_rag_statistics()
if stats['total_pages'] < 5:
    # Need to build more knowledge first
    print("Learning phase: store more successful interactions")
```

### Low Confidence Recommendations
```python
planning = plan_next_action_with_context(...)
if not planning['planning_context']['recommendations']:
    # Fall back to standard selectors
    click_element("button[type='submit']")
```

### Vector DB Issues
- Database location: `./chroma_data/`
- Reset: Delete `chroma_data` folder to start fresh
- Backup: Copy `chroma_data` folder to preserve knowledge

## 📈 Measuring Success

### Track Improvement Over Time
```python
# Before RAG
success_rate_manual = 0.65  # 65% action success

# After building knowledge (20+ pages)
stats = get_rag_statistics()
if stats['total_pages'] > 20:
    # Use RAG recommendations
    planning = plan_next_action_with_context(...)
    # Success rate should improve to 85-95%
```

### Monitor Metrics
- Pages stored per domain
- Selector success rates
- Retrieval relevance
- Planning confidence scores

## 🎯 Next Steps

1. **Start Small**: Begin with one website
2. **Store Everything**: Capture successful workflows
3. **Build Knowledge**: 10-20 pages per common task
4. **Use Planning**: Let RAG recommend actions
5. **Iterate**: Update results, improve over time

Your MCP server now learns from experience and gets smarter with every interaction! 🚀