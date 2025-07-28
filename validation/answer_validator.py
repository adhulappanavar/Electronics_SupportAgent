import re
from typing import Dict, Any, List, Optional
from openai import OpenAI
from config import OPENAI_API_KEY

class AnswerValidator:
    def __init__(self):
        self.openai_client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None
        
        # Define validation criteria
        self.validation_criteria = {
            'completeness': 0.3,  # Does it answer the full question?
            'accuracy': 0.4,      # Is the information technically correct?
            'relevance': 0.3      # Is it relevant to the specific product/issue?
        }
    
    def validate_answer(self, question: str, answer: str, context_docs: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Validate an answer against multiple criteria"""
        validation_result = {
            'overall_score': 0.0,
            'is_valid': False,
            'criteria_scores': {},
            'validation_details': {},
            'suggestions': []
        }
        
        # Basic validation checks
        basic_checks = self._perform_basic_checks(question, answer, context_docs)
        
        # Advanced AI-powered validation (if OpenAI available)
        if self.openai_client:
            ai_validation = self._perform_ai_validation(question, answer, context_docs)
            validation_result.update(ai_validation)
        else:
            validation_result.update(basic_checks)
        
        # Calculate overall score
        validation_result['overall_score'] = self._calculate_overall_score(validation_result['criteria_scores'])
        validation_result['is_valid'] = validation_result['overall_score'] >= 0.7  # 70% threshold
        
        return validation_result
    
    def _perform_basic_checks(self, question: str, answer: str, context_docs: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Perform basic validation without AI"""
        criteria_scores = {}
        validation_details = {}
        suggestions = []
        
        # Completeness check
        question_words = set(re.findall(r'\w+', question.lower()))
        answer_words = set(re.findall(r'\w+', answer.lower()))
        overlap = len(question_words.intersection(answer_words)) / len(question_words) if question_words else 0
        criteria_scores['completeness'] = min(overlap * 2, 1.0)  # Scale to 0-1
        
        # Relevance check (based on context)
        if context_docs:
            context_brands = [doc.get('brand', '').lower() for doc in context_docs if doc.get('brand')]
            context_products = [doc.get('product_category', '').lower() for doc in context_docs if doc.get('product_category')]
            
            brand_mentioned = any(brand in answer.lower() for brand in context_brands if brand)
            product_mentioned = any(product in answer.lower() for product in context_products if product)
            
            criteria_scores['relevance'] = 0.8 if (brand_mentioned and product_mentioned) else 0.5
        else:
            criteria_scores['relevance'] = 0.3
        
        # Accuracy check (basic heuristics)
        has_steps = bool(re.search(r'\d+\.|step \d+|first|second|then|next|finally', answer.lower()))
        has_specific_info = bool(re.search(r'settings|menu|button|error|code|temperature|mode', answer.lower()))
        criteria_scores['accuracy'] = 0.7 if (has_steps and has_specific_info) else 0.5
        
        # Generate suggestions
        if criteria_scores['completeness'] < 0.7:
            suggestions.append("Answer may be incomplete - consider addressing all parts of the question")
        if criteria_scores['relevance'] < 0.7:
            suggestions.append("Answer may not be specific enough to the product/brand mentioned")
        if criteria_scores['accuracy'] < 0.7:
            suggestions.append("Answer could include more specific steps or technical details")
        
        return {
            'criteria_scores': criteria_scores,
            'validation_details': validation_details,
            'suggestions': suggestions
        }
    
    def _perform_ai_validation(self, question: str, answer: str, context_docs: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Perform AI-powered validation"""
        try:
            # Prepare context information
            context_summary = self._summarize_context(context_docs)
            
            # Create validation prompt
            validation_prompt = f"""
You are an expert technical support validator. Evaluate the following customer support answer:

CUSTOMER QUESTION: {question}

PROPOSED ANSWER: {answer}

AVAILABLE CONTEXT: {context_summary}

Rate the answer on these criteria (0.0 to 1.0):
1. COMPLETENESS: Does it fully answer the customer's question?
2. ACCURACY: Is the technical information correct and reliable?
3. RELEVANCE: Is it specific to the mentioned product/brand/issue?

Also provide:
- Specific validation details for each criterion
- Actionable suggestions for improvement

Respond in this exact JSON format:
{{
    "criteria_scores": {{
        "completeness": 0.0,
        "accuracy": 0.0,
        "relevance": 0.0
    }},
    "validation_details": {{
        "completeness": "explanation here",
        "accuracy": "explanation here", 
        "relevance": "explanation here"
    }},
    "suggestions": ["suggestion 1", "suggestion 2"]
}}
"""
            
            response = self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": validation_prompt}],
                temperature=0.1
            )
            
            # Parse AI response
            import json
            ai_result = json.loads(response.choices[0].message.content)
            return ai_result
            
        except Exception as e:
            print(f"AI validation failed: {e}")
            return self._perform_basic_checks(question, answer, context_docs)
    
    def _summarize_context(self, context_docs: List[Dict[str, Any]]) -> str:
        """Summarize context documents for validation"""
        if not context_docs:
            return "No context available"
        
        summary_parts = []
        for doc in context_docs[:3]:  # Top 3 most relevant
            brand = doc.get('brand', 'Unknown')
            product = doc.get('product_category', 'Unknown')
            doc_type = doc.get('document_type', 'Unknown')
            summary_parts.append(f"- {brand} {product} {doc_type}")
        
        return "\n".join(summary_parts)
    
    def _calculate_overall_score(self, criteria_scores: Dict[str, float]) -> float:
        """Calculate weighted overall score"""
        total_score = 0.0
        for criterion, weight in self.validation_criteria.items():
            score = criteria_scores.get(criterion, 0.0)
            total_score += score * weight
        return total_score
    
    def validate_batch(self, qa_pairs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Validate multiple question-answer pairs"""
        results = []
        for qa_pair in qa_pairs:
            validation = self.validate_answer(
                qa_pair['question'],
                qa_pair['answer'], 
                qa_pair.get('context_docs', [])
            )
            validation['question'] = qa_pair['question']
            validation['answer'] = qa_pair['answer']
            results.append(validation)
        return results 