import uuid
import pandas as pd
import numpy as np
from typing import List, Dict, Any, Optional
from sentence_transformers import SentenceTransformer
from database.lancedb_manager import LanceDBManager
from feedback.feedback_manager import FeedbackManager
from config import VECTOR_DIMENSION

class ManualKnowledgeManager:
    def __init__(self, db_path: str = "./manual_knowledge_db"):
        self.db_path = db_path
        self.encoder = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
        self.table_name = "manual_knowledge"
        
        # Initialize LanceDB for manual knowledge
        import lancedb
        self.db = lancedb.connect(db_path)
        self._initialize_table()
        
        # Initialize feedback manager
        self.feedback_manager = FeedbackManager()
    
    def _initialize_table(self):
        """Initialize the manual knowledge table"""
        try:
            self.table = self.db.open_table(self.table_name)
        except Exception:
            # Create table with proper schema
            import pyarrow as pa
            
            schema = pa.schema([
                pa.field("id", pa.string()),
                pa.field("question", pa.string()),
                pa.field("solution", pa.string()),
                pa.field("embedding", pa.list_(pa.float32(), VECTOR_DIMENSION)),
                pa.field("brand", pa.string()),
                pa.field("product_category", pa.string()),
                pa.field("issue_category", pa.string()),
                pa.field("resolution_method", pa.string()),
                pa.field("timestamp", pa.string()),
                pa.field("source_type", pa.string()),
                pa.field("tags", pa.string()),
                pa.field("confidence_score", pa.float32())
            ])
            
            # Create dummy data
            dummy_data = pd.DataFrame({
                "id": ["dummy"],
                "question": ["dummy question"],
                "solution": ["dummy solution"],
                "embedding": [np.zeros(VECTOR_DIMENSION, dtype=np.float32).tolist()],
                "brand": [""],
                "product_category": [""],
                "issue_category": [""],
                "resolution_method": [""],
                "timestamp": [""],
                "source_type": ["manual"],
                "tags": ["[]"],
                "confidence_score": [0.0]
            })
            
            self.table = self.db.create_table(self.table_name, dummy_data, schema=schema)
            self.table.delete("id = 'dummy'")
    
    def sync_from_feedback(self) -> int:
        """Sync manual learning data from feedback manager"""
        learning_data = self.feedback_manager.get_manual_learning_data()
        
        if not learning_data:
            print("No manual learning data to sync")
            return 0
        
        # Process and add to manual knowledge base
        processed_count = 0
        for entry in learning_data:
            if self._add_manual_entry(entry):
                processed_count += 1
        
        print(f"Synced {processed_count} manual learning entries")
        return processed_count
    
    def _add_manual_entry(self, entry: Dict[str, Any]) -> bool:
        """Add a single manual learning entry"""
        try:
            # Check if entry already exists by searching the table
            # We'll use a simple embedding search and then filter results
            dummy_query = "check existing"
            dummy_embedding = self.encoder.encode(dummy_query).astype(np.float32)
            
            search_result = self.table.search(dummy_embedding, vector_column_name="embedding").limit(1000)
            existing_df = search_result.to_pandas()
            
            # Filter for matching ID
            existing = existing_df[existing_df['id'] == entry['id']]
            
            if len(existing) > 0:
                print(f"Manual entry with ID {entry['id']} already exists")
                return False  # Already exists
            
            # Create combined text for embedding
            combined_text = f"Question: {entry['question']} Solution: {entry['solution']}"
            embedding = self.encoder.encode(combined_text).astype(np.float32).tolist()
            
            # Calculate confidence score based on recency and tags
            confidence_score = self._calculate_confidence_score(entry)
            
            # Prepare data
            data = pd.DataFrame({
                "id": [entry['id']],
                "question": [entry['question']],
                "solution": [entry['solution']],
                "embedding": [embedding],
                "brand": [entry.get('brand', '')],
                "product_category": [entry.get('product_category', '')],
                "issue_category": [entry.get('issue_category', '')],
                "resolution_method": [entry.get('resolution_method', '')],
                "timestamp": [entry.get('timestamp', '')],
                "source_type": [entry.get('source_type', 'manual')],
                "tags": [str(entry.get('tags', []))],
                "confidence_score": [confidence_score]
            })
            
            self.table.add(data)
            print(f"✅ Successfully added manual knowledge entry: {entry['id']}")
            return True
            
        except Exception as e:
            print(f"❌ Error adding manual entry: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def search_manual_knowledge(self, query: str, limit: int = 5, filters: Optional[Dict[str, str]] = None) -> List[Dict[str, Any]]:
        """Search manual knowledge base"""
        try:
            # Generate query embedding
            query_embedding = self.encoder.encode(query).astype(np.float32)
            
            # Build search
            search = self.table.search(query_embedding, vector_column_name="embedding").limit(limit * 2)  # Get more for filtering
            
            # Apply filters
            if filters:
                filter_conditions = []
                for key, value in filters.items():
                    if key in ['brand', 'product_category', 'issue_category']:
                        filter_conditions.append(f"{key} = '{value}'")
                
                if filter_conditions:
                    search = search.where(" AND ".join(filter_conditions))
            
            results = search.to_pandas()
            
            # Convert to list and sort by confidence
            manual_results = []
            for _, row in results.iterrows():
                manual_results.append({
                    'id': row['id'],
                    'question': row['question'],
                    'solution': row['solution'],
                    'brand': row['brand'],
                    'product_category': row['product_category'],
                    'issue_category': row['issue_category'],
                    'resolution_method': row['resolution_method'],
                    'timestamp': row['timestamp'],
                    'source_type': row['source_type'],
                    'tags': eval(row['tags']) if row['tags'] else [],
                    'confidence_score': row['confidence_score'],
                    'similarity_score': row.get('_distance', 0)
                })
            
            # Sort by confidence score and limit results
            manual_results.sort(key=lambda x: x['confidence_score'], reverse=True)
            return manual_results[:limit]
            
        except Exception as e:
            print(f"Error searching manual knowledge: {e}")
            return []
    
    def add_real_time_feedback(self, 
                             user_question: str,
                             original_answer: str,
                             manual_solution: str,
                             support_agent: str,
                             metadata: Dict[str, Any]) -> str:
        """Add real-time feedback and immediately update manual knowledge"""
        
        # Log to feedback system
        feedback_id = self.feedback_manager.log_unsatisfactory_answer(
            user_question=user_question,
            original_answer=original_answer,
            original_sources=metadata.get('original_sources', []),
            manual_solution=manual_solution,
            support_agent=support_agent,
            feedback_details=metadata
        )
        
        # Immediately add to manual knowledge if customer was satisfied
        customer_satisfaction = metadata.get('customer_satisfaction')
        print(f"🔍 Customer satisfaction value: '{customer_satisfaction}'")
        print(f"🔍 Checking if '{customer_satisfaction}' is in ['satisfied', 'very_satisfied', '4', '5']")
        
        if customer_satisfaction in ['satisfied', 'very_satisfied', '4', '5']:
            print(f"✅ Customer satisfaction condition met, creating manual knowledge entry...")
            manual_entry = {
                'id': feedback_id,
                'question': user_question,
                'solution': manual_solution,
                'brand': metadata.get('brand', ''),
                'product_category': metadata.get('product_category', ''),
                'issue_category': metadata.get('issue_category', ''),
                'resolution_method': metadata.get('resolution_method', ''),
                'timestamp': metadata.get('timestamp', ''),
                'source_type': 'real_time_manual',
                'tags': metadata.get('tags', [])
            }
            
            if self._add_manual_entry(manual_entry):
                print(f"✅ Successfully added real-time manual knowledge entry: {feedback_id}")
            else:
                print(f"❌ Failed to add manual knowledge entry: {feedback_id}")
        else:
            print(f"⚠️ Customer satisfaction '{customer_satisfaction}' does not meet criteria for manual knowledge creation")
            print(f"💡 Required values: satisfied, very_satisfied, 4, or 5")
        
        return feedback_id
    
    def search(self, query: str, limit: int = 5, brand_filter: str = None, product_filter: str = None) -> List[Dict[str, Any]]:
        """Search manual knowledge database"""
        try:
            # Generate query embedding
            query_embedding = self.encoder.encode(query).astype(np.float32)
            
            # Search the table
            search_result = self.table.search(query_embedding, vector_column_name="embedding").limit(limit * 2)
            df = search_result.to_pandas()
            
            # Apply filters if provided
            if brand_filter and 'brand' in df.columns:
                df = df[df['brand'].str.contains(brand_filter, case=False, na=False)]
            
            if product_filter and 'product_category' in df.columns:
                df = df[df['product_category'].str.contains(product_filter, case=False, na=False)]
            
            # Limit results
            df = df.head(limit)
            
            # Convert to list of dictionaries
            results = []
            for _, row in df.iterrows():
                result = {
                    "id": row.get("id", ""),
                    "question": row.get("question", ""),
                    "solution": row.get("solution", ""),
                    "brand": row.get("brand", ""),
                    "product_category": row.get("product_category", ""),
                    "issue_category": row.get("issue_category", ""),
                    "resolution_method": row.get("resolution_method", ""),
                    "confidence_score": row.get("confidence_score", 0.8),
                    "timestamp": row.get("timestamp", ""),
                    "source_type": row.get("source_type", ""),
                    "tags": row.get("tags", [])
                }
                results.append(result)
            
            return results
            
        except Exception as e:
            print(f"❌ Error searching manual knowledge: {e}")
            return []

    def get_manual_knowledge_stats(self) -> Dict[str, Any]:
        """Get statistics about manual knowledge base"""
        try:
            df = self.table.to_pandas()
            
            if len(df) == 0:
                return {'total_manual_entries': 0}
            
            # Calculate recent entries with proper timestamp handling
            recent_entries_count = 0
            try:
                # Convert timestamp strings to datetime
                df_timestamps = pd.to_datetime(df['timestamp'], errors='coerce')
                recent_cutoff = pd.Timestamp.now() - pd.Timedelta(days=7)
                recent_entries_count = len(df_timestamps[df_timestamps >= recent_cutoff])
            except Exception as e:
                print(f"Warning: Could not calculate recent entries: {e}")
            
            stats = {
                'total_manual_entries': len(df),
                'entries_by_brand': df['brand'].value_counts().to_dict() if 'brand' in df.columns else {},
                'entries_by_product': df['product_category'].value_counts().to_dict() if 'product_category' in df.columns else {},
                'entries_by_issue_category': df['issue_category'].value_counts().to_dict() if 'issue_category' in df.columns else {},
                'avg_confidence_score': df['confidence_score'].mean() if 'confidence_score' in df.columns and len(df) > 0 else 0,
                'high_confidence_entries': len(df[df['confidence_score'] > 0.8]) if 'confidence_score' in df.columns else 0,
                'recent_entries': recent_entries_count
            }
            
            return stats
        except Exception as e:
            print(f"Error getting manual knowledge stats: {e}")
            import traceback
            traceback.print_exc()
            return {'total_manual_entries': 0}
    
    def _calculate_confidence_score(self, entry: Dict[str, Any]) -> float:
        """Calculate confidence score for manual entry"""
        score = 0.5  # Base score
        
        # Recency boost
        try:
            timestamp = pd.to_datetime(entry.get('timestamp', ''))
            days_old = (pd.Timestamp.now() - timestamp).days
            recency_boost = max(0, 0.3 * (1 - days_old / 365))  # Decays over a year
            score += recency_boost
        except:
            pass
        
        # Tag-based boost
        tags = entry.get('tags', [])
        if 'verified' in tags:
            score += 0.2
        if 'expert_validated' in tags:
            score += 0.3
        
        # Resolution method boost
        resolution_method = entry.get('resolution_method', '')
        if 'escalation' in resolution_method.lower():
            score += 0.1
        
        return min(score, 1.0)  # Cap at 1.0
    
    def clear_manual_knowledge(self) -> bool:
        """Clear all manual knowledge entries"""
        try:
            self.table.delete("id != ''")
            print("Manual knowledge base cleared")
            return True
        except Exception as e:
            print(f"Error clearing manual knowledge: {e}")
            return False 