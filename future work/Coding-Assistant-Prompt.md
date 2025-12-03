# Prompt for Implementing RAG Integration in Web Automation MCP

## Context

I'm building a Large Action Model (LAM) for web automation with Model Context Protocol (MCP). My current implementation observes web DOM and performs actions (click, fill inputs, etc.). 

**GitHub Repository:** https://github.com/Gafoor2005/LAM-mcp

I want to add Retrieval Augmented Generation (RAG) to enhance the system by:
1. **Persisting web page data** across sessions
2. **Intelligently retrieving** similar pages from past interactions
3. **Leveraging proven patterns** (selectors, navigation flows) from similar tasks
4. **Making informed decisions** about next actions using retrieval context

---

## System Design Overview

### Current Architecture
```
observe_dom() → plan_action() → execute_action()
```

### Desired Architecture
```
observe_dom() → retrieve_context() → plan_action_with_context() → execute_action() → store_page() → update_feedback()
```

### Data Flow
1. When visiting a page, extract semantic page data (structure, interactive elements, forms, navigation)
2. Chunk and embed the page data
3. Store in vector database with metadata
4. When planning next action, query vector DB for similar pages
5. Pass retrieval results to LLM planner for better decision-making
6. After executing action, update page annotations based on success/failure

---

## Implementation Requirements

### Part 1: Vector Database & Embeddings

**Objective:** Set up persistent storage for page snapshots with semantic embeddings

**Deliverables:**
1. Initialize vector database (recommend Chroma for prototyping)
   - Collection name: `web_automation_pages`
   - Distance metric: Cosine similarity
   - Persistent storage to `./chroma_data`

2. Load embedding model from sentence-transformers
   - Model: `all-MiniLM-L6-v2` (384-dim, fast, suitable for web content)
   - Method to generate embeddings for page summaries

3. Create data schema for page snapshots
   ```json
   {
     "id": "unique_identifier",
     "page_url": "string",
     "timestamp": "ISO 8601",
     "task_context": "what user is trying to do",
     "page_data": {
       "title": "page title",
       "interactive_elements": [{"selector": "...", "type": "...", "label": "..."}],
       "forms": [...],
       "navigation": [...],
       "content_sections": [...]
     },
     "action_history": [...],
     "vector_embedding": "384-dimensional vector",
     "metadata": {"domain": "...", "session_id": "..."}
   }
   ```

**Success Criteria:**
- Vector DB initialized with persistent storage
- Can store and retrieve page snapshots
- Embeddings have consistent dimensionality (384)
- Similarity search returns relevant results

---

### Part 2: Document Processing & Chunking

**Objective:** Convert raw DOM and page data into semantic chunks suitable for RAG retrieval

**Deliverables:**
1. Function to extract semantic page data from DOM
   - Parse interactive elements (inputs, buttons, links, forms)
   - Identify forms and their fields
   - Extract navigation structure
   - Summarize content sections

