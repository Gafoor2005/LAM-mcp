# RAG Integration for Web Automation MCP (LAM)

## Overview

This document outlines integrating Retrieval Augmented Generation (RAG) into your existing Large Action Model (LAM) MCP for enhanced web automation capabilities.

**Current State:** Your LAM observes DOM and performs actions (click, fill, etc.)

**Goal:** Add persistent web data storage and intelligent retrieval for context-aware task planning and proven action patterns.

---

## 1. Architecture Overview

### Current LAM MCP Structure
```
observe_dom() → get current page state
click() → click elements  
fill_input() → fill forms
take_action() → execute actions
```

### With RAG Layer Added
```
┌─────────────────────────────────────────────┐
│         Web Automation Task                 │
└──────────────┬──────────────────────────────┘
               │
        ┌──────▼──────┐
        │  Current    │
        │   DOM       │
        └──────┬──────┘
               │
        ┌──────▼─────────────────────────┐
        │  RAG Retrieval Layer           │
        │  ├─ Retrieve Similar Pages     │
        │  ├─ Get Proven Selectors       │
        │  ├─ Extract Common Patterns    │
        │  └─ Build Planning Context     │
        └──────┬──────────────────────────┘
               │
        ┌──────▼──────────────────────────┐
        │  Enhanced Action Planner        │
        │  (uses retrieval context)       │
        └──────┬──────────────────────────┘
               │
        ┌──────▼──────┐
        │   Execute   │
        │   Action    │
        └──────┬──────┘
               │
        ┌──────▼──────────────────────────┐
        │  Store Results & Update Vector  │
        │  DB (Feedback Loop)             │
        └─────────────────────────────────┘
```

### Vector Store Structure
```
Vector Database (Chroma/Milvus)
├── Collection: web_automation_pages
│   ├── Document: Page Snapshot + Embeddings
│   ├── Metadata: url, task_context, domain, depth
│   ├── Timestamp: when visited
│   └── Interactive Elements: selectors, types, labels
└── Indexing: Cosine similarity search
```

---

## 2. Data Model

### Page Snapshot Schema

Store the following for each page visited:

```json
{
  "id": "page_snapshot_uuid",
  "page_url": "https://example.com/search",
  "timestamp": "2025-12-02T14:45:00Z",
  "task_context": "user searched for 'laptop with 16GB RAM'",
  
  "page_data": {
    "title": "Search Results - Example.com",
    "semantic_summary": "Page contains search results with product listings, filters, and pagination",
    
    "interactive_elements": [
      {
        "selector": ".search-input",
        "type": "text_input",
        "label": "Search Box",
        "attributes": {"placeholder": "Search products..."},
        "successfully_interacted": true
      },
      {
        "selector": ".search-btn",
        "type": "button",
        "label": "Search Button",
        "successfully_interacted": true
      },
      {
        "selector": ".filter-ram",
        "type": "checkbox",
        "label": "Filter by RAM",
        "options": ["8GB", "16GB", "32GB"]
      }
    ],
    
    "forms": [
      {
        "id": "search_form",
        "fields": ["search_input", "filters"],
        "action": "POST /search"
      }
    ],
    
    "navigation": ["home", "products", "deals", "about", "contact"],
    
    "content_sections": [
      {
        "section_type": "product_listing",
        "selector": ".product-item",
        "count": 20
      }
    ]
  },
  
  "action_history": [
    {
      "action": "fill_input",
      "selector": ".search-input",
      "value": "laptop",
      "success": true
    },
    {
      "action": "click",
      "selector": ".search-btn",
      "success": true
    }
  ],
  
  "vector_embedding": [0.234, 0.456, ...],  // 384-dim or higher
  
  "metadata": {
    "domain": "example.com",
    "page_depth": 1,
    "response_time_ms": 1200,
    "session_id": "session_12345"
  }
}
```

---

## 3. Implementation Components

### 3.1 Vector Database Setup

#### Option A: Chroma (Recommended for prototyping)
- **Pros:** Local, no server setup, persistent storage, simple API
- **Cons:** Not distributed, single-machine only
- **Use Case:** Development, testing, single-instance deployment

```python
from chromadb.config import Settings
import chromadb

client = chromadb.Client(Settings(
    chroma_db_impl="duckdb+parquet",
    persist_directory="./chroma_data",
    anonymized_telemetry=False
))

collection = client.get_or_create_collection(
    name="web_automation_pages",
    metadata={"hnsw:space": "cosine"}  # Cosine distance
)
```

