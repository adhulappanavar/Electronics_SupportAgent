#!/usr/bin/env python3
"""
Cognee-Enhanced RAG Engine
Uses Cognee as AI memory engine with LanceDB backend for intelligent responses
Leverages knowledge graphs and semantic understanding
"""

import asyncio
from typing import Dict, List, Any, Optional
import openai
import config
from cognee_integration.enhanced_cognee_manager import EnhancedCogneeManager
from validation.answer_validator import AnswerValidator
from feedback.feedback_manager import FeedbackManager
from database.manual_knowledge_manager import ManualKnowledgeManager

class CogneeEnhancedRAGEngine:
    def __init__(self):
        """Initialize the Cognee-enhanced RAG engine"""
        self.cognee_manager = EnhancedCogneeManager()
        self.validator = AnswerValidator()
        self.feedback_manager = FeedbackManager()
        self.manual_knowledge = ManualKnowledgeManager()
        
        # Set OpenAI API key
        openai.api_key = config.OPENAI_API_KEY
        
        print("🧠 Cognee-Enhanced RAG Engine initialized")
        print("   - AI Memory Engine: ✅ Cognee")
        print("   - Vector Backend: ✅ LanceDB") 
        print("   - Knowledge Graphs: ✅ Enabled")
        print("   - Manual Learning: ✅ Enabled")
    
    async def process_documents(self, file_paths: List[str]) -> Dict[str, Any]:
        """Process documents into Cognee's AI memory system"""
        try:
            print(f"🧠 Processing {len(file_paths)} documents into AI memory...")
            
            # Let Cognee process documents into semantic memory
            result = await self.cognee_manager.process_documents_to_memory(file_paths)
            
            if result["status"] == "success":
                print("✅ Documents processed into AI memory with knowledge graphs")
                return {
                    "success": True,
                    "files_processed": result["files_processed"],
                    "memory_system": "cognee_ai_memory",
                    "knowledge_graph_built": result.get("knowledge_graph_built", False)
                }
            else:
                print(f"❌ Error processing documents: {result.get('error')}")
                return {"success": False, "error": result.get("error")}
                
        except Exception as e:
            print(f"❌ Error in document processing: {e}")
            return {"success": False, "error": str(e)}
    
    async def intelligent_query(self, 
                               query: str, 
                               context: Dict[str, Any] = None,
                               use_validation: bool = True) -> Dict[str, Any]:
        """
        Perform intelligent query using Cognee's AI memory and knowledge graphs
        """
        try:
            print(f"🧠 Processing intelligent query: '{query}'")
            
            # Step 1: Check manual knowledge first (highest priority)
            manual_results = await self._check_manual_knowledge(query, context)
            
            # Step 2: Query Cognee's AI memory system
            cognee_results = await self.cognee_manager.intelligent_query(query, context)
            
            # Step 3: Generate intelligent response using both sources
            response = await self._generate_intelligent_response(
                query, manual_results, cognee_results, context
            )
            
            # Step 4: Validate response if requested
            if use_validation and response.get("answer"):
                validation = self.validator.validate_answer(
                    query, response["answer"], response.get("sources", [])
                )
                response["validation"] = validation
            
            return response
            
        except Exception as e:
            print(f"❌ Error in intelligent query: {e}")
            return {
                "answer": "I apologize, but I encountered an error processing your query.",
                "error": str(e),
                "sources": [],
                "ai_memory_used": False
            }
    
    async def _check_manual_knowledge(self, query: str, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Check manual knowledge database for existing solutions"""
        try:
            if context:
                brand = context.get('brand', '')
                product = context.get('product_category', '')
                
                # Search manual knowledge with context
                manual_results = self.manual_knowledge.search(
                    query, limit=3, brand_filter=brand, product_filter=product
                )
            else:
                manual_results = self.manual_knowledge.search(query, limit=3)
            
            return [
                {
                    "content": result["solution"],
                    "source": "manual_knowledge",
                    "confidence": result.get("confidence_score", 0.9),
                    "metadata": {
                        "brand": result.get("brand", ""),
                        "product_category": result.get("product_category", ""),
                        "issue_category": result.get("issue_category", ""),
                        "resolution_method": result.get("resolution_method", "")
                    }
                }
                for result in manual_results
            ]
            
        except Exception as e:
            print(f"⚠️ Error checking manual knowledge: {e}")
            return []
    
    async def _generate_intelligent_response(self, 
                                           query: str,
                                           manual_results: List[Dict[str, Any]],
                                           cognee_results: Dict[str, Any],
                                           context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate intelligent response using AI memory and manual knowledge"""
        
        try:
            # Combine all sources
            all_sources = []
            source_content = []
            
            # Prioritize manual knowledge (human-validated solutions)
            if manual_results:
                print("✅ Found manual knowledge - using human-validated solutions")
                for result in manual_results[:2]:  # Top 2 manual results
                    all_sources.append(result)
                    source_content.append(f"Manual Solution: {result['content']}")
            
            # Add Cognee AI memory results
            if cognee_results.get("status") == "success" and cognee_results.get("results"):
                print("🧠 Using AI memory insights from knowledge graphs")
                for result in cognee_results["results"][:3]:  # Top 3 AI memory results
                    if result.get("content"):
                        all_sources.append({
                            "content": result["content"],
                            "source": "ai_memory",
                            "confidence": 1.0 - result.get("relevance_score", 0.0),
                            "metadata": result.get("metadata", {}),
                            "memory_type": result.get("memory_type", "semantic"),
                            "connections": result.get("connections", [])
                        })
                        source_content.append(f"AI Memory: {result['content']}")
            
            if not source_content:
                return {
                    "answer": "I don't have specific information about this query in my memory system.",
                    "sources": [],
                    "ai_memory_used": False,
                    "confidence_score": 0.0
                }
            
            # Generate contextual prompt
            context_str = ""
            if context:
                brand = context.get('brand', '')
                product = context.get('product_category', '')
                if brand or product:
                    context_str = f"Context: {brand} {product}\n"
            
            # Create intelligent prompt leveraging both manual and AI memory
            prompt = f"""You are an AI assistant with access to an intelligent memory system and human-validated solutions. 
            
{context_str}
User Question: {query}

Available Information:
{chr(10).join(f"{i+1}. {content}" for i, content in enumerate(source_content))}

Instructions:
1. Prioritize human-validated manual solutions (marked as "Manual Solution")
2. Use AI memory insights to provide comprehensive context
3. If manual solutions exist, use them as the primary answer
4. Supplement with AI memory for additional context or related information
5. Provide a clear, helpful response that combines the best information
6. If the information comes from manual solutions, mention it's been human-validated

Generate a helpful response:"""

            # Get response from OpenAI
            response = openai.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                max_tokens=800
            )
            
            answer = response.choices[0].message.content
            
            # Calculate confidence based on source types
            confidence = self._calculate_confidence(manual_results, cognee_results)
            
            return {
                "answer": answer,
                "sources": all_sources,
                "ai_memory_used": bool(cognee_results.get("results")),
                "manual_knowledge_used": bool(manual_results),
                "knowledge_graph_insights": cognee_results.get("graph_connections", []),
                "memory_insights": cognee_results.get("memory_insights", {}),
                "confidence_score": confidence,
                "source_breakdown": {
                    "manual_solutions": len(manual_results),
                    "ai_memory_results": len(cognee_results.get("results", [])),
                    "total_sources": len(all_sources)
                }
            }
            
        except Exception as e:
            print(f"❌ Error generating intelligent response: {e}")
            return {
                "answer": "I encountered an error while processing your query with the AI memory system.",
                "error": str(e),
                "sources": [],
                "ai_memory_used": False
            }
    
    def _calculate_confidence(self, manual_results: List, cognee_results: Dict) -> float:
        """Calculate confidence score based on source quality"""
        confidence = 0.0
        
        # Manual knowledge gets high confidence (human-validated)
        if manual_results:
            manual_confidence = sum(result.get("confidence", 0.8) for result in manual_results) / len(manual_results)
            confidence = max(confidence, manual_confidence)
        
        # AI memory gets moderate confidence 
        if cognee_results.get("results"):
            ai_confidence = 0.7  # Base confidence for AI memory
            confidence = max(confidence, ai_confidence)
        
        return min(confidence, 1.0)
    
    async def add_feedback_to_memory(self, feedback_data: Dict[str, Any]) -> bool:
        """Add feedback to both manual knowledge and AI memory"""
        try:
            # Add to manual knowledge database
            feedback_id = self.manual_knowledge.add_real_time_feedback(**feedback_data)
            
            # Also add to Cognee's AI memory if it's a good solution
            if feedback_data.get("customer_satisfaction") in ["satisfied", "very_satisfied", "4", "5"]:
                success = await self.cognee_manager.add_manual_memory(
                    feedback_data.get("user_question", ""),
                    feedback_data.get("manual_solution", ""),
                    feedback_data.get("metadata", {})
                )
                
                if success:
                    print("✅ Added feedback to both manual knowledge and AI memory")
                    return True
            
            return bool(feedback_id)
            
        except Exception as e:
            print(f"❌ Error adding feedback to memory: {e}")
            return False
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status"""
        try:
            # Get Cognee memory statistics
            memory_stats = self.cognee_manager.get_memory_statistics()
            
            # Get manual knowledge stats
            manual_stats = self.manual_knowledge.get_manual_knowledge_stats()
            
            # Get feedback stats
            feedback_stats = self.feedback_manager.get_feedback_statistics()
            
            return {
                "system_type": "Cognee-Enhanced RAG with AI Memory",
                "ai_memory_engine": memory_stats,
                "manual_knowledge": {
                    "total_entries": manual_stats.get("total_manual_entries", 0),
                    "recent_entries": manual_stats.get("recent_entries", 0),
                    "avg_confidence": manual_stats.get("avg_confidence_score", 0)
                },
                "feedback_system": {
                    "total_feedback": feedback_stats.get("total_feedback", 0),
                    "manual_corrections": feedback_stats.get("manual_corrections", 0),
                    "satisfaction_rate": feedback_stats.get("avg_satisfaction", 0)
                },
                "capabilities": {
                    "ai_memory": "✅ Active",
                    "knowledge_graphs": "✅ Active", 
                    "semantic_understanding": "✅ Active",
                    "manual_learning": "✅ Active",
                    "validation": "✅ Active"
                }
            }
            
        except Exception as e:
            return {"error": str(e)}
    
    def query_sync(self, query: str, **kwargs) -> Dict[str, Any]:
        """Synchronous wrapper for intelligent query"""
        return asyncio.run(self.intelligent_query(query, **kwargs)) 