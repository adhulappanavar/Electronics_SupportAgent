#!/usr/bin/env python3
"""
Enhanced RAG Knowledge Base with Validation and Feedback Learning
Main application entry point
"""

import os
import sys
import argparse
from pathlib import Path
from typing import Optional, Dict

from rag_engine.enhanced_query_engine import EnhancedQueryEngine
from database.manual_knowledge_manager import ManualKnowledgeManager
from feedback.feedback_manager import FeedbackManager
from validation.answer_validator import AnswerValidator
from sample_data.create_sample_data import create_sample_data

def setup_environment():
    """Setup environment and check requirements"""
    env_file = Path(".env")
    if not env_file.exists():
        print("⚠️  No .env file found. Creating from template...")
        print("Please edit .env file with your API keys before running.")
        
        # Create basic .env file
        with open(".env", "w") as f:
            f.write("OPENAI_API_KEY=your_openai_api_key_here\n")
            f.write("COGNEE_API_KEY=your_cognee_api_key_here\n")
        return False
    
    return True

def initialize_enhanced_system(load_sample: bool = False) -> EnhancedQueryEngine:
    """Initialize the enhanced knowledge base system"""
    print("🚀 Initializing Enhanced RAG Knowledge Base...")
    
    # Initialize enhanced components
    enhanced_engine = EnhancedQueryEngine()
    manual_knowledge = ManualKnowledgeManager()
    feedback_manager = FeedbackManager()
    validator = AnswerValidator()
    
    print("✅ Enhanced components initialized successfully")
    
    # Load sample data if requested
    if load_sample:
        print("📁 Creating and loading sample data...")
        sample_dir = create_sample_data()
        
        print("📄 Processing sample documents...")
        documents = enhanced_engine.db_manager.get_document_count()
        
        if documents == 0:  # Only load if no documents exist
            from processors.document_processor import DocumentProcessor
            processor = DocumentProcessor()
            docs = processor.process_directory(str(sample_dir))
            
            if docs:
                print(f"💾 Adding {len(docs)} document chunks to database...")
                success = enhanced_engine.db_manager.add_documents(docs)
                if success:
                    print("✅ Sample data loaded successfully!")
                else:
                    print("❌ Failed to load sample data")
            else:
                print("⚠️  No documents found in sample data")
        else:
            print(f"📊 Using existing {documents} documents")
    
    # Print comprehensive stats
    stats = enhanced_engine.get_comprehensive_stats()
    print(f"\n📊 Enhanced Knowledge Base Stats:")
    print(f"   Original Documents: {stats['original_knowledge']['document_count']}")
    print(f"   Manual Solutions: {stats['manual_knowledge'].get('total_manual_entries', 0)}")
    print(f"   Validation: {'Available' if stats['validation_available'] else 'Not available'}")
    print(f"   OpenAI: {'Available' if stats['openai_available'] else 'Not configured'}")
    print(f"   Cognee: {'Available' if stats['cognee_available'] else 'Not configured'}")
    
    return enhanced_engine

def run_enhanced_cli_mode(enhanced_engine: EnhancedQueryEngine):
    """Run enhanced CLI mode with validation and feedback"""
    print("\n💬 Enhanced CLI Mode - Type 'quit' to exit")
    print("Features: Answer validation, manual knowledge integration, feedback collection")
    print("\nExample queries:")
    print("  - Samsung TV won't turn on after following manual steps")
    print("  - LG washer shows error code IE - tried cleaning filter")
    print("  - Refrigerator temperature issue - customer already tried basic troubleshooting")
    
    while True:
        try:
            question = input("\n🤔 Your question: ").strip()
            
            if question.lower() in ['quit', 'exit', 'q']:
                break
            
            if not question:
                continue
            
            print("🔍 Searching knowledge bases and validating response...")
            
            # Use enhanced query with validation
            result = enhanced_engine.query_with_validation(
                question, 
                filters=None,
                use_cognee=False,
                validation_enabled=True
            )
            
            print(f"\n🤖 Answer:")
            print(result['response'])
            
            # Show confidence and validation info
            confidence = result.get('confidence_indicators', {})
            print(f"\n🎯 Confidence: {confidence.get('overall_confidence', 0.5):.1%}")
            
            if confidence.get('has_manual_solutions'):
                print("✅ Includes verified manual solutions from support agents")
            
            # Show validation results
            validation = result.get('validation')
            if validation:
                print(f"📊 Validation Score: {validation.get('overall_score', 0):.1%}")
                if validation.get('is_valid'):
                    print("✅ Answer validated as accurate")
                else:
                    print("⚠️  Answer may need review")
                    if validation.get('suggestions'):
                        print("💡 Suggestions: " + "; ".join(validation['suggestions']))
            
            # Show sources
            total_sources = result.get('total_sources', 0)
            if total_sources > 0:
                print(f"\n📚 Sources ({total_sources} total):")
                
                # Manual sources first
                manual_sources = result.get('manual_sources', [])
                if manual_sources:
                    print("  🔧 Manual Solutions:")
                    for i, source in enumerate(manual_sources[:2], 1):
                        conf = source.get('confidence_score', 0)
                        print(f"    {i}. {source['brand']} {source['product_category']} - {source['issue_category']} (Confidence: {conf:.1%})")
                
                # Original documentation
                original_sources = result.get('original_sources', [])
                if original_sources:
                    print("  📖 Documentation:")
                    for i, source in enumerate(original_sources[:2], 1):
                        print(f"    {i}. {source['brand']} {source['product_category']} - {source['document_type']}")
            
            # Ask for feedback
            print(f"\n📝 Was this answer helpful? (y/n/s for 'add manual solution'): ", end='')
            feedback = input().strip().lower()
            
            if feedback == 'n':
                collect_negative_feedback(enhanced_engine, question, result)
            elif feedback == 's':
                collect_manual_solution(enhanced_engine, question, result)
            elif feedback == 'y':
                print("👍 Thank you for the positive feedback!")
        
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"❌ Error: {e}")
    
    print("\n👋 Goodbye!")

