"""
RAG Engine for Web Automation MCP
Provides persistent storage and intelligent retrieval of web page interactions.
"""

import os
import json
import logging
import hashlib
from typing import Dict, List, Any, Optional
from datetime import datetime
import chromadb
from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)


class RAGEngine:
    """Manages session-based context for intelligent web automation."""
    
    def __init__(self, session_id: str = None):
        """Initialize RAG engine with ephemeral session storage."""
        self.session_id = session_id or f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Use in-memory client for session-only storage
        self.client = chromadb.Client()
        
        # Create ephemeral collection for this session
        self.collection = self.client.get_or_create_collection(
            name=f"session_{self.session_id}",
            metadata={"hnsw:space": "cosine"}
        )
        
        # Load embedding model
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Session tracking
        self.current_page_chunks = []
        self.navigation_history = []
        
        logger.info(f"RAG Engine initialized for session: {self.session_id}")
    
    def _generate_page_id(self, url: str, timestamp: str) -> str:
        """Generate unique ID for page snapshot."""
        content = f"{url}_{timestamp}"
        return hashlib.md5(content.encode()).hexdigest()
    
    def _extract_semantic_data(self, dom_html: str, url: str) -> Dict[str, Any]:
        """Extract semantic data from DOM HTML."""
        from bs4 import BeautifulSoup
        
        soup = BeautifulSoup(dom_html, 'html.parser')
        
        # Extract page title
        title = soup.find('title')
        title_text = title.get_text().strip() if title else "Untitled"
        
        # Extract interactive elements
        interactive_elements = []
        
        # Buttons
        for button in soup.find_all(['button', 'input']):
            if button.name == 'input' and button.get('type') not in ['text', 'password', 'email', 'search', 'tel', 'url']:
                element_type = button.get('type', 'button')
            else:
                element_type = button.name
            
            label = (
                button.get('aria-label') or 
                button.get('title') or 
                button.get('value') or 
                button.get_text().strip()
            )[:100]
            
            # Generate CSS selector
            elem_id = button.get('id')
            elem_class = button.get('class')
            
            if elem_id:
                selector = f"#{elem_id}"
            elif elem_class:
                selector = f".{elem_class[0]}" if isinstance(elem_class, list) else f".{elem_class}"
            else:
                selector = f"{button.name}[type='{element_type}']" if element_type else button.name
            
            interactive_elements.append({
                "type": element_type,
                "label": label,
                "selector": selector
            })
        
        # Links
        for link in soup.find_all('a', href=True):
            label = link.get_text().strip()[:100]
            href = link.get('href')
            
            elem_id = link.get('id')
            elem_class = link.get('class')
            
            if elem_id:
                selector = f"#{elem_id}"
            elif elem_class:
                selector = f".{elem_class[0]}" if isinstance(elem_class, list) else f".{elem_class}"
            else:
                selector = f"a[href='{href}']"
            
            interactive_elements.append({
                "type": "link",
                "label": label,
                "selector": selector,
                "href": href
            })
        
        # Forms
        forms = []
        for form in soup.find_all('form'):
            form_id = form.get('id', 'unnamed_form')
            fields = []
            
            for input_field in form.find_all(['input', 'textarea', 'select']):
                field_name = input_field.get('name') or input_field.get('id', 'unnamed')
                field_type = input_field.get('type', input_field.name)
                
                fields.append({
                    "name": field_name,
                    "type": field_type
                })
            
            forms.append({
                "id": form_id,
                "fields": fields,
                "field_count": len(fields)
            })
        
        # Extract text content sections
        content_sections = []
        for section in soup.find_all(['section', 'article', 'div'], class_=True):
            section_class = section.get('class')
            if section_class:
                class_name = section_class[0] if isinstance(section_class, list) else section_class
                text_content = section.get_text().strip()[:200]
                
                if text_content:
                    content_sections.append({
                        "type": section.name,
                        "class": class_name,
                        "preview": text_content
                    })
        
        # Detect popups, modals, and overlays
        popups = []
        popup_indicators = [
            'modal', 'popup', 'dialog', 'overlay', 'banner', 
            'cookie', 'consent', 'newsletter', 'announcement',
            'auth', 'login', 'signup', 'age-gate'
        ]
        
        # Check for modals/dialogs
        for element in soup.find_all(['div', 'aside', 'section'], class_=True):
            elem_class = ' '.join(element.get('class', [])).lower()
            elem_id = (element.get('id') or '').lower()
            role = (element.get('role') or '').lower()
            aria_modal = element.get('aria-modal')
            
            # Check if it matches popup patterns
            is_popup = (
                role in ['dialog', 'alertdialog', 'banner'] or
                aria_modal == 'true' or
                any(indicator in elem_class for indicator in popup_indicators) or
                any(indicator in elem_id for indicator in popup_indicators)
            )
            
            if is_popup:
                # Find close button
                close_button = element.find(['button', 'a'], attrs={
                    'aria-label': lambda x: x and 'close' in x.lower()
                }) or element.find(['button', 'a'], attrs={
                    'title': lambda x: x and 'close' in x.lower()
                })
                
                # Classify popup type
                popup_type = 'unknown'
                if 'cookie' in elem_class or 'consent' in elem_class:
                    popup_type = 'cookie_consent'
                elif 'login' in elem_class or 'auth' in elem_class or 'signup' in elem_class:
                    popup_type = 'auth_modal'
                elif 'newsletter' in elem_class or 'subscribe' in elem_class:
                    popup_type = 'newsletter'
                elif 'banner' in elem_class or 'announcement' in elem_class:
                    popup_type = 'banner'
                elif 'age' in elem_class:
                    popup_type = 'age_verification'
                elif role == 'dialog' or aria_modal:
                    popup_type = 'modal_dialog'
                
                popup_info = {
                    "type": popup_type,
                    "role": role,
                    "class": elem_class[:100],
                    "id": elem_id,
                    "close_button": None
                }
                
                if close_button:
                    close_selector = None
                    if close_button.get('id'):
                        close_selector = f"#{close_button.get('id')}"
                    elif close_button.get('class'):
                        classes = close_button.get('class')
                        close_selector = f".{classes[0]}" if isinstance(classes, list) else f".{classes}"
                    elif close_button.get('aria-label'):
                        close_selector = f"[aria-label='{close_button.get('aria-label')}']"
                    
                    popup_info["close_button"] = {
                        "selector": close_selector,
                        "text": close_button.get_text().strip()[:50],
                        "aria_label": close_button.get('aria-label'),
                        "tag": close_button.name
                    }
                
                popups.append(popup_info)
        
        # Also check for common button text patterns for closing
        reject_accept_buttons = []
        for button in soup.find_all(['button', 'a']):
            button_text = button.get_text().strip().lower()
            aria_label = (button.get('aria-label') or '').lower()
            
            if any(text in button_text or text in aria_label for text in [
                'reject', 'accept', 'close', 'dismiss', 'no thanks', 
                'skip', 'not now', 'continue', 'agree'
            ]):
                btn_class = button.get('class')
                btn_id = button.get('id')
                
                selector = None
                if btn_id:
                    selector = f"#{btn_id}"
                elif btn_class:
                    selector = f".{btn_class[0]}" if isinstance(btn_class, list) else f".{btn_class}"
                
                reject_accept_buttons.append({
                    "text": button_text[:50],
                    "selector": selector,
                    "aria_label": button.get('aria-label'),
                    "tag": button.name
                })
        
        return {
            "title": title_text,
            "interactive_elements": interactive_elements[:50],  # Limit to 50
            "forms": forms[:10],  # Limit to 10
            "content_sections": content_sections[:20],  # Limit to 20
            "popups": popups[:10],  # Detected popups/modals
            "popup_buttons": reject_accept_buttons[:20]  # Common popup action buttons
        }
    
    def _create_semantic_chunks(self, page_data: Dict[str, Any]) -> List[str]:
        """Create semantic chunks from page data."""
        chunks = []
        
        # Chunk 1: Page header
        header_chunk = f"""
Page: {page_data['page_data']['title']}
URL: {page_data['page_url']}
Task Context: {page_data['task_context']}
        """.strip()
        chunks.append(header_chunk)
        
        # Chunk 2: Interactive elements
        if page_data['page_data']['interactive_elements']:
            interactive_chunk = "Interactive Elements:\n"
            for elem in page_data['page_data']['interactive_elements'][:20]:
                interactive_chunk += f"- {elem['label']} ({elem['type']}): {elem['selector']}\n"
            chunks.append(interactive_chunk.strip())
        
        # Chunk 3: Forms
        if page_data['page_data']['forms']:
            forms_chunk = "Forms:\n"
            for form in page_data['page_data']['forms']:
                field_names = [f['name'] for f in form['fields'][:10]]
                forms_chunk += f"- {form['id']}: {', '.join(field_names)}\n"
            chunks.append(forms_chunk.strip())
        
        # Chunk 4: Popups and Modals (NEW - for automatic popup detection)
        if page_data['page_data'].get('popups') or page_data['page_data'].get('popup_buttons'):
            popup_chunk = "Popups/Modals Detected:\n"
            
            for popup in page_data['page_data'].get('popups', []):
                popup_chunk += f"- {popup['type']}: role={popup['role']}, class={popup['class'][:50]}\n"
                if popup.get('close_button'):
                    btn = popup['close_button']
                    popup_chunk += f"  Close: {btn['selector']} ('{btn['text']}')\n"
            
            if page_data['page_data'].get('popup_buttons'):
                popup_chunk += "Popup Action Buttons:\n"
                for btn in page_data['page_data']['popup_buttons'][:10]:
                    popup_chunk += f"- {btn['tag']}: '{btn['text']}' → {btn['selector']}\n"
            
            chunks.append(popup_chunk.strip())
        
        # Chunk 5: Content sections
        if page_data['page_data']['content_sections']:
            content_chunk = "Content Sections:\n"
            for section in page_data['page_data']['content_sections'][:10]:
                content_chunk += f"- {section['type']}.{section['class']}: {section['preview']}\n"
            chunks.append(content_chunk.strip())
        
        # Chunk 6: Action history
        if page_data.get('action_history'):
            history_chunk = f"Actions Taken: {len(page_data['action_history'])} interactions\n"
            for action in page_data['action_history'][:5]:
                history_chunk += f"- {action.get('action', 'unknown')}: {action.get('selector', 'N/A')}\n"
            chunks.append(history_chunk.strip())
        
        return [c for c in chunks if c]
    
    def analyze_and_store_page(
        self,
        dom_content: str,
        current_url: str,
        task_context: str,
        action_history: List[Dict] = None
    ) -> Dict[str, Any]:
        """Analyze current page and store context for intelligent element identification."""
        try:
            timestamp = datetime.now().isoformat()
            page_id = self._generate_page_id(current_url, timestamp)
            
            # Track navigation
            self.navigation_history.append({
                "url": current_url,
                "timestamp": timestamp,
                "task": task_context
            })
            
            # Extract semantic data
            semantic_data = self._extract_semantic_data(dom_content, current_url)
            
            # Create page snapshot
            page_snapshot = {
                "id": page_id,
                "page_url": current_url,
                "timestamp": timestamp,
                "task_context": task_context,
                "page_data": semantic_data,
                "action_history": action_history or []
            }
            
            # Create semantic chunks
            chunks = self._create_semantic_chunks(page_snapshot)
            
            # Generate embeddings for all chunks
            embeddings = self.embedding_model.encode(chunks).tolist()
            
            # Store each chunk with embeddings
            documents = []
            metadatas = []
            ids = []
            
            for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
                chunk_id = f"{page_id}_chunk_{i}"
                ids.append(chunk_id)
                documents.append(chunk)
                metadatas.append({
                    "page_id": page_id,
                    "url": current_url,
                    "task_context": task_context,
                    "timestamp": timestamp,
                    "chunk_index": i,
                    "chunk_type": self._get_chunk_type(i),
                    "domain": self._extract_domain(current_url),
                    "snapshot_data": json.dumps(page_snapshot)
                })
            
            # Add to collection
            self.collection.add(
                ids=ids,
                embeddings=embeddings,
                documents=documents,
                metadatas=metadatas
            )
            
            # Track current page chunks for quick access
            self.current_page_chunks = ids
            
            logger.info(f"Analyzed and stored page: {current_url} with {len(chunks)} chunks")
            
            return {
                "status": "analyzed",
                "page_id": page_id,
                "chunks": len(chunks),
                "interactive_elements": len(semantic_data.get('interactive_elements', [])),
                "forms": len(semantic_data.get('forms', [])),
                "url": current_url,
                "session_id": self.session_id
            }
            
        except Exception as e:
            logger.error(f"Failed to store page snapshot: {e}")
            return {
                "status": "error",
                "message": str(e)
            }
    
    def _get_chunk_type(self, index: int) -> str:
        """Get chunk type based on index."""
        types = ["header", "interactive", "forms", "popups", "content", "history"]
        return types[index] if index < len(types) else "other"
    
    def _extract_domain(self, url: str) -> str:
        """Extract domain from URL."""
        from urllib.parse import urlparse
        parsed = urlparse(url)
        return parsed.netloc or "unknown"
    
    def find_relevant_context(
        self,
        task_description: str,
        element_type: Optional[str] = None,
        top_k: int = 5
    ) -> Dict[str, Any]:
        """Find relevant page sections for the current task."""
        try:
            # Build query with element type context if provided
            query_text = task_description
            if element_type:
                query_text = f"{task_description} - looking for {element_type} element"
            
            # Generate query embedding
            query_embedding = self.embedding_model.encode([query_text]).tolist()[0]
            
            # Query current session only
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k
            )
            
            # Process results to return relevant page sections
            relevant_sections = []
            
            if results['ids'] and results['ids'][0]:
                for i, (doc_id, distance, metadata, document) in enumerate(zip(
                    results['ids'][0],
                    results['distances'][0],
                    results['metadatas'][0],
                    results['documents'][0]
                )):
                    # Parse snapshot data
                    snapshot = json.loads(metadata.get('snapshot_data', '{}'))
                    chunk_type = metadata.get('chunk_type', 'unknown')
                    
                    # Extract relevant elements from this section
                    relevant_elements = []
                    if chunk_type == 'interactive':
                        page_data = snapshot.get('page_data', {})
                        for elem in page_data.get('interactive_elements', []):
                            if not element_type or elem.get('type') == element_type:
                                relevant_elements.append(elem)
                    
                    relevant_sections.append({
                        "chunk_id": doc_id,
                        "section_type": chunk_type,
                        "relevance_score": 1 - distance,
                        "content_preview": document[:200],
                        "relevant_elements": relevant_elements,
                        "url": metadata.get('url'),
                        "timestamp": metadata.get('timestamp')
                    })
            
            logger.info(f"Found {len(relevant_sections)} relevant sections for task: {task_description}")
            
            return {
                "status": "success",
                "relevant_sections": relevant_sections,
                "section_count": len(relevant_sections),
                "query": query_text,
                "element_type_filter": element_type
            }
            
        except Exception as e:
            logger.error(f"Failed to retrieve similar pages: {e}")
            return {
                "status": "error",
                "message": str(e),
                "similar_pages": []
            }
    
    def get_element_with_context(
        self,
        element_type: str,
        task_context: str,
        top_k: int = 5
    ) -> Dict[str, Any]:
        """Get elements with surrounding context for better identification."""
        try:
            # Find relevant sections
            relevant_results = self.find_relevant_context(task_context, element_type=element_type, top_k=top_k)
            
            if relevant_results['status'] != 'success':
                return relevant_results
            
            # Extract elements with context
            elements_with_context = []
            
            for section in relevant_results['relevant_sections']:
                for elem in section.get('relevant_elements', []):
                    # Analyze element context
                    context_info = {
                        "selector": elem.get('selector'),
                        "label": elem.get('label', ''),
                        "type": elem.get('type'),
                        "section_relevance": section.get('relevance_score', 0),
                        "section_type": section.get('section_type'),
                        "surrounding_context": section.get('content_preview', ''),
                        "confidence": section.get('relevance_score', 0)
                    }
                    
                    # Add href for links
                    if 'href' in elem:
                        context_info['href'] = elem['href']
                    
                    elements_with_context.append(context_info)
            
            # Sort by relevance/confidence
            elements_with_context.sort(key=lambda x: x['confidence'], reverse=True)
            
            logger.info(f"Found {len(elements_with_context)} elements with context for {element_type}")
            
            return {
                "status": "success",
                "element_type": element_type,
                "elements": elements_with_context[:top_k],
                "total_found": len(elements_with_context),
                "task_context": task_context
            }
            
        except Exception as e:
            logger.error(f"Failed to get proven selectors: {e}")
            return {
                "status": "error",
                "message": str(e)
            }
    
    def get_detected_popups(self) -> Dict[str, Any]:
        """Get all detected popups/modals from current page analysis.
        
        Returns information about popups detected during page analysis,
        including their types, close buttons, and recommended actions.
        """
        try:
            if not self.current_page_chunks:
                return {
                    "status": "no_page_analyzed",
                    "message": "No page has been analyzed yet",
                    "popups": []
                }
            
            # Get the current page data from the latest chunk
            results = self.collection.get(
                ids=self.current_page_chunks,
                include=['metadatas', 'documents']
            )
            
            popups_info = []
            popup_buttons = []
            
            if results['metadatas']:
                for metadata in results['metadatas']:
                    snapshot = json.loads(metadata.get('snapshot_data', '{}'))
                    page_data = snapshot.get('page_data', {})
                    
                    # Extract popup information
                    if page_data.get('popups'):
                        popups_info.extend(page_data['popups'])
                    
                    if page_data.get('popup_buttons'):
                        popup_buttons.extend(page_data['popup_buttons'])
            
            # Deduplicate
            unique_popups = []
            seen = set()
            for popup in popups_info:
                key = f"{popup['type']}_{popup['class']}"
                if key not in seen:
                    seen.add(key)
                    unique_popups.append(popup)
            
            logger.info(f"Retrieved {len(unique_popups)} detected popups")
            
            return {
                "status": "success",
                "popups": unique_popups,
                "popup_buttons": popup_buttons[:20],
                "total_popups": len(unique_popups),
                "has_popups": len(unique_popups) > 0
            }
            
        except Exception as e:
            logger.error(f"Failed to get detected popups: {e}")
            return {
                "status": "error",
                "message": str(e),
                "popups": []
            }
    
    def track_action(
        self,
        page_url: str,
        selector: str,
        action: str,
        success: bool,
        element_type: str = None,
        context: str = None
    ) -> Dict[str, Any]:
        """Track action in current session for progress monitoring."""
        try:
            action_record = {
                "action": action,
                "selector": selector,
                "success": success,
                "element_type": element_type,
                "context": context,
                "timestamp": datetime.now().isoformat(),
                "url": page_url
            }
            
            # Add to navigation history if current page
            if self.navigation_history and self.navigation_history[-1]['url'] == page_url:
                if 'actions' not in self.navigation_history[-1]:
                    self.navigation_history[-1]['actions'] = []
                self.navigation_history[-1]['actions'].append(action_record)
            
            logger.info(f"Tracked action: {action} on {selector} - {'success' if success else 'failed'}")
            
            return {
                "status": "tracked",
                "action": action,
                "selector": selector,
                "success": success,
                "session_id": self.session_id
            }
            
        except Exception as e:
            logger.error(f"Failed to update action result: {e}")
            return {
                "status": "error",
                "message": str(e)
            }
    
    def get_session_progress(self) -> Dict[str, Any]:
        """Get current session progress and statistics."""
        try:
            # Get collection count
            count_result = self.collection.count()
            
            # Count successful and failed actions
            total_actions = 0
            successful_actions = 0
            
            for nav in self.navigation_history:
                for action in nav.get('actions', []):
                    total_actions += 1
                    if action.get('success'):
                        successful_actions += 1
            
            success_rate = successful_actions / total_actions if total_actions > 0 else 0
            
            return {
                "session_id": self.session_id,
                "pages_visited": len(self.navigation_history),
                "current_page_chunks": len(self.current_page_chunks),
                "total_chunks_analyzed": count_result,
                "actions_taken": total_actions,
                "successful_actions": successful_actions,
                "success_rate": success_rate,
                "navigation_history": self.navigation_history[-5:],  # Last 5 pages
                "embedding_model": "all-MiniLM-L6-v2",
                "embedding_dimension": 384
            }
            
        except Exception as e:
            logger.error(f"Failed to get session progress: {e}")
            return {
                "status": "error",
                "message": str(e)
            }
    
    def clear_session(self) -> Dict[str, Any]:
        """Clear current session data."""
        try:
            # Delete the collection
            self.client.delete_collection(name=f"session_{self.session_id}")
            
            # Reset tracking
            self.current_page_chunks = []
            self.navigation_history = []
            
            # Create new collection
            self.collection = self.client.get_or_create_collection(
                name=f"session_{self.session_id}",
                metadata={"hnsw:space": "cosine"}
            )
            
            logger.info(f"Cleared session: {self.session_id}")
            
            return {
                "status": "cleared",
                "session_id": self.session_id
            }
            
        except Exception as e:
            logger.error(f"Failed to clear session: {e}")
            return {
                "status": "error",
                "message": str(e)
            }
