"""Test RAG Engine functionality"""

from browser_mcp_server.rag_engine import RAGEngine

print("🧪 Testing RAG Engine...")
print("=" * 50)

# Initialize RAG engine
print("\n1. Initializing RAG Engine...")
rag = RAGEngine()
print("✅ RAG Engine initialized successfully!")

# Get statistics
print("\n2. Getting statistics...")
stats = rag.get_statistics()
print(f"   Total chunks: {stats['total_chunks']}")
print(f"   Total pages: {stats['total_pages']}")
print(f"   Domains: {stats['domains']}")
print(f"   Embedding model: {stats['embedding_model']}")
print(f"   Embedding dimension: {stats['embedding_dimension']}")

# Test storing a page
print("\n3. Testing page storage...")
test_html = """
<html>
<head><title>Test Page</title></head>
<body>
    <h1>Welcome</h1>
    <input id="search-box" type="text" placeholder="Search...">
    <button id="search-btn">Search</button>
    <a href="/products">Products</a>
</body>
</html>
"""

result = rag.store_page_snapshot(
    dom_content=test_html,
    current_url="https://example.com/test",
    task_context="Testing page storage functionality",
    action_history=[
        {"action": "fill", "selector": "#search-box", "success": True},
        {"action": "click", "selector": "#search-btn", "success": True}
    ]
)

print(f"   Status: {result['status']}")
print(f"   Page ID: {result.get('page_id', 'N/A')}")
print(f"   Chunks stored: {result.get('chunks', 0)}")

# Test retrieval
print("\n4. Testing page retrieval...")
retrieval = rag.retrieve_similar_pages(
    task_description="search functionality test",
    top_k=3
)

print(f"   Status: {retrieval['status']}")
print(f"   Retrieved: {retrieval['retrieved_count']} pages")

# Get updated statistics
print("\n5. Final statistics...")
final_stats = rag.get_statistics()
print(f"   Total pages: {final_stats['total_pages']}")
print(f"   Total chunks: {final_stats['total_chunks']}")

print("\n" + "=" * 50)
print("🎉 RAG Engine test completed successfully!")