#### Option B: Milvus (Recommended for production)
- **Pros:** Distributed, scalable, supports large-scale retrieval
- **Cons:** Requires server setup, more complex
- **Use Case:** Production deployment, high-volume page storage

```python
from pymilvus import Collection, FieldSchema, CollectionSchema, connections, DataType

# Connection
connections.connect("default", host="localhost", port="19530")

# Schema definition
fields = [
    FieldSchema(name="id", dtype=DataType.VARCHAR, is_primary=True, max_length=100),
    FieldSchema(name="url", dtype=DataType.VARCHAR, max_length=500),
    FieldSchema(name="task_context", dtype=DataType.VARCHAR, max_length=1000),
    FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=384),
    FieldSchema(name="metadata", dtype=DataType.JSON)
]

schema = CollectionSchema(fields, description="Web automation pages")
collection = Collection("web_pages", schema)

# Create index
collection.create_index(field_name="embedding", index_params={"index_type": "IVF_FLAT", "metric_type": "L2"})
```

#### Option C: Pinecone (Recommended for managed service)
- **Pros:** Fully managed, serverless, no infrastructure
- **Cons:** Cloud-dependent, API costs
- **Use Case:** Quick production deployment, minimal DevOps

```python
import pinecone

pinecone.init(api_key="your-api-key", environment="us-west1-gcp")
index = pinecone.Index("lam-web-automation")

# Upsert vectors
index.upsert(vectors=[
    (id, embedding_vector, {"url": url, "task": task})
    for id, embedding_vector, url, task in batch
])
```

### 3.2 Embedding Model

Use `sentence-transformers` for semantic embeddings of web content:

```python
from sentence_transformers import SentenceTransformer

# Model choices (sorted by speed vs quality)
# "all-MiniLM-L6-v2"      - 384 dims, fastest, good for web content (RECOMMENDED)
# "all-mpnet-base-v2"     - 768 dims, better quality
# "multi-qa-MiniLM-L6"    - 384 dims, tuned for Q&A, good for retrieval

embedding_model = SentenceTransformer('all-MiniLM-L6-v2')

# Generate embedding for page summary
page_summary = "Search page with results for laptop queries, includes filters and pagination"
embedding = embedding_model.encode(page_summary, convert_to_numpy=True)
```

### 3.3 Document Chunking Strategy

For web content, use semantic chunking instead of fixed-size:

```python
def semantic_chunk_page_snapshot(page_snapshot: dict, chunk_size: int = 200) -> list:
    """
    Split page snapshot into semantic chunks.
    Preserves meaning by grouping related elements.
    """
    chunks = []
    
    # Chunk 1: Page header + navigation
    header_chunk = f"""
    Page: {page_snapshot['page_data']['title']}
    URL: {page_snapshot['page_url']}
    Navigation: {', '.join(page_snapshot['page_data']['navigation'])}
    """
    chunks.append(header_chunk)
    
    # Chunk 2: Interactive elements (grouped by type)
    interactive_chunk = "Interactive Elements: "
    for elem in page_snapshot['page_data']['interactive_elements']:
        interactive_chunk += f"\n- {elem['label']} ({elem['type']}): {elem['selector']}"
    chunks.append(interactive_chunk)
    
    # Chunk 3: Forms
    forms_chunk = "Forms: "
    for form in page_snapshot['page_data']['forms']:
        forms_chunk += f"\n- {form['id']}: Fields {form['fields']}"
    chunks.append(forms_chunk)
    
    # Chunk 4: Content sections
    content_chunk = "Content: "
    for section in page_snapshot['page_data']['content_sections']:
        content_chunk += f"\n- {section['section_type']} (count: {section['count']})"
    chunks.append(content_chunk)
    
    # Chunk 5: Task context + action history
    history_chunk = f"""
    Task: {page_snapshot['task_context']}
    Actions Taken: {len(page_snapshot['action_history'])} successful interactions
    """
    chunks.append(history_chunk)
    
    return [c.strip() for c in chunks if c.strip()]
```

### 3.4 MCP Tools for RAG

Add these tools to your MCP server:

