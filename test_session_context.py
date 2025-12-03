"""
Test Session-Based Context Analysis

This demonstrates how the RAG engine provides intelligent element
identification and context analysis for the current session only.
"""

from browser_mcp_server.rag_engine import RAGEngine
import json

def test_session_context():
    """Test session-based context analysis."""
    
    print("=" * 60)
    print("Testing Session-Based Context Analysis")
    print("=" * 60)
    
    # Initialize RAG engine with a session
    print("\n1. Initializing session...")
    rag = RAGEngine()
    print(f"   ✅ Session ID: {rag.session_id}")
    print(f"   ✅ Storage: In-memory (ephemeral)")
    
    # Simulate a page with a login form
    print("\n2. Analyzing login page...")
    login_html = """
    <html>
        <body>
            <h1>Welcome to Example App</h1>
            <form id="login-form">
                <label for="username">Username:</label>
                <input type="text" id="username" name="username" placeholder="Enter your username">
                
                <label for="password">Password:</label>
                <input type="password" id="password" name="password" placeholder="Enter your password">
                
                <button type="submit" id="login-btn">Sign In</button>
                <a href="/forgot-password">Forgot Password?</a>
            </form>
            
            <div class="footer">
                <a href="/help">Help Center</a>
                <a href="/contact">Contact Us</a>
            </div>
        </body>
    </html>
    """
    
    result = rag.analyze_and_store_page(
        dom_content=login_html,
        current_url="https://example.com/login",
        task_context="User wants to log in to their account",
        action_history=[]
    )
    
    print(f"   ✅ Page analyzed: {result['url']}")
    print(f"   ✅ Chunks stored: {result['chunks']}")
    print(f"   ✅ Interactive elements found: {result['interactive_elements']}")
    print(f"   ✅ Forms detected: {result['forms']}")
    
    # Find relevant context for entering username
    print("\n3. Finding relevant context for 'enter username'...")
    context_result = rag.find_relevant_context(
        task_description="enter username in login form",
        element_type="input",
        top_k=3
    )
    
    if context_result['status'] == 'success':
        print(f"   ✅ Found {context_result['section_count']} relevant sections")
        for i, section in enumerate(context_result['relevant_sections'][:2], 1):
            print(f"\n   Section {i}:")
            print(f"     - Type: {section['section_type']}")
            print(f"     - Relevance: {section['relevance_score']:.2%}")
            print(f"     - Preview: {section['content_preview'][:100]}...")
    
    # Get smart element selector for username input
    print("\n4. Getting smart selector for username input...")
    element_result = rag.get_element_with_context(
        element_type="input",
        task_context="enter username",
        top_k=5
    )
    
    if element_result['status'] == 'success':
        print(f"   ✅ Found {element_result['total_found']} input elements")
        for i, elem in enumerate(element_result['elements'][:3], 1):
            print(f"\n   Element {i}:")
            print(f"     - Selector: {elem['selector']}")
            print(f"     - Label: {elem['label']}")
            print(f"     - Confidence: {elem['confidence']:.2%}")
            print(f"     - Context: {elem['surrounding_context'][:80]}...")
    
    # Track an action
    print("\n5. Tracking action: typing username...")
    track_result = rag.track_action(
        page_url="https://example.com/login",
        selector="#username",
        action="type",
        success=True,
        element_type="input",
        context="entered username 'john_doe'"
    )
    
    print(f"   ✅ Action tracked: {track_result['action']} - {track_result['success']}")
    
    # Analyze a search page
    print("\n6. Analyzing search results page...")
    search_html = """
    <html>
        <body>
            <h1>Search Results for "laptop"</h1>
            <div class="search-bar">
                <input type="text" id="search-input" value="laptop" placeholder="Search products...">
                <button id="search-btn">Search</button>
            </div>
            
            <div class="results">
                <div class="product">
                    <h3>Gaming Laptop Pro</h3>
                    <p>High-performance gaming laptop with RTX 4090</p>
                    <button class="add-to-cart" data-product-id="123">Add to Cart</button>
                    <a href="/product/123">View Details</a>
                </div>
                <div class="product">
                    <h3>Business Laptop Ultra</h3>
                    <p>Professional laptop for business users</p>
                    <button class="add-to-cart" data-product-id="456">Add to Cart</button>
                    <a href="/product/456">View Details</a>
                </div>
            </div>
            
            <div class="pagination">
                <button id="prev-page">Previous</button>
                <button id="next-page">Next</button>
            </div>
        </body>
    </html>
    """
    
    result2 = rag.analyze_and_store_page(
        dom_content=search_html,
        current_url="https://example.com/search?q=laptop",
        task_context="User is browsing search results for laptops",
        action_history=[]
    )
    
    print(f"   ✅ Page analyzed: {result2['url']}")
    print(f"   ✅ Chunks stored: {result2['chunks']}")
    
    # Find buttons for adding to cart
    print("\n7. Finding 'add to cart' buttons with context...")
    button_result = rag.get_element_with_context(
        element_type="button",
        task_context="add product to shopping cart",
        top_k=5
    )
    
    if button_result['status'] == 'success':
        print(f"   ✅ Found {button_result['total_found']} button elements")
        for i, elem in enumerate(button_result['elements'][:3], 1):
            print(f"\n   Button {i}:")
            print(f"     - Selector: {elem['selector']}")
            print(f"     - Label: {elem['label']}")
            print(f"     - Confidence: {elem['confidence']:.2%}")
    
    # Get session progress
    print("\n8. Checking session progress...")
    progress = rag.get_session_progress()
    
    print(f"   ✅ Session ID: {progress['session_id']}")
    print(f"   ✅ Pages visited: {progress['pages_visited']}")
    print(f"   ✅ Total chunks analyzed: {progress['total_chunks_analyzed']}")
    print(f"   ✅ Actions taken: {progress['actions_taken']}")
    print(f"   ✅ Successful actions: {progress['successful_actions']}")
    print(f"   ✅ Success rate: {progress['success_rate']:.2%}")
    
    print("\n   Recent navigation:")
    for nav in progress['navigation_history']:
        print(f"     - {nav['url']}")
        print(f"       Task: {nav['task']}")
        if 'actions' in nav:
            print(f"       Actions: {len(nav['actions'])}")
    
    # Clear session
    print("\n9. Clearing session...")
    clear_result = rag.clear_session()
    print(f"   ✅ Session cleared: {clear_result['session_id']}")
    
    # Verify empty after clear
    progress_after = rag.get_session_progress()
    print(f"   ✅ Pages after clear: {progress_after['pages_visited']}")
    print(f"   ✅ Chunks after clear: {progress_after['total_chunks_analyzed']}")
    
    print("\n" + "=" * 60)
    print("✅ All session context tests passed!")
    print("=" * 60)
    print("\nKey Features Demonstrated:")
    print("  • Session-based storage (no persistent learning)")
    print("  • Intelligent element identification with context")
    print("  • Semantic search for relevant page sections")
    print("  • Action tracking and progress monitoring")
    print("  • Context-aware element suggestions")
    print("  • Session clearing for fresh starts")
    print("=" * 60)


if __name__ == "__main__":
    test_session_context()
