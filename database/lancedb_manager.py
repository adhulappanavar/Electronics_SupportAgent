import lancedb
import pandas as pd
import numpy as np
from typing import List, Dict, Any, Optional
from sentence_transformers import SentenceTransformer
import os
from config import LANCEDB_PATH, VECTOR_DIMENSION

class LanceDBManager:
    def __init__(self, db_path: str = LANCEDB_PATH):
        self.db_path = db_path
        self.db = lancedb.connect(db_path)
        self.encoder = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
        self.table_name = "knowledge_base"
        self._initialize_table()
    
    def _initialize_table(self):
        """Initialize the LanceDB table if it doesn't exist"""
        try:
            self.table = self.db.open_table(self.table_name)
        except Exception:
            # Create table if it doesn't exist with proper vector schema
            import pyarrow as pa
            
            # Define schema with proper vector type
            schema = pa.schema([
                pa.field("id", pa.string()),
                pa.field("content", pa.string()),
                pa.field("embedding", pa.list_(pa.float32(), VECTOR_DIMENSION)),
                pa.field("metadata", pa.string()),
                pa.field("brand", pa.string()),
                pa.field("product_category", pa.string()),
                pa.field("document_type", pa.string()),
                pa.field("file_name", pa.string()),
                pa.field("chunk_index", pa.int64())
            ])
            
            # Create dummy data to establish schema
            dummy_data = pd.DataFrame({
                "id": ["dummy"],
                "content": ["dummy content"],
                "embedding": [np.zeros(VECTOR_DIMENSION, dtype=np.float32).tolist()],
                "metadata": ["{}"],
                "brand": [""],
                "product_category": [""],
                "document_type": [""],
                "file_name": [""],
                "chunk_index": [0]
            })
            
            self.table = self.db.create_table(self.table_name, dummy_data, schema=schema)
            # Remove dummy data
            self.table.delete("id = 'dummy'")
    
    def add_documents(self, documents: List[Dict[str, Any]]) -> bool:
        """Add documents to the vector database"""
        try:
            for doc in documents:
                # Generate embedding as float32 array
                embedding = self.encoder.encode(doc['content']).astype(np.float32).tolist()
                
                # Prepare data for insertion
                data = pd.DataFrame({
                    "id": [doc['id']],
                    "content": [doc['content']],
                    "embedding": [embedding],
                    "metadata": [str(doc.get('metadata', {}))],
                    "brand": [doc.get('brand', '')],
                    "product_category": [doc.get('product_category', '')],
                    "document_type": [doc.get('document_type', '')],
                    "file_name": [doc.get('file_name', '')],
                    "chunk_index": [doc.get('chunk_index', 0)]
                })
                
                self.table.add(data)
            return True
        except Exception as e:
            print(f"Error adding documents: {e}")
            return False
    
    def search(self, query: str, limit: int = 10, filters: Optional[Dict[str, str]] = None) -> List[Dict[str, Any]]:
        """Search for similar documents"""
        try:
            # Generate query embedding as float32
            query_embedding = self.encoder.encode(query).astype(np.float32)
            
            # Build search with explicit vector column
            search = self.table.search(query_embedding, vector_column_name="embedding").limit(limit)
            
            # Apply filters if provided
            if filters:
                filter_conditions = []
                for key, value in filters.items():
                    if key in ['brand', 'product_category', 'document_type']:
                        filter_conditions.append(f"{key} = '{value}'")
                
                if filter_conditions:
                    search = search.where(" AND ".join(filter_conditions))
            
            results = search.to_pandas()
            
            # Convert to list of dictionaries
            documents = []
            for _, row in results.iterrows():
                documents.append({
                    'id': row['id'],
                    'content': row['content'],
                    'brand': row['brand'],
                    'product_category': row['product_category'],
                    'document_type': row['document_type'],
                    'file_name': row['file_name'],
                    'score': row.get('_distance', 0),
                    'metadata': eval(row['metadata']) if row['metadata'] else {}
                })
            
            return documents
        except Exception as e:
            print(f"Error searching documents: {e}")
            return []
    
    def get_document_count(self) -> int:
        """Get total number of documents in the database"""
        try:
            return len(self.table.to_pandas())
        except:
            return 0
    
    def clear_database(self) -> bool:
        """Clear all documents from the database"""
        try:
            self.table.delete("id != ''")
            return True
        except Exception as e:
            print(f"Error clearing database: {e}")
            return False 