```python
from mcp.server import Server
from mcp.types import Tool, TextContent

app = Server("lam-with-rag")

# ============================================
# TOOL 1: Store Current Page
# ============================================
@app.call_tool()
async def store_current_page(
    dom_content: str,
    current_url: str,
    task_context: str,
    action_history: list = None
) -> dict:
    """
    Store current page snapshot in vector DB for future retrieval.
    
    Args:
        dom_content: Full DOM HTML of current page
        current_url: URL of the page
        task_context: Description of what we're trying to achieve
        action_history: List of actions taken on this page
    
    Returns:
        {"status": "stored", "chunks": N, "embedding_dim": 384}
    """
    try:
        # 1. Extract semantic page data
        page_summary = await extract_page_semantics(dom_content, current_url)
        
        # 2. Build snapshot document
        snapshot = {
            "page_url": current_url,
            "timestamp": datetime.now().isoformat(),
            "task_context": task_context,
            "page_data": page_summary,
            "action_history": action_history or [],
            "metadata": {
                "domain": extract_domain(current_url),
                "session_id": get_current_session_id()
            }
        }
        
        # 3. Chunk and embed
        chunks = semantic_chunk_page_snapshot(snapshot)
        embeddings = embedding_model.encode(chunks, convert_to_numpy=True)
        
        # 4. Store in vector DB
        for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
            vector_db.add({
                "id": f"{current_url}_{int(time.time())}_{i}",
                "content": chunk,
                "embedding": embedding.tolist(),
                "full_snapshot": snapshot,
                "metadata": snapshot["metadata"]
            })
        
        return {
            "status": "stored",
            "chunks": len(chunks),
            "embedding_dim": len(embeddings[0])
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}


# ============================================
# TOOL 2: Retrieve Similar Pages
# ============================================
@app.call_tool()
async def retrieve_similar_pages(
    task_description: str,
    top_k: int = 3,
    domain_filter: str = None
) -> dict:
    """
    Find similar pages from vector DB for context-aware planning.
    
    Args:
        task_description: Description of what we're trying to do
        top_k: Number of similar pages to retrieve
        domain_filter: Optional - filter by domain (e.g., "amazon.com")
    
    Returns:
        {"similar_pages": [...], "retrieved_count": N}
    """
    try:
        # 1. Embed query
        query_embedding = embedding_model.encode(
            task_description, 
            convert_to_numpy=True
        )
        
        # 2. Search vector DB
        filters = {}
        if domain_filter:
            filters["metadata.domain"] = domain_filter
        
        results = vector_db.search(
            query_embedding=query_embedding.tolist(),
            top_k=top_k,
            filters=filters
        )
        
        # 3. Format results
        similar_pages = []
        for result in results:
            similar_pages.append({
                "url": result["metadata"]["url"],
                "task_context": result["full_snapshot"]["task_context"],
                "page_title": result["full_snapshot"]["page_data"]["title"],
                "interactive_elements": result["full_snapshot"]["page_data"]["interactive_elements"],
                "similarity_score": result["score"]
            })
        
        return {
            "similar_pages": similar_pages,
            "retrieved_count": len(similar_pages)
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}


# ============================================
# TOOL 3: Get Proven Selectors
# ============================================
@app.call_tool()
async def get_proven_selectors(
    element_type: str,
    task_context: str,
    top_k: int = 5
) -> dict:
    """
    Retrieve CSS selectors that have worked for similar tasks.
    
    Args:
        element_type: Type of element ("button", "input", "link", etc.)
        task_context: Description of the task
        top_k: Number of proven selectors to return
    
    Returns:
        {"proven_selectors": [...], "success_rate": float}
    """
    try:
        # 1. Search for pages with similar task context
        query = f"Find {element_type} elements for task: {task_context}"
        query_embedding = embedding_model.encode(query, convert_to_numpy=True)
        
        results = vector_db.search(
            query_embedding=query_embedding.tolist(),
            top_k=top_k
        )
        
        # 2. Extract and rank proven selectors
        proven_selectors = {}
        for result in results:
            page_data = result["full_snapshot"]["page_data"]
            for elem in page_data["interactive_elements"]:
                if elem["type"] == element_type and elem.get("successfully_interacted"):
                    selector = elem["selector"]
                    proven_selectors[selector] = proven_selectors.get(selector, 0) + 1
        
        # 3. Sort by frequency (proven to work)
        ranked = sorted(
            proven_selectors.items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        return {
            "proven_selectors": [sel for sel, count in ranked],
            "frequency": dict(ranked),
            "success_rate": len(ranked) / max(len(proven_selectors), 1)
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}


# ============================================
# TOOL 4: Plan Next Action with Retrieval
# ============================================
@app.call_tool()
async def plan_next_action_with_rag(
    task_description: str,
    current_dom: str,
    current_url: str
) -> dict:
    """
    Generate next action using retrieval context from similar pages.
    More informed planning = higher success rate.
    
    Args:
        task_description: What we're trying to accomplish
        current_dom: Current page DOM
        current_url: Current page URL
    
    Returns:
        {"action": "click|fill|scroll|...", "selector": "...", "confidence": 0.95}
    """
    try:
        # 1. Retrieve similar pages
        retrieval = await retrieve_similar_pages(task_description, top_k=3)
        similar_pages = retrieval["similar_pages"]
        
        # 2. Extract proven patterns
        proven_selectors_result = await get_proven_selectors("button", task_description, top_k=5)
        
        # 3. Build retrieval context
        retrieval_context = {
            "similar_pages_count": len(similar_pages),
            "similar_pages": similar_pages,
            "proven_selectors": proven_selectors_result["proven_selectors"],
            "common_element_types": extract_common_elements(similar_pages)
        }
        
        # 4. Call LLM with context (see Section 5 for prompt)
        planning_prompt = build_planning_prompt(
            task=task_description,
            current_dom=current_dom,
            current_url=current_url,
            retrieval_context=retrieval_context
        )
        
        # 5. Get action from LLM
        next_action = await llm_client.generate(planning_prompt)
        
        return {
            "action": next_action["action"],
            "selector": next_action.get("selector"),
            "value": next_action.get("value"),
            "reasoning": next_action.get("reasoning"),
            "confidence": next_action.get("confidence", 0.8),
            "context_used": {
                "similar_pages_retrieved": len(similar_pages),
                "proven_selectors_available": len(proven_selectors_result["proven_selectors"])
            }
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}


# ============================================
# TOOL 5: Update Page Annotations
# ============================================
@app.call_tool()
async def update_page_annotations(
    page_url: str,
    element_selector: str,
    action_result: dict
) -> dict:
    """
    Update page data based on action results (feedback loop).
    Build knowledge base of what works.
    
    Args:
        page_url: URL of the page
        element_selector: CSS selector of element
        action_result: {"success": bool, "error": str, "new_state": {...}}
    
    Returns:
        {"status": "updated", "annotation_count": N}
    """
    try:
        success = action_result.get("success", False)
        
        # Update vector DB records for this page
        vector_db.update_annotations(
            filters={"metadata.url": page_url},
            updates={
                "element_interactions": {
                    element_selector: {
                        "success": success,
                        "timestamp": datetime.now().isoformat()
                    }
                }
            }
        )
        
        return {"status": "updated", "element": element_selector, "success": success}
    except Exception as e:
        return {"status": "error", "message": str(e)}
```