def collect_negative_feedback(enhanced_engine: EnhancedQueryEngine, question: str, result: Dict):
    """Collect negative feedback about an answer"""
    print("\n📝 Feedback Collection:")
    issue_type = input("What was wrong? (incomplete/incorrect/irrelevant): ").strip()
    additional_notes = input("Additional notes (optional): ").strip()
    
    # Log feedback for analysis
    print("📊 Feedback logged for system improvement")

def collect_manual_solution(enhanced_engine: EnhancedQueryEngine, question: str, result: Dict):
    """Collect manual solution from support agent"""
    print("\n🔧 Manual Solution Entry:")
    agent_name = input("Support agent name: ").strip()
    manual_solution = input("What was the actual solution that worked?: ").strip()
    
    if not manual_solution:
        print("❌ Manual solution is required")
        return
    
    brand = input("Brand (Samsung/LG): ").strip()
    product = input("Product category: ").strip()
    issue_category = input("Issue category: ").strip()
    resolution_method = input("Resolution method (phone/email/chat/escalation): ").strip()
    satisfaction = input("Customer satisfaction (satisfied/very_satisfied): ").strip()
    
    # Create metadata
    metadata = {
        'brand': brand,
        'product_category': product,
        'issue_category': issue_category,
        'resolution_method': resolution_method,
        'customer_satisfaction': satisfaction,
        'tags': ['cli_entry', 'manual_verified'],
        'notes': 'Entered via CLI',
        'feedback_type': 'manual_correction',
        'timestamp': datetime.now().isoformat(),
        'original_sources': result.get('original_sources', [])
    }
    
    # Add to manual knowledge
    feedback_id = enhanced_engine.manual_knowledge.add_real_time_feedback(
        user_question=question,
        original_answer=result['response'],
        manual_solution=manual_solution,
        support_agent=agent_name,
        metadata=metadata
    )
    
    print(f"✅ Manual solution added to knowledge base! ID: {feedback_id}")

def run_enhanced_web_interface():
    """Launch the enhanced Streamlit web interface"""
    print("🌐 Launching enhanced web interface...")
    os.system("streamlit run chat_interface/enhanced_streamlit_app.py")

def demonstrate_validation():
    """Demonstrate validation capabilities"""
    print("\n🧪 Validation System Demo")
    print("=" * 50)
    
    validator = AnswerValidator()
    
    # Test cases
    test_cases = [
        {
            "question": "How do I connect my Samsung TV to WiFi?",
            "answer": "Go to Settings > Network > WiFi and select your network. Enter password when prompted.",
            "context": [{"brand": "Samsung", "product_category": "TV", "document_type": "FAQ"}]
        },
        {
            "question": "LG washing machine error code IE",
            "answer": "Try different settings.",
            "context": [{"brand": "LG", "product_category": "Washing Machine", "document_type": "FAQ"}]
        }
    ]
    
    for i, test in enumerate(test_cases, 1):
        print(f"\nTest {i}: {test['question']}")
        print(f"Answer: {test['answer']}")
        
        validation = validator.validate_answer(test['question'], test['answer'], test['context'])
        
        print(f"Validation Score: {validation['overall_score']:.1%}")
        print(f"Valid: {'✅ Yes' if validation['is_valid'] else '❌ No'}")
        
        if validation['suggestions']:
            print(f"Suggestions: {'; '.join(validation['suggestions'])}")

def main():
    """Enhanced main application entry point"""
    parser = argparse.ArgumentParser(description="Enhanced RAG Knowledge Base with Validation & Feedback")
    parser.add_argument("--mode", choices=["web", "cli", "demo"], default="web", 
                       help="Interface mode (default: web)")
    parser.add_argument("--load-sample", action="store_true", 
                       help="Load sample data on startup")
    parser.add_argument("--setup", action="store_true",
                       help="Run initial setup only")
    parser.add_argument("--demo-validation", action="store_true",
                       help="Demonstrate validation system")
    
    args = parser.parse_args()
    
    print("🔧 Enhanced Electronics Support Knowledge Base")
    print("=" * 60)
    print("✨ Features: Validation, Feedback Learning, Manual Knowledge")
    
    # Setup environment
    if not setup_environment():
        print("Please configure your .env file and run again.")
        return
    
    if args.demo_validation:
        demonstrate_validation()
        return
    
    # Initialize enhanced system
    enhanced_engine = initialize_enhanced_system(load_sample=args.load_sample)
    
    if args.setup:
        print("✅ Enhanced setup complete!")
        return
    
    # Run interface
    if args.mode == "cli":
        run_enhanced_cli_mode(enhanced_engine)
    elif args.mode == "demo":
        demonstrate_validation()
    else:
        run_enhanced_web_interface()

if __name__ == "__main__":
    import datetime
    main() 