import cognee
import asyncio
from typing import List, Dict, Any, Optional
from config import COGNEE_API_KEY
import os
import sqlite3
import pandas as pd
from pathlib import Path

class CogneeManager:
    def __init__(self):
        if COGNEE_API_KEY:
            os.environ["COGNEE_API_KEY"] = COGNEE_API_KEY
        
        # Configure Cognee with correct API
        try:
            cognee.config.set_llm_provider("openai")
            # Use the correct method name suggested by the error
            if hasattr(cognee.config, 'set_vector_engine'):
                cognee.config.set_vector_engine("lancedb")
            else:
                print("Warning: Cognee vector engine configuration unavailable in this version")
        except Exception as e:
            print(f"Warning: Cognee configuration failed: {e}")
    
    async def add_documents_async(self, file_paths: List[str]) -> bool:
        """Add documents to Cognee knowledge graph"""
        try:
            await cognee.add(file_paths)
            await cognee.cognify()
            return True
        except Exception as e:
            print(f"Error adding documents to Cognee: {e}")
            return False
    
    def add_documents(self, file_paths: List[str]) -> bool:
        """Synchronous wrapper for adding documents"""
        try:
            return asyncio.run(self.add_documents_async(file_paths))
        except Exception as e:
            print(f"Error in Cognee add_documents: {e}")
            return False
    
    async def query_async(self, query: str, user_id: str = "default_user") -> str:
        """Query the Cognee knowledge base"""
        try:
            search_results = await cognee.search("SIMILARITY", query_text=query)
            
            if search_results:
                # Extract and format results
                context = ""
                for result in search_results[:5]:  # Top 5 results
                    if hasattr(result, 'text'):
                        context += f"{result.text}\n\n"
                    elif isinstance(result, dict) and 'text' in result:
                        context += f"{result['text']}\n\n"
                
                return context.strip()
            else:
                return "No relevant information found."
        
        except Exception as e:
            print(f"Error querying Cognee: {e}")
            return "Error occurred while searching."
    
    def query(self, query: str, user_id: str = "default_user") -> str:
        """Synchronous wrapper for querying"""
        try:
            return asyncio.run(self.query_async(query, user_id))
        except Exception as e:
            print(f"Error in Cognee query: {e}")
            return f"Cognee query failed: {e}"
    
    async def reset_async(self) -> bool:
        """Reset the Cognee knowledge base"""
        try:
            await cognee.prune.prune_data()
            await cognee.prune.prune_system()
            return True
        except Exception as e:
            print(f"Error resetting Cognee: {e}")
            return False
    
    def reset(self) -> bool:
        """Synchronous wrapper for resetting"""
        try:
            return asyncio.run(self.reset_async())
        except Exception as e:
            print(f"Error in Cognee reset: {e}")
            return False

    def get_status(self) -> Dict[str, Any]:
        """Get comprehensive Cognee status and database information"""
        status = {
            "cognee_version": getattr(cognee, '__version__', 'unknown'),
            "configuration": {},
            "databases": {},
            "system_info": {}
        }
        
        try:
            # Get Cognee configuration
            if hasattr(cognee, 'config'):
                status["configuration"] = {
                    "llm_provider": getattr(cognee.config, 'llm_provider', 'unknown'),
                    "vector_engine": getattr(cognee.config, 'vector_engine', 'unknown'),
                    "api_key_set": bool(os.environ.get("COGNEE_API_KEY"))
                }
        except Exception as e:
            status["configuration"]["error"] = str(e)
        
        # Get database information
        status["databases"] = self._get_database_info()
        
        # Get system directories
        status["system_info"] = self._get_system_info()
        
        return status
    
    def _get_database_info(self) -> Dict[str, Any]:
        """Get information about Cognee databases"""
        db_info = {
            "sqlite": {},
            "vector": {},
            "graph": {}
        }
        
        try:
            # SQLite database information
            sqlite_path = Path.home() / ".pyenv/versions/3.12.2/lib/python3.12/site-packages/cognee/.cognee_system/databases"
            if sqlite_path.exists():
                db_info["sqlite"]["path"] = str(sqlite_path)
                
                # Try to connect and get table information
                cognee_db_path = sqlite_path / "cognee_db"
                if cognee_db_path.exists():
                    db_info["sqlite"]["database_file"] = str(cognee_db_path)
                    db_info["sqlite"]["tables"] = self._get_sqlite_tables(cognee_db_path)
            
            # Vector database information
            vector_db_path = sqlite_path / "cognee.lancedb"
            if vector_db_path.exists():
                db_info["vector"]["path"] = str(vector_db_path)
                db_info["vector"]["size_mb"] = self._get_directory_size(vector_db_path)
            
            # Graph database information  
            graph_db_path = sqlite_path / "cognee_graph_kuzu"
            if graph_db_path.exists():
                db_info["graph"]["path"] = str(graph_db_path)
                db_info["graph"]["size_mb"] = self._get_directory_size(graph_db_path)
                
        except Exception as e:
            db_info["error"] = str(e)
        
        return db_info
    
    def _get_sqlite_tables(self, db_path: Path) -> Dict[str, Any]:
        """Get SQLite table information"""
        tables = {}
        try:
            conn = sqlite3.connect(str(db_path))
            cursor = conn.cursor()
            
            # Get table names
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            table_names = [row[0] for row in cursor.fetchall()]
            
            # Get table info for each table
            for table_name in table_names:
                cursor.execute(f"SELECT COUNT(*) FROM `{table_name}`;")
                count = cursor.fetchone()[0]
                
                cursor.execute(f"PRAGMA table_info(`{table_name}`);")
                columns = cursor.fetchall()
                
                tables[table_name] = {
                    "row_count": count,
                    "columns": [{"name": col[1], "type": col[2]} for col in columns]
                }
            
            conn.close()
        except Exception as e:
            tables["error"] = str(e)
        
        return tables
    
    def _get_directory_size(self, path: Path) -> float:
        """Get directory size in MB"""
        try:
            total_size = sum(f.stat().st_size for f in path.rglob('*') if f.is_file())
            return round(total_size / (1024 * 1024), 2)
        except:
            return 0.0
    
    def _get_system_info(self) -> Dict[str, Any]:
        """Get Cognee system information"""
        info = {}
        try:
            # Try to get Cognee system paths
            import cognee
            
            # Look for common Cognee system directories
            possible_paths = [
                Path.home() / ".pyenv/versions/3.12.2/lib/python3.12/site-packages/cognee/.cognee_system",
                Path.home() / ".cognee_system",
                Path.cwd() / ".cognee_system"
            ]
            
            for path in possible_paths:
                if path.exists():
                    info["system_directory"] = str(path)
                    info["system_size_mb"] = self._get_directory_size(path)
                    break
                    
        except Exception as e:
            info["error"] = str(e)
        
        return info
    
    def get_usage_statistics(self) -> Dict[str, Any]:
        """Get Cognee usage statistics"""
        stats = {
            "documents": {},
            "queries": {},
            "storage": {}
        }
        
        try:
            db_info = self._get_database_info()
            
            # Document statistics from SQLite
            if "sqlite" in db_info and "tables" in db_info["sqlite"]:
                tables = db_info["sqlite"]["tables"]
                
                # Look for document-related tables
                document_tables = [name for name in tables.keys() if 'document' in name.lower() or 'file' in name.lower()]
                total_documents = sum(tables[table]["row_count"] for table in document_tables)
                
                stats["documents"] = {
                    "total_documents": total_documents,
                    "document_tables": document_tables,
                    "table_details": {table: tables[table] for table in document_tables}
                }
            
            # Storage statistics
            stats["storage"] = {
                "vector_db_size_mb": db_info.get("vector", {}).get("size_mb", 0),
                "graph_db_size_mb": db_info.get("graph", {}).get("size_mb", 0),
                "total_size_mb": (
                    db_info.get("vector", {}).get("size_mb", 0) + 
                    db_info.get("graph", {}).get("size_mb", 0)
                )
            }
            
        except Exception as e:
            stats["error"] = str(e)
        
        return stats
    
    def explore_data(self, table_name: str = None, limit: int = 10) -> Dict[str, Any]:
        """Explore Cognee data in SQLite database"""
        result = {"tables": [], "data": {}}
        
        try:
            db_info = self._get_database_info()
            sqlite_db = db_info.get("sqlite", {}).get("database_file")
            
            if not sqlite_db or not Path(sqlite_db).exists():
                return {"error": "Cognee SQLite database not found"}
            
            conn = sqlite3.connect(sqlite_db)
            
            # Get all table names
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            table_names = [row[0] for row in cursor.fetchall()]
            result["tables"] = table_names
            
            # If specific table requested, get data
            if table_name:
                if table_name in table_names:
                    df = pd.read_sql_query(f"SELECT * FROM `{table_name}` LIMIT {limit};", conn)
                    result["data"][table_name] = {
                        "columns": df.columns.tolist(),
                        "row_count": len(df),
                        "sample_data": df.to_dict('records')
                    }
                else:
                    result["error"] = f"Table '{table_name}' not found"
            else:
                # Get sample data from all tables
                for table in table_names[:5]:  # Limit to first 5 tables
                    try:
                        df = pd.read_sql_query(f"SELECT * FROM `{table}` LIMIT 3;", conn)
                        result["data"][table] = {
                            "columns": df.columns.tolist(),
                            "sample_data": df.to_dict('records')
                        }
                    except Exception as e:
                        result["data"][table] = {"error": str(e)}
            
            conn.close()
            
        except Exception as e:
            result["error"] = str(e)
        
        return result 