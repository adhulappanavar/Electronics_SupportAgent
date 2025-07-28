from typing import List, Dict, Any, Optional, Tuple
import openai
from database.lancedb_manager import LanceDBManager
from database.manual_knowledge_manager import ManualKnowledgeManager
from validation.answer_validator import AnswerValidator
from cognee_integration.cognee_manager import CogneeManager
from config import OPENAI_API_KEY, MAX_TOKENS

class EnhancedQueryEngine:
    def __init__(self):
        self.db_manager = LanceDBManager()
        self.manual_knowledge = ManualKnowledgeManager()
        self.validator = AnswerValidator()
        self.cognee_manager = CogneeManager()
        
        # Initialize OpenAI
        if OPENAI_API_KEY:
            openai.api_key = OPENAI_API_KEY
            self.openai_client = openai.OpenAI(api_key=OPENAI_API_KEY)
        else:
            self.openai_client = None
            print("Warning: OpenAI API key not set. Responses will be limited.")
    
    def query_with_validation(self, 
                            user_query: str, 
                            filters: Optional[Dict[str, str]] = None,
                            use_cognee: bool = False,
                            validation_enabled: bool = True) -> Dict[str, Any]:
        """Enhanced query with validation and manual knowledge integration"""
        
        # Step 1: Search both knowledge bases
        original_docs = self.db_manager.search(user_query, limit=5, filters=filters)
        manual_docs = self.manual_knowledge.search_manual_knowledge(user_query, limit=3, filters=filters)
        
        # Step 2: Combine and prioritize results
        combined_context = self._combine_knowledge_sources(original_docs, manual_docs)
        
        # Step 3: Generate response
        if use_cognee and self.cognee_manager:
            try:
                response = self.cognee_manager.query(user_query)
                response_source = "cognee"
            except Exception as e:
                print(f"Cognee query failed: {e}, falling back to enhanced generation")
                response = self._generate_enhanced_response(user_query, combined_context)
                response_source = "enhanced_rag"
        else:
            response = self._generate_enhanced_response(user_query, combined_context)
            response_source = "enhanced_rag"
        
        # Step 4: Validate the response
        validation_result = None
        if validation_enabled and response:
            validation_result = self.validator.validate_answer(
                user_query, 
                response, 
                original_docs + manual_docs
            )
        
        # Step 5: Prepare comprehensive result
        result = {
            "response": response,
            "response_source": response_source,
            "original_sources": self._format_sources(original_docs, "original"),
            "manual_sources": self._format_sources(manual_docs, "manual"),
            "total_sources": len(original_docs) + len(manual_docs),
            "validation": validation_result,
            "confidence_indicators": self._calculate_confidence_indicators(original_docs, manual_docs, validation_result)
        }
        
        return result
    
    def _combine_knowledge_sources(self, 
                                 original_docs: List[Dict[str, Any]], 
                                 manual_docs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Combine and prioritize knowledge from both sources"""
        combined = []
        
        # Add manual knowledge first (higher priority for recent human-validated solutions)
        for doc in manual_docs:
            doc['knowledge_source'] = 'manual'
            doc['priority_score'] = doc.get('confidence_score', 0.5) * 1.5  # Boost manual knowledge
            combined.append(doc)
        
        # Add original knowledge
        for doc in original_docs:
            doc['knowledge_source'] = 'original'
            doc['priority_score'] = 1.0 - doc.get('score', 0.5)  # Convert distance to similarity
            combined.append(doc)
        
        # Sort by priority score
        combined.sort(key=lambda x: x.get('priority_score', 0), reverse=True)
        
        return combined[:8]  # Top 8 most relevant across both sources
    
    def _generate_enhanced_response(self, query: str, combined_context: List[Dict[str, Any]]) -> str:
        """Generate response using combined knowledge sources"""
        if not self.openai_client:
            return self._generate_simple_response(combined_context)
        
        # Prepare enhanced context
        context = self._prepare_enhanced_context(combined_context)
        
        # Create enhanced system prompt
        system_prompt = """You are an expert technical support assistant for consumer electronics (Samsung/LG products). 

You have access to TWO types of knowledge:
1. ORIGINAL DOCUMENTATION: Standard manuals, SOPs, and FAQs
2. MANUAL SOLUTIONS: Real solutions provided by human support agents for similar issues

PRIORITY GUIDELINES:
- Prefer MANUAL SOLUTIONS when available (marked as 'manual' source)
- Use ORIGINAL DOCUMENTATION for standard procedures
- Combine both sources when helpful
- Always mention the source type in your response

Response guidelines:
1. Start with the most relevant solution (manual solutions take priority)
2. Provide step-by-step instructions when applicable
3. Include specific model numbers, error codes, or settings when mentioned
4. If using manual solutions, acknowledge they were "previously validated by support agents"
5. Be specific about brand and product details
6. Offer alternative approaches when multiple solutions exist

Context from knowledge bases:
{context}"""
        
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
            return self._generate_simple_response(combined_context)
    
    def _prepare_enhanced_context(self, combined_context: List[Dict[str, Any]]) -> str:
        """Prepare enhanced context from combined sources"""
        if not combined_context:
            return "No relevant information found in either knowledge base."
        
        context_parts = []
        for i, doc in enumerate(combined_context, 1):
            source_type = doc.get('knowledge_source', 'unknown')
            
            if source_type == 'manual':
                # Format manual knowledge
                source_info = f"[MANUAL SOLUTION {i} - Previously validated by support agents]"
                source_info += f"\nBrand: {doc.get('brand', 'Unknown')} | Product: {doc.get('product_category', 'Unknown')}"
                source_info += f"\nIssue Category: {doc.get('issue_category', 'Unknown')}"
                source_info += f"\nResolution Method: {doc.get('resolution_method', 'Unknown')}"
                source_info += f"\nConfidence Score: {doc.get('confidence_score', 0):.2f}"
                
                content = f"Question: {doc.get('question', '')}\nSolution: {doc.get('solution', '')}"
            else:
                # Format original documentation
                source_info = f"[ORIGINAL DOCUMENTATION {i}]"
                source_info += f"\nBrand: {doc.get('brand', 'Unknown')} | Product: {doc.get('product_category', 'Unknown')}"
                source_info += f"\nDocument Type: {doc.get('document_type', 'Unknown')}"
                source_info += f"\nFile: {doc.get('file_name', 'Unknown')}"
                
                content = doc.get('content', '')
            
            context_parts.append(f"{source_info}\n{content}\n")
        
        return "\n---\n".join(context_parts)
    
    def _generate_simple_response(self, combined_context: List[Dict[str, Any]]) -> str:
        """Generate simple response when OpenAI is not available"""
        if not combined_context:
            return "I couldn't find relevant information to answer your question."
        
        response = "Based on available information:\n\n"
        
        # Prioritize manual solutions
        manual_solutions = [doc for doc in combined_context if doc.get('knowledge_source') == 'manual']
        original_docs = [doc for doc in combined_context if doc.get('knowledge_source') == 'original']
        
        if manual_solutions:
            response += "**Verified Solution (from support agent experience):**\n"
            best_manual = manual_solutions[0]
            response += f"{best_manual.get('solution', '')}\n\n"
        
        if original_docs:
            response += "**From documentation:**\n"
            for i, doc in enumerate(original_docs[:2], 1):
                source = f"{doc.get('brand', '')} {doc.get('product_category', '')} {doc.get('document_type', '')}"
                response += f"{i}. {source}:\n{doc.get('content', '')[:200]}...\n\n"
        
        return response
    
    def _format_sources(self, docs: List[Dict[str, Any]], source_type: str) -> List[Dict[str, Any]]:
        """Format source information for response"""
        sources = []
        for doc in docs:
            if source_type == "manual":
                sources.append({
                    "type": "manual_solution",
                    "question": doc.get('question', ''),
                    "brand": doc.get('brand', ''),
                    "product_category": doc.get('product_category', ''),
                    "issue_category": doc.get('issue_category', ''),
                    "confidence_score": doc.get('confidence_score', 0),
                    "timestamp": doc.get('timestamp', ''),
                    "resolution_method": doc.get('resolution_method', '')
                })
            else:
                sources.append({
                    "type": "original_documentation",
                    "file_name": doc.get('file_name', ''),
                    "brand": doc.get('brand', ''),
                    "product_category": doc.get('product_category', ''),
                    "document_type": doc.get('document_type', ''),
                    "relevance_score": doc.get('score', 0)
                })
        return sources
    
    def _calculate_confidence_indicators(self, 
                                       original_docs: List[Dict[str, Any]], 
                                       manual_docs: List[Dict[str, Any]], 
                                       validation_result: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate confidence indicators for the response"""
        indicators = {
            "has_manual_solutions": len(manual_docs) > 0,
            "manual_solution_confidence": max([doc.get('confidence_score', 0) for doc in manual_docs], default=0),
            "original_docs_count": len(original_docs),
            "total_sources": len(original_docs) + len(manual_docs),
            "validation_score": validation_result.get('overall_score', 0) if validation_result else None,
            "is_validated": validation_result.get('is_valid', False) if validation_result else None
        }
        
        # Overall confidence calculation
        confidence = 0.5  # Base confidence
        
        if indicators["has_manual_solutions"]:
            confidence += 0.3  # Boost for manual solutions
            confidence += indicators["manual_solution_confidence"] * 0.2
        
        if indicators["original_docs_count"] > 0:
            confidence += min(indicators["original_docs_count"] * 0.1, 0.3)
        
        if indicators["validation_score"]:
            confidence = (confidence + indicators["validation_score"]) / 2
        
        indicators["overall_confidence"] = min(confidence, 1.0)
        
        return indicators
    
    def get_comprehensive_stats(self) -> Dict[str, Any]:
        """Get comprehensive statistics from all knowledge sources"""
        original_stats = self.db_manager.get_document_count()
        manual_stats = self.manual_knowledge.get_manual_knowledge_stats()
        
        return {
            "original_knowledge": {
                "document_count": original_stats
            },
            "manual_knowledge": manual_stats,
            "validation_available": self.validator is not None,
            "cognee_available": self.cognee_manager is not None,
            "openai_available": self.openai_client is not None
        } 