---

## 4. Integration with Existing LAM

### Modify Your Current Workflow

**Before (Current):**
```
observe_dom() 
  → parse current state
  → plan next action (no context)
  → execute action
```

**After (With RAG):**
```
observe_dom()
  → parse current state
  → RETRIEVE similar pages (NEW)
  → plan next action WITH retrieval context (ENHANCED)
  → execute action
  → store page snapshot (NEW)
  → update annotations (NEW)
```

### Code Integration Points

```python
class LAMWithRAG:
    def __init__(self, vector_db, embedding_model, llm_client):
        self.vector_db = vector_db
        self.embedding_model = embedding_model
        self.llm = llm_client
    
    async def execute_task(self, task_description: str):
        session_id = generate_session_id()
        
        while not task_complete:
            # Step 1: Observe current state
            dom = await self.browser.get_dom()
            url = await self.browser.get_url()
            
            # Step 2: RETRIEVE CONTEXT (NEW)
            retrieval_result = await self.retrieve_similar_pages(task_description)
            
            # Step 3: Plan action WITH retrieval (ENHANCED)
            action = await self.plan_next_action_with_rag(
                task_description=task_description,
                current_dom=dom,
                current_url=url
                # retrieval_context is used internally
            )
            
            # Step 4: Execute
            result = await self.execute_action(action)
            
            # Step 5: STORE page + UPDATE annotations (NEW)
            await self.store_current_page(
                dom_content=dom,
                current_url=url,
                task_context=task_description,
                action_history=[action]
            )
            
            if result["success"]:
                await self.update_page_annotations(url, action["selector"], result)
```