2. Semantic chunking function
   - Preserve semantic meaning (don't split related elements)
   - Group by: header/nav, interactive elements, forms, content, task history
   - Chunk size: 150-250 tokens
   - Return list of meaningful chunks

3. Embedding function
   - Batch embed chunks for efficiency
   - Return embeddings in correct format for vector DB

**Success Criteria:**
- Page data properly extracted from arbitrary DOM structures
- Chunks are semantically coherent and meaningful
- Embeddings generated consistently
- Chunking preserves task-relevant information

---

### Part 3: MCP Tools - Part A (Storage & Retrieval)

**Objective:** Create MCP tools to store and retrieve page data

**Deliverables:**

1. **Tool: `store_current_page`**
   - Input: dom_content, current_url, task_context, action_history
   - Process: Extract data → Chunk → Embed → Store in vector DB
   - Output: {"status": "stored", "chunks": N, "embedding_dim": 384}
   - Error handling: Graceful failures with clear messages

2. **Tool: `retrieve_similar_pages`**
   - Input: task_description, top_k=3, domain_filter=None
   - Process: Embed query → Search vector DB → Format results
   - Output: {"similar_pages": [...], "retrieved_count": N}
   - Each result should include: url, task_context, page_title, interactive_elements, similarity_score

3. **Tool: `get_proven_selectors`**
   - Input: element_type (button, input, link, etc.), task_context, top_k=5
   - Process: Retrieve pages → Extract selectors of given type → Rank by success frequency
   - Output: {"proven_selectors": ["selector1", "selector2", ...], "frequency": {...}, "success_rate": 0.0-1.0}

**Success Criteria:**
- Tools integrate with MCP server
- Storage is persistent across sessions
- Retrieval returns relevant, ranked results
- Proven selectors correctly extracted and ranked

---

### Part 4: MCP Tools - Part B (Planning & Feedback)

**Objective:** Create tools for enhanced planning and learning

**Deliverables:**

1. **Tool: `plan_next_action_with_rag`**
   - Input: task_description, current_dom, current_url
   - Process:
     1. Retrieve similar pages (3 results)
     2. Extract proven selectors for relevant element types
     3. Build retrieval context (common patterns, proven interactions)
     4. Call LLM with enhanced prompt (see Part 5)
     5. Return planned action
   - Output: {"action": "click|fill|scroll|...", "selector": "...", "confidence": 0.0-1.0, "context_used": {...}}

2. **Tool: `update_page_annotations`**
   - Input: page_url, element_selector, action_result (success: bool)
   - Process: Update vector DB with success/failure annotation
   - Output: {"status": "updated", "element": "...", "success": bool}
   - Purpose: Build feedback loop - track what works on which pages

**Success Criteria:**
- Planning incorporates retrieval context
- LLM receives properly formatted context
- Confidence scores reflect retrieval quality
- Annotations update successfully in vector DB

---

### Part 5: LLM Prompt Engineering

**Objective:** Create effective prompts that leverage retrieval context for better planning

**Deliverables:**

1. **Prompt Template for Action Planning**
   - Input: task_description, current_dom, current_url, retrieval_context
   - Structure:
     ```
     # Web Automation Task Planning
     
     ## Current Situation
     - Task Goal: [task_description]
     - Current Page: [url, title]
     
     ## Current Page Structure
     [formatted DOM with interactive elements]
     
     ## Context from Similar Pages (RAG Retrieved)
     [3 similar pages with their successful interactions]
     
     ### Proven Interaction Patterns
     [selectors ranked by success rate]
     
     ## Your Task
     Generate next action considering the retrieval context.
     
     ## Response Format
     {
       "action": "...",
       "selector": "...",
       "reasoning": "explain how retrieval context informed this",
       "confidence": 0.0-1.0
     }
     ```

2. **Prompt Variations**
   - For exploration (no retrieval results): More conservative, ask for verification
   - For confident patterns: Use proven selector directly
   - For ambiguous situations: Request multiple action candidates

3. **Context Formatting**
   - Format retrieved pages in readable way for LLM
   - Highlight proven selectors and their success rates
   - Include relevant action sequences from history

**Success Criteria:**
- LLM receives clear, well-structured context
- Actions chosen are justified by retrieval context
- Confidence scores align with retrieval quality
- Prompts are adaptable to different confidence levels

---

### Part 6: Integration with Existing LAM

**Objective:** Integrate RAG tools into current LAM workflow

**Deliverables:**

1. **Modify main task execution loop**
   - Before: observe_dom() → plan() → execute()
   - After: observe_dom() → retrieve() → plan_with_context() → execute() → store() → annotate()

2. **Update action planner**
   - Replace current planning with `plan_next_action_with_rag`
   - Pass retrieval context to LLM
   - Handle cases where retrieval returns no results

3. **Add post-execution hooks**
   - After successful action: call `store_current_page`
   - Track action results: call `update_page_annotations`

4. **Error handling**
   - Graceful degradation if vector DB unavailable
   - Fallback to non-RAG planning if retrieval fails
   - Validation of retrieved selectors before using

**Success Criteria:**
- RAG seamlessly integrated into existing task loop
- System works even if vector DB is down (graceful degradation)
- All pages visited are stored for future use
- Action success/failure is tracked

---

## Technical Specifications

### Tech Stack
- **Vector DB:** Chroma (local, persistent)
- **Embeddings:** sentence-transformers (all-MiniLM-L6-v2)
- **LLM Integration:** Claude/GPT-4 API
- **Language:** Python 3.10+
- **Framework:** MCP (Model Context Protocol)

### Data Persistence
- Vector DB: `./chroma_data/` (DuckDB with Parquet)
- Page snapshots: Serialized JSON in vector DB metadata
- Session logs: Optional, for debugging

### Performance Requirements
- Retrieval latency: <200ms for top-3 results
- Embedding generation: <100ms per page
- Storage per page: <1MB
- Vector DB queries: Support top-k retrieval

### Error Handling
- Invalid selectors: Validation before execution
- Vector DB failures: Fallback to non-RAG planning
- Malformed pages: Graceful degradation
- Rate limiting: Batch requests to LLM

---

## Testing Strategy

### Unit Tests
1. Vector DB initialization and persistence
2. Semantic chunking preserves information
3. Embedding consistency
4. Similarity search returns relevant results
5. Selector extraction accuracy

### Integration Tests
1. Store and retrieve page snapshots
2. Plan actions with retrieval context
3. Update annotations correctly
4. Graceful fallback on retrieval failure
5. End-to-end task with RAG enabled

### Example Test Cases
- Store page A, retrieve should find it
- Similar pages retrieved for same domain
- Proven selectors ranked correctly
- Planning with context produces better decisions than without
- Annotations prevent using failed selectors

---

## Success Metrics

### Quantitative
- Retrieval precision: % of retrieved pages actually relevant to task
- Action success rate: % of LLM-planned actions that succeed with retrieval vs without
- Storage efficiency: bytes per page stored
- Query latency: average retrieval time in milliseconds
- Coverage: % of tasks with at least 1 similar page in vector DB

### Qualitative
- Ease of integration with existing LAM
- Code clarity and maintainability
- Graceful error handling
- Extensibility for future improvements

---

## Deliverables Checklist

- [ ] Part 1: Vector DB & embeddings setup
- [ ] Part 2: Document processing & chunking
- [ ] Part 3: Storage & retrieval MCP tools
- [ ] Part 4: Planning & feedback tools
- [ ] Part 5: LLM prompts for planning
- [ ] Part 6: Integration with existing LAM
- [ ] Error handling & graceful degradation
- [ ] Documentation & usage examples
- [ ] Unit tests for core components
- [ ] Integration tests end-to-end
- [ ] Performance metrics & monitoring

---

## References & Resources

- **Sentence Transformers:** https://www.sbert.net/
- **Chroma Documentation:** https://docs.trychroma.com/
- **MCP Specification:** https://modelcontextprotocol.io/
- **RAG Architecture:** https://python.langchain.com/docs/use_cases/question_answering/
- **Web Automation Best Practices:** https://blog.apify.com/

---

## Notes for Coding Assistant

1. **Start Simple:** Begin with Chroma (local) instead of Milvus for initial development
2. **Test Retrieval Quality:** Verify that similar pages are actually similar before moving forward
3. **Validate Selectors:** Always check retrieved selectors against current DOM before using
4. **Monitor Storage:** Keep track of vector DB size; implement cleanup if needed
5. **Feedback Loop:** Track which selectors work; refine vector DB over time
6. **Session Isolation:** Consider keeping vector DB across sessions (persistent learning)
7. **Error Handling:** Never let vector DB failures break the main LAM flow
8. **Performance:** Profile retrieval speed; optimize if >200ms
9. **Documentation:** Update README with RAG capabilities and usage examples
10. **Future Scaling:** Design for migration to Milvus/Pinecone without refactoring

---

## Communication Checklist

When implementing, ensure:
- [ ] Progress updates on each component
- [ ] Clarify any ambiguous requirements
- [ ] Ask for example pages to test with
- [ ] Confirm LLM integration method (which model/API)
- [ ] Clarify data retention policy (store all pages forever?)
- [ ] Discuss performance vs quality tradeoffs
- [ ] Plan for testing strategy
- [ ] Schedule reviews after each major component
