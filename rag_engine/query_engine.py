from typing import List, Dict, Any, Optional
import openai
from database.lancedb_manager import LanceDBManager
from cognee_integration.cognee_manager import CogneeManager
from config import OPENAI_API_KEY, MAX_TOKENS

class RAGQueryEngine:
    def __init__(self):
        self.db_manager = LanceDBManager()
        self.cognee_manager = CogneeManager()
        
        # Initialize OpenAI
        if OPENAI_API_KEY:
            openai.api_key = OPENAI_API_KEY
            self.openai_client = openai.OpenAI(api_key=OPENAI_API_KEY)
        else:
            self.openai_client = None
            print("Warning: OpenAI API key not set. Chat responses will be limited.")
    
    def search_knowledge_base(self, query: str, filters: Optional[Dict[str, str]] = None, limit: int = 5) -> List[Dict[str, Any]]:
        """Search the knowledge base for relevant documents"""
        return self.db_manager.search(query, limit=limit, filters=filters)
    
    def generate_response(self, query: str, context_docs: List[Dict[str, Any]], use_cognee: bool = False) -> str:
        """Generate a response using the retrieved context"""
        if use_cognee and self.cognee_manager:
            try:
                return self.cognee_manager.query(query)
            except Exception as e:
                print(f"Cognee query failed: {e}, falling back to OpenAI")
        
        if not self.openai_client:
            return self._generate_simple_response(context_docs)
        
        # Prepare context from retrieved documents
        context = self._prepare_context(context_docs)
        
        # Create system prompt
        system_prompt = """You are a helpful technical support assistant for consumer electronics (Samsung/LG products including TVs, Refrigerators, Washing Machines, Speakers, Air Conditioners).

Your job is to answer customer questions using the provided documentation context. Follow these guidelines:

1. Always base your answers on the provided context
2. If the context doesn't contain relevant information, say so clearly
3. Be specific and technical when needed
4. Provide step-by-step instructions for troubleshooting
5. Mention specific model numbers, error codes, or procedures when available
6. If multiple solutions exist, present them in order of preference
7. Always maintain a helpful and professional tone

Context from knowledge base:
{context}"""
        
        # Create messages
        messages = [
            {"role": "system", "content": system_prompt.format(context=context)},
            {"role": "user", "content": query}
        ]
        
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=messages,
                max_tokens=MAX_TOKENS,
                temperature=0.7
            )
            
            return response.choices[0].message.content
        except Exception as e:
            print(f"OpenAI API error: {e}")
            return self._generate_simple_response(context_docs)
    
    def _prepare_context(self, context_docs: List[Dict[str, Any]]) -> str:
        """Prepare context string from retrieved documents"""
        if not context_docs:
            return "No relevant information found in the knowledge base."
        
        context_parts = []
        for i, doc in enumerate(context_docs, 1):
            source_info = f"[Source {i}: {doc.get('brand', 'Unknown')} {doc.get('product_category', '')} - {doc.get('document_type', '')} from {doc.get('file_name', '')}]"
            context_parts.append(f"{source_info}\n{doc['content']}\n")
        
        return "\n".join(context_parts)
    
    def _generate_simple_response(self, context_docs: List[Dict[str, Any]]) -> str:
        """Generate a simple response when OpenAI is not available"""
        if not context_docs:
            return "I couldn't find relevant information in the knowledge base to answer your question."
        
        response = "Based on the available documentation, here's what I found:\n\n"
        
        for i, doc in enumerate(context_docs[:3], 1):
            source = f"{doc.get('brand', 'Unknown')} {doc.get('product_category', '')} {doc.get('document_type', '')}"
            response += f"{i}. From {source}:\n{doc['content'][:300]}...\n\n"
        
        return response
    
    def query(self, user_query: str, filters: Optional[Dict[str, str]] = None, use_cognee: bool = False) -> Dict[str, Any]:
        """Main query method that combines search and response generation"""
        # Search for relevant documents
        relevant_docs = self.search_knowledge_base(user_query, filters=filters)
        
        # Generate response
        response = self.generate_response(user_query, relevant_docs, use_cognee=use_cognee)
        
        # Prepare source information
        sources = []
        for doc in relevant_docs:
            sources.append({
                "file_name": doc.get('file_name', ''),
                "brand": doc.get('brand', ''),
                "product_category": doc.get('product_category', ''),
                "document_type": doc.get('document_type', ''),
                "score": doc.get('score', 0)
            })
        
        return {
            "response": response,
            "sources": sources,
            "found_documents": len(relevant_docs)
        }
    
    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about the knowledge base"""
        doc_count = self.db_manager.get_document_count()
        cognee_status = self.cognee_manager.get_status()
        
        return {
            "total_documents": doc_count,
            "lancedb_status": "active" if doc_count > 0 else "empty",
            "cognee_status": cognee_status,
            "openai_available": self.openai_client is not None
        } 