---

## 5. LLM Prompting Strategy

### Planning Prompt Template

Use this prompt structure when calling your LLM for action planning:

```
# Web Automation Task Planning

## Current Situation
- **Task Goal:** {task_description}
- **Current Page URL:** {current_url}
- **Current Page Title:** {page_title}

## Current Page Structure
{formatted_current_dom}

## Context from Similar Pages (Retrieved via RAG)
You have successfully completed similar tasks on these pages:

{formatted_similar_pages}

### Proven Interaction Patterns
These selectors and interactions have worked before for similar tasks:
{proven_selectors_with_success_rates}

### Common Navigation Patterns
Other successful workflows used these sequences:
{common_action_sequences}

## Your Task
Based on the above context from similar pages and proven patterns, decide the next action to take.

## Required Response Format
{
  "action": "click|fill|scroll|navigate|wait|extract",
  "selector": "<css_selector>",
  "value": "<value_if_applicable>",
  "reasoning": "<explain_why_this_action_based_on_context>",
  "confidence": <0.0_to_1.0>,
  "retrieval_informed": true|false
}

## Constraints
- Always prefer proven selectors from similar pages
- If multiple patterns work, choose the most frequently successful one
- Explain how the retrieved context influenced your decision
- If no similar pages, still attempt but mark confidence lower
```

### Example Filled Prompt

```
# Web Automation Task Planning

## Current Situation
- **Task Goal:** Search for "laptop with 16GB RAM" on Amazon
- **Current Page URL:** https://www.amazon.com/s
- **Current Page Title:** Amazon.com: Online Shopping

## Current Page Structure
[search-box]
[search-button]
[logo] [nav-menu] [cart]

## Context from Similar Pages (Retrieved via RAG)
Successfully completed 3 similar search tasks:

1. Page: amazon.com/s | Task: "Find iPhone 15"
   - Filled .s-search-input with query
   - Clicked .s-result-sorting-select
   - Success Rate: 100%

2. Page: amazon.com/s | Task: "Search gaming laptop"
   - Filled #twotabsearchtextbox with query
   - Hit Enter key
   - Success Rate: 95%

### Proven Interaction Patterns
- Selector "#twotabsearchtextbox" works 95% of the time for searches
- Selector ".s-search-input" works 90% of the time (alternative)
- After fill: click ".s-search-button" OR press Enter (both work equally)

### Common Navigation Patterns
1. Fill search box → Click search button → Wait for results (95% success)
2. Fill search box → Press Enter → Wait for results (93% success)

## Your Task
Based on the above context from similar pages and proven patterns, decide the next action to take.

## Response
{
  "action": "fill",
  "selector": "#twotabsearchtextbox",
  "value": "laptop with 16GB RAM",
  "reasoning": "Based on retrieval context: similar search tasks use #twotabsearchtextbox 95% of the time. This selector has highest success rate from proven patterns.",
  "confidence": 0.95,
  "retrieval_informed": true
}
```

---

## 6. Setup & Deployment

### Step 1: Install Dependencies

```bash
pip install chromadb sentence-transformers mcp anthropic pymilvus pinecone
```

### Step 2: Initialize Vector DB

```python
# chroma_init.py
import chromadb
from chromadb.config import Settings

client = chromadb.Client(Settings(
    chroma_db_impl="duckdb+parquet",
    persist_directory="./chroma_data",
    anonymized_telemetry=False
))

collection = client.get_or_create_collection(
    name="web_automation_pages",
    metadata={"hnsw:space": "cosine"}
)

print("✓ Chroma DB initialized at ./chroma_data")
```

### Step 3: Add RAG Tools to MCP Server

```python
# mcp_server_rag.py
from mcp.server import Server
from your_rag_module import RAGTools

app = Server("lam-with-rag")
rag = RAGTools(vector_db, embedding_model, llm_client)

# Register all 5 tools
# (see Section 3.4 for full tool implementations)
```

### Step 4: Integrate with Browser Automation

```python
# main_lam.py
from your_lam_module import LAMWithRAG

lam = LAMWithRAG(vector_db, embedding_model, llm_client)
await lam.execute_task("Search for laptop with 16GB RAM and add to cart")
```

---

## 7. Best Practices & Optimization

