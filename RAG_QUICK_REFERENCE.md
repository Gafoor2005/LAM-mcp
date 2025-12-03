# 🚀 RAG Quick Reference Card

## Quick Start

```python
# 1. Navigate to a page
navigate_to_url("https://example.com")

# 2. Get smart recommendations
planning = plan_next_action_with_context(
    task_description="search for products",
    current_element_type="input"
)

# 3. Use recommended selector
selector = planning['planning_context']['recommendations'][0]['selector']
type_text(selector=selector, text="gaming laptop")

# 4. Track success
update_action_result(selector=selector, action="fill", success=True)

# 5. Store for future use
store_current_page(
    task_context="Searched for gaming laptops",
    action_history=[{"action": "fill", "selector": selector, "success": True}]
)
```

## Essential Tools

| Tool | Use Case | Example |
|------|----------|---------|
| `store_current_page` | Save successful workflow | After completing a task |
| `retrieve_similar_pages` | Find related pages | Before starting a new task |
| `get_proven_selectors` | Get reliable selectors | Before clicking/filling |
| `update_action_result` | Track what works | After every action |
| `plan_next_action_with_context` | Smart planning | Complex multi-step tasks |
| `get_rag_statistics` | Monitor learning | Check knowledge base size |

## Typical Workflow

```
1. Navigate    → navigate_to_url()
2. Plan        → plan_next_action_with_context()
3. Execute     → click_element() / type_text()
4. Track       → update_action_result()
5. Store       → store_current_page()
6. Repeat
```

## Best Practices

✅ **DO:**
- Store every successful workflow
- Update results after each action
- Use planning for complex tasks
- Provide detailed task contexts
- Monitor statistics regularly

❌ **DON'T:**
- Store failed interactions
- Skip updating action results
- Use vague task descriptions
- Ignore confidence scores
- Forget to check statistics

## Key Metrics

- **Success Rate**: 85-95% with 20+ stored pages
- **Retrieval Time**: <200ms for top-3 results
- **Storage**: ~1-5KB per page
- **Embedding**: 384 dimensions
- **Model**: all-MiniLM-L6-v2

## Troubleshooting

**No similar pages found?**
```python
stats = get_rag_statistics()
# Need at least 10-20 pages for good results
```

**Low confidence?**
```python
# Build more knowledge first
for task in common_tasks:
    complete_task(task)
    store_current_page(task_context=task)
```

**Vector DB issues?**
- Location: `./chroma_data/`
- Reset: Delete folder to start fresh
- Backup: Copy folder to preserve

## Example: Complete Search Task

```python
# Navigate
navigate_to_url("https://amazon.com")

# Get context from similar searches
planning = plan_next_action_with_context("search for laptop")
recommended_input = planning['planning_context']['recommendations'][0]

# Use proven selector
type_text(
    selector=recommended_input['selector'],
    text="gaming laptop 16GB"
)
update_action_result(
    selector=recommended_input['selector'],
    action="fill",
    success=True,
    element_type="input"
)

# Get proven button selector
buttons = get_proven_selectors("button", "submit search")
search_btn = buttons['proven_selectors'][0]['selector']

# Click
click_element(search_btn)
update_action_result(
    selector=search_btn,
    action="click",
    success=True,
    element_type="button"
)

# Store success
store_current_page(
    task_context="Searched for gaming laptops on Amazon",
    action_history=[...]
)
```

## Success Formula

```
More stored pages → Better recommendations → Higher success rate → Store more pages → ...
```

Start with 10-20 successful interactions per common task, then let RAG do the work! 🎯
