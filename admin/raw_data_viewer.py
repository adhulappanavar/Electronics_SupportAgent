#!/usr/bin/env python3
"""
Raw Data Viewer for Enhanced RAG Knowledge Base
Provides access to raw data from all databases: LanceDB, Kuzu, Cognee, etc.
"""

import pandas as pd
import sqlite3
import json
import os
from pathlib import Path
from typing import Dict, List, Any, Optional
import lancedb
from database.lancedb_manager import LanceDBManager
from database.manual_knowledge_manager import ManualKnowledgeManager
from cognee_integration.cognee_manager import CogneeManager
from feedback.feedback_manager import FeedbackManager

class RawDataViewer:
    def __init__(self):
        self.lance_manager = LanceDBManager()
        self.manual_knowledge = ManualKnowledgeManager()
        self.cognee_manager = CogneeManager()
        self.feedback_manager = FeedbackManager()
    
    def get_lancedb_raw_data(self, table_name: str = "knowledge_base", limit: int = 100) -> Dict[str, Any]:
        """Get raw data from LanceDB tables"""
        try:
            db = lancedb.connect("./lancedb_data")
            
            # Get all table names
            table_names = db.table_names()
            
            result = {
                "available_tables": table_names,
                "current_table": table_name,
                "data": None,
                "error": None
            }
            
            if table_name in table_names:
                table = db.open_table(table_name)
                
                # Get schema information
                schema = table.schema
                result["schema"] = {
                    "fields": [{"name": field.name, "type": str(field.type)} for field in schema]
                }
                
                # Get data
                df = table.to_pandas().head(limit)
                
                # Convert embedding columns to string representation for display
                for col in df.columns:
                    if 'embedding' in col.lower() and df[col].dtype == 'object':
                        df[col] = df[col].apply(lambda x: f"Vector[{len(x)}]" if hasattr(x, '__len__') else str(x))
                
                result["data"] = {
                    "rows": len(table.to_pandas()),
                    "columns": list(df.columns),
                    "sample_data": df.to_dict('records')
                }
            else:
                result["error"] = f"Table '{table_name}' not found"
                
        except Exception as e:
            result = {"error": str(e), "available_tables": []}
        
        return result
    
    def get_manual_knowledge_raw_data(self, limit: int = 100) -> Dict[str, Any]:
        """Get raw data from manual knowledge database"""
        try:
            # Access the manual knowledge table directly
            table = self.manual_knowledge.table
            df = table.to_pandas().head(limit)
            
            # Convert embedding to readable format
            if 'embedding' in df.columns:
                df['embedding'] = df['embedding'].apply(lambda x: f"Vector[{len(x)}]" if hasattr(x, '__len__') else str(x))
            
            return {
                "total_rows": len(table.to_pandas()),
                "columns": list(df.columns),
                "sample_data": df.to_dict('records'),
                "error": None
            }
        except Exception as e:
            return {"error": str(e)}
    
    def get_cognee_sqlite_raw_data(self, table_name: str = None, limit: int = 100) -> Dict[str, Any]:
        """Get raw data from Cognee SQLite database"""
        try:
            db_info = self.cognee_manager._get_database_info()
            sqlite_db = db_info.get("sqlite", {}).get("database_file")
            
            if not sqlite_db or not Path(sqlite_db).exists():
                return {"error": "Cognee SQLite database not found"}
            
            conn = sqlite3.connect(sqlite_db)
            
            # Get all table names
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            table_names = [row[0] for row in cursor.fetchall()]
            
            result = {
                "available_tables": table_names,
                "current_table": table_name,
                "data": None,
                "error": None
            }
            
            if table_name:
                if table_name in table_names:
                    # Get table schema
                    cursor.execute(f"PRAGMA table_info(`{table_name}`);")
                    columns_info = cursor.fetchall()
                    
                    result["schema"] = {
                        "columns": [{"name": col[1], "type": col[2], "nullable": not col[3]} for col in columns_info]
                    }
                    
                    # Get data
                    df = pd.read_sql_query(f"SELECT * FROM `{table_name}` LIMIT {limit};", conn)
                    
                    # Get total count
                    count_df = pd.read_sql_query(f"SELECT COUNT(*) as count FROM `{table_name}`;", conn)
                    total_rows = count_df.iloc[0]['count']
                    
                    result["data"] = {
                        "total_rows": total_rows,
                        "columns": list(df.columns),
                        "sample_data": df.to_dict('records')
                    }
                else:
                    result["error"] = f"Table '{table_name}' not found"
            else:
                # Get summary of all tables
                result["tables_summary"] = {}
                for table in table_names:
                    try:
                        count_df = pd.read_sql_query(f"SELECT COUNT(*) as count FROM `{table}`;", conn)
                        result["tables_summary"][table] = count_df.iloc[0]['count']
                    except:
                        result["tables_summary"][table] = "Error"
            
            conn.close()
            return result
            
        except Exception as e:
            return {"error": str(e)}
    
    def get_kuzu_raw_data(self) -> Dict[str, Any]:
        """Get information about Kuzu graph database"""
        try:
            db_info = self.cognee_manager._get_database_info()
            kuzu_info = db_info.get("graph", {})
            
            if not kuzu_info:
                return {"error": "Kuzu database information not available"}
            
            kuzu_path = Path(kuzu_info.get("path", ""))
            
            result = {
                "database_path": str(kuzu_path),
                "size_mb": kuzu_info.get("size_mb", 0),
                "files": [],
                "error": None
            }
            
            if kuzu_path.exists():
                # List files in Kuzu directory
                result["files"] = [
                    {
                        "name": f.name,
                        "size_mb": round(f.stat().st_size / (1024*1024), 2),
                        "type": f.suffix
                    }
                    for f in kuzu_path.rglob('*') if f.is_file()
                ]
                
                # Try to get basic info (this might need Kuzu Python client)
                try:
                    import kuzu
                    db = kuzu.Database(str(kuzu_path))
                    conn = kuzu.Connection(db)
                    
                    # Try to get node/relationship tables
                    # This is database-specific and might need adjustment
                    result["kuzu_info"] = "Connected to Kuzu database"
                    
                except ImportError:
                    result["kuzu_info"] = "Kuzu Python client not available for detailed inspection"
                except Exception as e:
                    result["kuzu_info"] = f"Could not connect to Kuzu: {e}"
            else:
                result["error"] = "Kuzu database directory not found"
            
            return result
            
        except Exception as e:
            return {"error": str(e)}
    
    def get_feedback_raw_data(self, limit: int = 100) -> Dict[str, Any]:
        """Get raw feedback data from CSV files"""
        try:
            feedback_csv = Path("feedback_data/feedback_log.csv")
            
            if not feedback_csv.exists():
                return {"error": "Feedback CSV file not found"}
            
            df = pd.read_csv(feedback_csv)
            
            return {
                "total_rows": len(df),
                "columns": list(df.columns),
                "sample_data": df.head(limit).to_dict('records'),
                "file_path": str(feedback_csv),
                "file_size_mb": round(feedback_csv.stat().st_size / (1024*1024), 2),
                "error": None
            }
            
        except Exception as e:
            return {"error": str(e)}
    
    def get_system_overview(self) -> Dict[str, Any]:
        """Get overview of all system databases"""
        overview = {
            "lancedb": {},
            "manual_knowledge": {},
            "cognee_sqlite": {},
            "kuzu": {},
            "feedback": {},
            "system_stats": {}
        }
        
        try:
            # LanceDB overview
            lancedb_data = self.get_lancedb_raw_data()
            overview["lancedb"] = {
                "status": "✅ Connected" if not lancedb_data.get("error") else "❌ Error",
                "tables": len(lancedb_data.get("available_tables", [])),
                "error": lancedb_data.get("error")
            }
            
            # Manual knowledge overview
            manual_data = self.get_manual_knowledge_raw_data()
            overview["manual_knowledge"] = {
                "status": "✅ Connected" if not manual_data.get("error") else "❌ Error",
                "rows": manual_data.get("total_rows", 0),
                "error": manual_data.get("error")
            }
            
            # Cognee SQLite overview
            cognee_data = self.get_cognee_sqlite_raw_data()
            overview["cognee_sqlite"] = {
                "status": "✅ Connected" if not cognee_data.get("error") else "❌ Error",
                "tables": len(cognee_data.get("available_tables", [])),
                "error": cognee_data.get("error")
            }
            
            # Kuzu overview
            kuzu_data = self.get_kuzu_raw_data()
            overview["kuzu"] = {
                "status": "✅ Found" if not kuzu_data.get("error") else "❌ Error",
                "size_mb": kuzu_data.get("size_mb", 0),
                "files": len(kuzu_data.get("files", [])),
                "error": kuzu_data.get("error")
            }
            
            # Feedback overview
            feedback_data = self.get_feedback_raw_data()
            overview["feedback"] = {
                "status": "✅ Found" if not feedback_data.get("error") else "❌ Error",
                "rows": feedback_data.get("total_rows", 0),
                "size_mb": feedback_data.get("file_size_mb", 0),
                "error": feedback_data.get("error")
            }
            
            # System stats
            total_size = (
                kuzu_data.get("size_mb", 0) + 
                feedback_data.get("file_size_mb", 0)
            )
            
            overview["system_stats"] = {
                "total_databases": 5,
                "connected_databases": sum(1 for db in overview.values() if isinstance(db, dict) and db.get("status", "").startswith("✅")),
                "total_storage_mb": total_size
            }
            
        except Exception as e:
            overview["system_error"] = str(e)
        
        return overview
    
    def search_across_databases(self, search_term: str, limit: int = 50) -> Dict[str, Any]:
        """Search for a term across all databases"""
        results = {
            "search_term": search_term,
            "lancedb": [],
            "manual_knowledge": [],
            "cognee": [],
            "feedback": []
        }
        
        try:
            # Search LanceDB
            lancedb_data = self.get_lancedb_raw_data(limit=1000)
            if not lancedb_data.get("error") and lancedb_data.get("data"):
                for row in lancedb_data["data"]["sample_data"]:
                    if any(search_term.lower() in str(value).lower() for value in row.values()):
                        results["lancedb"].append(row)
            
            # Search Manual Knowledge
            manual_data = self.get_manual_knowledge_raw_data(limit=1000)
            if not manual_data.get("error"):
                for row in manual_data["sample_data"]:
                    if any(search_term.lower() in str(value).lower() for value in row.values()):
                        results["manual_knowledge"].append(row)
            
            # Search Feedback
            feedback_data = self.get_feedback_raw_data(limit=1000)
            if not feedback_data.get("error"):
                for row in feedback_data["sample_data"]:
                    if any(search_term.lower() in str(value).lower() for value in row.values()):
                        results["feedback"].append(row)
            
            # Limit results
            for key in results:
                if isinstance(results[key], list) and len(results[key]) > limit:
                    results[key] = results[key][:limit]
                    
        except Exception as e:
            results["error"] = str(e)
        
        return results 