### Retrieval Optimization
- **Batch similar pages:** Store 3-5 relevant pages, not all pages
- **Domain filtering:** When possible, retrieve from same domain first
- **Temporal decay:** Prioritize recent pages over old ones (add timestamp weight)
- **Hybrid search:** Combine semantic + BM25 for better recall

### Storage Optimization
- **Limit chunk size:** Keep chunks under 300 tokens for faster retrieval
- **Deduplicate:** Don't store near-identical pages
- **Archive old sessions:** Move pages >30 days old to cold storage
- **Compression:** Store full DOM separately, keep only essential data in vectors

### Retrieval Reliability
- **Fallback mechanism:** If retrieval returns <2 results, rely on heuristics
- **Confidence threshold:** Only use retrieved selectors if confidence >0.8
- **Validation:** Always test retrieved selectors before using in production
- **Diversification:** Retrieve from multiple domains if available

### Cost Optimization
- **Batch embeddings:** Embed 50+ pages at once (faster + cheaper)
- **Model selection:** Use smaller models (MiniLM) for speed, larger (MPNet) for accuracy
- **Lazy storage:** Store only successful interactions, discard failures
- **Index pruning:** Remove low-value duplicates monthly

---

## 8. Monitoring & Debugging

### Key Metrics to Track
```python
metrics = {
    "retrieval_success_rate": tasks_with_retrieved_context / total_tasks,
    "avg_retrieval_time_ms": sum(retrieval_times) / len(retrieval_times),
    "selector_success_rate": successful_actions / total_actions,
    "vector_db_size_mb": db_file_size,
    "avg_documents_per_task": total_docs / total_tasks,
    "embedding_quality": cosine_similarity_of_similar_pages
}
```

### Debugging Queries
```python
# What's in the vector DB?
collection.get(limit=100)

# Test retrieval for specific query
results = collection.query(
    query_texts=["search for laptop"],
    n_results=5
)

# Check embedding dimensions
embedding = embedding_model.encode("test")
print(f"Embedding dimension: {len(embedding)}")

# Validate page snapshots
snapshots = vector_db.get_all_snapshots()
print(f"Total pages stored: {len(snapshots)}")
print(f"Average elements per page: {avg_interactive_elements}")
```

---

## 9. Potential Issues & Solutions

| Issue | Cause | Solution |
|-------|-------|----------|
| **Low retrieval quality** | Embeddings don't capture web semantics | Use domain-specific embedding model or fine-tune |
| **Outdated selectors** | Pages change, stored selectors break | Add validation step before using retrieved selectors |
| **Too many results** | Not filtering enough | Add domain + temporal filters, use top-1 instead of top-k |
| **Slow retrieval** | Large vector DB or inefficient indexing | Use HNSW index in Chroma, partition by domain |
| **Memory usage** | Loading full DOM for every page | Store only semantic summary, full DOM in separate cache |
| **Hallucinated selectors** | LLM generates invalid CSS | Validate all selectors against actual DOM before executing |

---

## 10. Roadmap for Enhancement

### Phase 1 (Now): Basic RAG
- ✅ Vector DB setup (Chroma)
- ✅ Store page snapshots
- ✅ Retrieve similar pages
- ✅ Use context for planning

### Phase 2 (Next): Advanced Retrieval
- 🔄 Hybrid semantic + BM25 search
- 🔄 Domain-specific fine-tuned embeddings
- 🔄 Temporal decay weighting
- 🔄 Session-based context windows

### Phase 3 (Future): Feedback & Learning
- 📋 Automatic success/failure annotation
- 📋 Online learning from failed actions
- 📋 Selector validation and repair
- 📋 Pattern evolution over time

### Phase 4 (Future): Optimization
- 📋 Migrate to Milvus for scalability
- 📋 Multi-domain knowledge graphs
- 📋 Cross-domain pattern transfer
- 📋 Production observability dashboard

---

## References

- [Sentence Transformers Documentation](https://www.sbert.net/)
- [Chroma Vector DB](https://docs.trychroma.com/)
- [Milvus Documentation](https://milvus.io/docs)
- [MCP Specification](https://modelcontextprotocol.io/)
- [RAG Best Practices](https://python.langchain.com/docs/use_cases/question_answering/)

---

**Next Steps:**
1. Choose your vector DB (recommend Chroma for now)
2. Implement the 5 RAG tools from Section 3.4
3. Integrate with your current LAM MCP
4. Test with a single domain (e.g., only Amazon searches)
5. Monitor metrics and iterate
