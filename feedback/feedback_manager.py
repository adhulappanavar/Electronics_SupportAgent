import csv
import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional
import pandas as pd

class FeedbackManager:
    def __init__(self, feedback_csv_path: str = "feedback_data/feedback_log.csv"):
        self.feedback_csv_path = Path(feedback_csv_path)
        self.feedback_csv_path.parent.mkdir(exist_ok=True)
        
        # Initialize CSV if it doesn't exist
        if not self.feedback_csv_path.exists():
            self._initialize_feedback_csv()
    
    def _initialize_feedback_csv(self):
        """Initialize the feedback CSV file with headers"""
        headers = [
            'feedback_id',
            'timestamp',
            'user_question',
            'original_answer',
            'original_sources',
            'feedback_type',  # 'unsatisfactory', 'incorrect', 'incomplete'
            'manual_solution',
            'support_agent',
            'brand',
            'product_category',
            'issue_category',
            'resolution_method',
            'customer_satisfaction',
            'tags',
            'notes'
        ]
        
        with open(self.feedback_csv_path, 'w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(headers)
    
    def log_unsatisfactory_answer(self, 
                                 user_question: str,
                                 original_answer: str,
                                 original_sources: List[Dict[str, Any]],
                                 manual_solution: str,
                                 support_agent: str,
                                 feedback_details: Dict[str, Any]) -> str:
        """Log an unsatisfactory answer with manual correction"""
        
        feedback_id = str(uuid.uuid4())
        timestamp = datetime.now().isoformat()
        
        # Extract metadata from sources
        brand = self._extract_primary_brand(original_sources)
        product_category = self._extract_primary_product(original_sources)
        
        # Prepare feedback row
        feedback_row = [
            feedback_id,
            timestamp,
            user_question,
            original_answer,
            json.dumps(original_sources),
            feedback_details.get('feedback_type', 'unsatisfactory'),
            manual_solution,
            support_agent,
            brand,
            product_category,
            feedback_details.get('issue_category', ''),
            feedback_details.get('resolution_method', ''),
            feedback_details.get('customer_satisfaction', ''),
            json.dumps(feedback_details.get('tags', [])),
            feedback_details.get('notes', '')
        ]
        
        # Append to CSV
        with open(self.feedback_csv_path, 'a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(feedback_row)
        
        print(f"Feedback logged with ID: {feedback_id}")
        return feedback_id
    
    def get_feedback_statistics(self) -> Dict[str, Any]:
        """Get statistics about feedback patterns"""
        try:
            df = pd.read_csv(self.feedback_csv_path)
            
            stats = {
                'total_feedback_entries': len(df),
                'feedback_by_type': df['feedback_type'].value_counts().to_dict(),
                'feedback_by_brand': df['brand'].value_counts().to_dict(),
                'feedback_by_product': df['product_category'].value_counts().to_dict(),
                'recent_feedback_count': len(df[df['timestamp'] >= (datetime.now() - pd.Timedelta(days=7)).isoformat()]),
                'top_issue_categories': df['issue_category'].value_counts().head(5).to_dict(),
                'resolution_methods': df['resolution_method'].value_counts().to_dict()
            }
            
            return stats
        except Exception as e:
            print(f"Error generating feedback statistics: {e}")
            return {}
    
    def get_manual_learning_data(self) -> List[Dict[str, Any]]:
        """Extract data for manual learning knowledge base"""
        try:
            df = pd.read_csv(self.feedback_csv_path)
            
            # Filter for entries with good manual solutions
            good_feedback = df[
                (df['manual_solution'].notna()) & 
                (df['manual_solution'] != '') &
                (df['customer_satisfaction'].isin(['satisfied', 'very_satisfied', '4', '5']))
            ]
            
            learning_data = []
            for _, row in good_feedback.iterrows():
                learning_entry = {
                    'id': row['feedback_id'],
                    'question': row['user_question'],
                    'solution': row['manual_solution'],
                    'brand': row['brand'],
                    'product_category': row['product_category'],
                    'issue_category': row['issue_category'],
                    'resolution_method': row['resolution_method'],
                    'timestamp': row['timestamp'],
                    'tags': json.loads(row['tags']) if row['tags'] else [],
                    'source_type': 'manual_learning'
                }
                learning_data.append(learning_entry)
            
            return learning_data
        except Exception as e:
            print(f"Error extracting manual learning data: {e}")
            return []
    
    def search_similar_issues(self, question: str, brand: str = None, product: str = None, limit: int = 5) -> List[Dict[str, Any]]:
        """Search for similar issues in feedback history"""
        try:
            df = pd.read_csv(self.feedback_csv_path)
            
            # Filter by brand and product if specified
            if brand:
                df = df[df['brand'].str.lower() == brand.lower()]
            if product:
                df = df[df['product_category'].str.lower() == product.lower()]
            
            # Simple keyword matching (could be enhanced with embeddings)
            question_words = set(question.lower().split())
            df['relevance_score'] = df['user_question'].apply(
                lambda x: len(set(x.lower().split()).intersection(question_words)) / len(question_words) if x else 0
            )
            
            # Get top matches
            similar_issues = df.nlargest(limit, 'relevance_score')
            
            results = []
            for _, row in similar_issues.iterrows():
                if row['relevance_score'] > 0.2:  # Minimum relevance threshold
                    results.append({
                        'feedback_id': row['feedback_id'],
                        'question': row['user_question'],
                        'manual_solution': row['manual_solution'],
                        'relevance_score': row['relevance_score'],
                        'timestamp': row['timestamp'],
                        'customer_satisfaction': row['customer_satisfaction']
                    })
            
            return results
        except Exception as e:
            print(f"Error searching similar issues: {e}")
            return []
    
    def export_feedback_report(self, output_path: str = "feedback_data/feedback_report.json") -> bool:
        """Export comprehensive feedback report"""
        try:
            stats = self.get_feedback_statistics()
            learning_data = self.get_manual_learning_data()
            
            report = {
                'generated_at': datetime.now().isoformat(),
                'statistics': stats,
                'manual_learning_entries': len(learning_data),
                'recommendations': self._generate_recommendations(stats),
                'learning_data_sample': learning_data[:10]  # First 10 entries as sample
            }
            
            with open(output_path, 'w', encoding='utf-8') as file:
                json.dump(report, file, indent=2, ensure_ascii=False)
            
            print(f"Feedback report exported to: {output_path}")
            return True
        except Exception as e:
            print(f"Error exporting feedback report: {e}")
            return False
    
    def _extract_primary_brand(self, sources: List[Dict[str, Any]]) -> str:
        """Extract the primary brand from sources"""
        brands = [source.get('brand', '') for source in sources if source.get('brand')]
        return brands[0] if brands else ''
    
    def _extract_primary_product(self, sources: List[Dict[str, Any]]) -> str:
        """Extract the primary product category from sources"""
        products = [source.get('product_category', '') for source in sources if source.get('product_category')]
        return products[0] if products else ''
    
    def _generate_recommendations(self, stats: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on feedback patterns"""
        recommendations = []
        
        total_feedback = stats.get('total_feedback_entries', 0)
        if total_feedback > 10:
            # Analyze patterns
            feedback_types = stats.get('feedback_by_type', {})
            top_issues = stats.get('top_issue_categories', {})
            
            if feedback_types.get('incomplete', 0) > total_feedback * 0.3:
                recommendations.append("Consider expanding documentation for incomplete answers")
            
            if feedback_types.get('incorrect', 0) > total_feedback * 0.2:
                recommendations.append("Review and update existing knowledge base for accuracy")
            
            if top_issues:
                top_issue = list(top_issues.keys())[0]
                recommendations.append(f"Focus on improving documentation for '{top_issue}' issues")
        
        return recommendations 