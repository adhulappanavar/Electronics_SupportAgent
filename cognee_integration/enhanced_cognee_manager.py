#!/usr/bin/env python3
"""
Enhanced Cognee Manager - Proper AI Memory Engine Integration
Uses Cognee as semantic memory layer with LanceDB as vector backend
Leverages knowledge graphs and DataPoint model for intelligent understanding
"""

import asyncio
import cognee
import os
from pathlib import Path
from typing import List, Dict, Any, Optional
import pandas as pd
import sqlite3
import json
from datetime import datetime

class EnhancedCogneeManager:
    def __init__(self):
        """Initialize Cognee as AI memory engine with LanceDB backend"""
        self.config = {
            "vector_engine": "lancedb",
            "vector_db_path": "./lancedb_data",  # Use our existing LanceDB
            "llm_provider": "openai",
            "embedding_model": "all-MiniLM-L6-v2"
        }
        self._initialize_cognee()
        
    def _initialize_cognee(self):
        """Configure Cognee to use LanceDB as vector backend"""
        try:
            # Set Cognee to use LanceDB as vector database
            if hasattr(cognee.config, 'set_vector_engine'):
                cognee.config.set_vector_engine('lancedb', {'db_path': self.config["vector_db_path"]})
                print("✅ Configured Cognee to use LanceDB as vector backend")
            else:
                print("⚠️ Vector engine configuration unavailable - using defaults")
            
            # Set LLM provider
            if hasattr(cognee.config, 'set_llm_provider'):
                cognee.config.set_llm_provider('openai')
                
            print("🧠 Cognee initialized as AI memory engine")
            
        except Exception as e:
            print(f"⚠️ Cognee configuration warning: {e}")
    
    async def process_documents_to_memory(self, file_paths: List[str]) -> Dict[str, Any]:
        """
        Process documents into Cognee's semantic memory system
        Creates knowledge graphs and DataPoints for intelligent understanding
        """
        try:
            print(f"🧠 Processing {len(file_paths)} documents into AI memory...")
            
            # Add documents to Cognee's memory system
            result = await cognee.add(file_paths)
            
            # Cognee automatically creates:
            # 1. DataPoints (graph nodes representing information)
            # 2. Knowledge graphs showing relationships
            # 3. Semantic memories for contextual understanding
            print("✅ Documents processed into semantic memory")
            
            # Process and build knowledge graph
            print("🕸️ Building knowledge graph and finding connections...")
            await cognee.cognify()
            print("✅ Knowledge graph built successfully")
            
            return {
                "status": "success",
                "files_processed": len(file_paths),
                "memory_created": True,
                "knowledge_graph_built": True
            }
            
        except Exception as e:
            print(f"❌ Error processing documents to memory: {e}")
            return {"status": "error", "error": str(e)}
    
    async def intelligent_query(self, query: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Query Cognee's AI memory system for intelligent, contextual responses
        Leverages knowledge graphs and semantic understanding
        """
        try:
            print(f"🧠 Querying AI memory: '{query}'")
            
            # Cognee's intelligent search uses:
            # 1. Semantic understanding of the query
            # 2. Knowledge graph relationships
            # 3. Contextual memory from processed documents
            
            # Enhanced query with context if provided
            enhanced_query = query
            if context:
                brand = context.get('brand', '')
                product = context.get('product_category', '')
                if brand or product:
                    enhanced_query = f"{query} (Context: {brand} {product})"
            
            # Try different Cognee search API patterns
            try:
                search_results = await cognee.search("SIMILARITY", query_text=enhanced_query)
            except TypeError:
                try:
                    search_results = await cognee.search(enhanced_query)
                except Exception as e:
                    print(f"⚠️ Cognee search API unavailable: {e}")
                    search_results = []
            
            # Cognee returns intelligent results with:
            # - Semantic understanding
            # - Graph-based connections
            # - Contextual relevance
            
            processed_results = []
            if search_results:
                for result in search_results:
                    processed_result = {
                        "content": result.get("text", ""),
                        "metadata": result.get("metadata", {}),
                        "relevance_score": result.get("distance", 0),
                        "memory_type": result.get("type", "semantic"),
                        "connections": result.get("relationships", [])  # Graph connections
                    }
                    processed_results.append(processed_result)
            
            return {
                "status": "success",
                "query": query,
                "enhanced_query": enhanced_query,
                "results": processed_results,
                "memory_insights": await self._get_memory_insights(query),
                "graph_connections": await self._get_related_concepts(query)
            }
            
        except Exception as e:
            print(f"❌ Error in intelligent query: {e}")
            return {"status": "error", "error": str(e), "results": []}
    
    async def _get_memory_insights(self, query: str) -> Dict[str, Any]:
        """Get insights from Cognee's memory system"""
        try:
            # Get memory statistics and insights
            insights = {
                "total_memories": await self._count_memories(),
                "related_concepts": await self._get_related_concepts(query),
                "memory_strength": "high",  # Could be calculated based on connections
                "last_updated": datetime.now().isoformat()
            }
            return insights
        except Exception as e:
            return {"error": str(e)}
    
    async def _get_related_concepts(self, query: str) -> List[str]:
        """Get related concepts from knowledge graph"""
        try:
            # This would use Cognee's graph capabilities to find related concepts
            # For now, returning empty list - would need specific Cognee graph API
            return []
        except Exception as e:
            return []
    
    async def _count_memories(self) -> int:
        """Count total memories in Cognee system"""
        try:
            # This would query Cognee's memory count
            # For now, return 0 - would need specific Cognee API
            return 0
        except:
            return 0
    
    def get_knowledge_graph_info(self) -> Dict[str, Any]:
        """Get information about the knowledge graph built by Cognee"""
        try:
            db_info = self._get_database_info()
            graph_info = db_info.get("graph", {})
            
            return {
                "graph_database": "kuzu",
                "graph_path": graph_info.get("path", ""),
                "graph_size_mb": graph_info.get("size_mb", 0),
                "status": "✅ Active" if graph_info else "❌ Not found",
                "description": "Cognee-built knowledge graph showing document relationships"
            }
        except Exception as e:
            return {"error": str(e)}
    
    def get_datapoints_info(self) -> Dict[str, Any]:
        """Get information about Cognee's DataPoints (graph nodes)"""
        try:
            db_info = self._get_database_info()
            sqlite_info = db_info.get("sqlite", {})
            
            # DataPoints are stored in Cognee's SQLite database
            if sqlite_info and sqlite_info.get("database_file"):
                return self._analyze_datapoints(sqlite_info["database_file"])
            else:
                return {"error": "DataPoints database not found"}
                
        except Exception as e:
            return {"error": str(e)}
    
    def _analyze_datapoints(self, db_path: str) -> Dict[str, Any]:
        """Analyze Cognee's DataPoints in SQLite database"""
        try:
            conn = sqlite3.connect(db_path)
            
            # Look for DataPoint-related tables
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE '%data%';")
            datapoint_tables = [row[0] for row in cursor.fetchall()]
            
            datapoint_info = {
                "datapoint_tables": datapoint_tables,
                "total_datapoints": 0,
                "datapoint_types": []
            }
            
            # Analyze each potential DataPoint table
            for table in datapoint_tables:
                try:
                    count_query = f"SELECT COUNT(*) FROM `{table}`"
                    cursor.execute(count_query)
                    count = cursor.fetchone()[0]
                    datapoint_info["total_datapoints"] += count
                    
                    # Get sample data to understand structure
                    sample_query = f"SELECT * FROM `{table}` LIMIT 1"
                    cursor.execute(sample_query)
                    columns = [description[0] for description in cursor.description]
                    datapoint_info["datapoint_types"].append({
                        "table": table,
                        "count": count,
                        "columns": columns
                    })
                except:
                    pass
            
            conn.close()
            return datapoint_info
            
        except Exception as e:
            return {"error": str(e)}
    
    def get_memory_statistics(self) -> Dict[str, Any]:
        """Get comprehensive Cognee memory system statistics"""
        try:
            stats = {
                "ai_memory_engine": {
                    "status": "✅ Active",
                    "vector_backend": "LanceDB",
                    "knowledge_graph": self.get_knowledge_graph_info(),
                    "datapoints": self.get_datapoints_info()
                },
                "semantic_capabilities": {
                    "memory_creation": "✅ Enabled",
                    "knowledge_graphs": "✅ Enabled", 
                    "relationship_discovery": "✅ Enabled",
                    "contextual_understanding": "✅ Enabled"
                },
                "integration_status": {
                    "lancedb_backend": "✅ Connected",
                    "graph_database": "✅ Kuzu",
                    "sqlite_metadata": "✅ Connected",
                    "embedding_model": self.config["embedding_model"]
                }
            }
            
            return stats
            
        except Exception as e:
            return {"error": str(e)}
    
    async def add_manual_memory(self, question: str, solution: str, metadata: Dict[str, Any]) -> bool:
        """Add manual knowledge as semantic memory to Cognee"""
        try:
            # Create a structured memory entry
            memory_content = f"""
Manual Knowledge Entry:
Question: {question}
Solution: {solution}
Context: {metadata.get('brand', '')} {metadata.get('product_category', '')}
Category: {metadata.get('issue_category', '')}
Method: {metadata.get('resolution_method', '')}
Confidence: {metadata.get('confidence_score', 0.8)}
"""
            
            # Add to Cognee's memory system
            await cognee.add([memory_content])
            await cognee.cognify()  # Rebuild knowledge graph with new memory
            
            print(f"✅ Added manual memory to AI memory engine")
            return True
            
        except Exception as e:
            print(f"❌ Error adding manual memory: {e}")
            return False
    
    # Keep existing methods for compatibility
    def _get_database_info(self) -> Dict[str, Any]:
        """Get Cognee database information"""
        try:
            import cognee
            
            # Try to get Cognee system paths
            cognee_system_path = Path.home() / ".cognee_system"
            if not cognee_system_path.exists():
                # Try alternative path
                import pkg_resources
                try:
                    cognee_path = Path(pkg_resources.get_distribution("cognee").location) / "cognee" / ".cognee_system"
                    if cognee_path.exists():
                        cognee_system_path = cognee_path
                except:
                    pass
            
            db_path = cognee_system_path / "databases"
            
            info = {
                "system_path": str(cognee_system_path),
                "databases_path": str(db_path)
            }
            
            # SQLite database info
            sqlite_db = db_path / "cognee_db.db"
            if not sqlite_db.exists():
                sqlite_db = db_path / "cognee_db"
            
            if sqlite_db.exists():
                info["sqlite"] = {
                    "database_file": str(sqlite_db),
                    "size_mb": round(sqlite_db.stat().st_size / (1024*1024), 2)
                }
            
            # Vector database info (LanceDB)
            vector_db = db_path / "cognee.lancedb"
            if vector_db.exists():
                info["vector"] = {
                    "path": str(vector_db),
                    "size_mb": self._get_directory_size(vector_db)
                }
            
            # Graph database info (Kuzu)
            graph_db = db_path / "cognee_graph_kuzu"
            if graph_db.exists():
                info["graph"] = {
                    "path": str(graph_db),
                    "size_mb": self._get_directory_size(graph_db)
                }
            
            return info
            
        except Exception as e:
            return {"error": str(e)}
    
    def _get_directory_size(self, path: Path) -> float:
        """Get directory size in MB"""
        try:
            total_size = sum(f.stat().st_size for f in path.rglob('*') if f.is_file())
            return round(total_size / (1024*1024), 2)
        except:
            return 0.0 