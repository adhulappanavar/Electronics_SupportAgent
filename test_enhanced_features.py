#!/usr/bin/env python3
"""
Comprehensive test of enhanced RAG features:
1. Answer validation
2. Feedback management 
3. Manual knowledge integration
"""

from rag_engine.enhanced_query_engine import EnhancedQueryEngine
from feedback.feedback_manager import FeedbackManager
from database.manual_knowledge_manager import ManualKnowledgeManager
from validation.answer_validator import AnswerValidator
from sample_data.create_sample_data import create_sample_data
from datetime import datetime

def test_enhanced_features():
    print("🧪 Enhanced RAG Features Test")
    print("=" * 60)
    
    # Step 1: Initialize all components
    print("\n1. 🚀 Initializing Enhanced Components...")
    enhanced_engine = EnhancedQueryEngine()
    feedback_manager = FeedbackManager()
    manual_knowledge = ManualKnowledgeManager()
    validator = AnswerValidator()
    print("✅ All components initialized")
    
    # Step 2: Load sample data
    print("\n2. 📁 Loading Sample Data...")
    sample_dir = create_sample_data()
    
    # Check if we need to load data
    doc_count = enhanced_engine.db_manager.get_document_count()
    if doc_count == 0:
        from processors.document_processor import DocumentProcessor
        processor = DocumentProcessor()
        docs = processor.process_directory(str(sample_dir))
        enhanced_engine.db_manager.add_documents(docs)
        print(f"✅ Loaded {len(docs)} document chunks")
    else:
        print(f"✅ Using existing {doc_count} documents")
    
    # Step 3: Test basic enhanced query
    print("\n3. 🔍 Testing Enhanced Query (Original Knowledge Only)...")
    test_query = "Samsung TV WiFi connection problems"
    result = enhanced_engine.query_with_validation(test_query, validation_enabled=True)
    
    print(f"Query: {test_query}")
    print(f"Response: {result['response'][:200]}...")
    print(f"Confidence: {result['confidence_indicators']['overall_confidence']:.1%}")
    print(f"Validation Score: {result['validation']['overall_score']:.1%}")
    print(f"Valid: {'✅' if result['validation']['is_valid'] else '❌'}")
    print(f"Sources: {result['total_sources']} (Original: {len(result['original_sources'])}, Manual: {len(result['manual_sources'])})")
    
    # Step 4: Test feedback logging
    print("\n4. 📝 Testing Feedback Logging...")
    feedback_id = feedback_manager.log_unsatisfactory_answer(
        user_question="Samsung TV won't turn on",
        original_answer="Check the power cable and try different outlet.",
        original_sources=[{"brand": "Samsung", "product_category": "TV", "document_type": "FAQ"}],
        manual_solution="The issue was with the Samsung TV's internal power supply. Customer needed to unplug for 60 seconds, then hold power button for 30 seconds while unplugged to drain residual power. After plugging back in, TV worked normally.",
        support_agent="Agent Smith",
        feedback_details={
            'feedback_type': 'incomplete',
            'issue_category': 'power_issues',
            'resolution_method': 'phone_support',
            'customer_satisfaction': 'very_satisfied',
            'tags': ['power_drain', 'verified_solution'],
            'notes': 'Common issue not covered in standard documentation'
        }
    )
    print(f"✅ Feedback logged with ID: {feedback_id}")
    
    # Step 5: Test manual knowledge addition
    print("\n5. 🔧 Testing Manual Knowledge Integration...")
    feedback_id_2 = manual_knowledge.add_real_time_feedback(
        user_question="LG washing machine makes loud noise during spin cycle",
        original_answer="Check if the load is balanced.",
        manual_solution="After checking load balance, the issue was worn suspension rods. Customer was advised to contact local service center for replacement. Temporary solution: reduce spin speed to 800 RPM and use shorter cycles until repair.",
        support_agent="Tech Specialist Jane",
        metadata={
            'brand': 'LG',
            'product_category': 'Washing Machine',
            'issue_category': 'mechanical_noise',
            'resolution_method': 'escalation',
            'customer_satisfaction': 'satisfied',
            'tags': ['hardware_issue', 'service_required'],
            'timestamp': datetime.now().isoformat(),
            'original_sources': []
        }
    )
    print(f"✅ Manual knowledge added with ID: {feedback_id_2}")
    
    # Step 6: Test enhanced query with manual knowledge
    print("\n6. 🔍 Testing Enhanced Query (With Manual Knowledge)...")
    test_query_2 = "Samsung TV power issues not turning on"
    result_2 = enhanced_engine.query_with_validation(test_query_2, validation_enabled=True)
    
    print(f"Query: {test_query_2}")
    print(f"Response: {result_2['response'][:300]}...")
    print(f"Confidence: {result_2['confidence_indicators']['overall_confidence']:.1%}")
    print(f"Has Manual Solutions: {'✅' if result_2['confidence_indicators']['has_manual_solutions'] else '❌'}")
    print(f"Manual Solution Confidence: {result_2['confidence_indicators']['manual_solution_confidence']:.1%}")
    print(f"Sources: {result_2['total_sources']} (Original: {len(result_2['original_sources'])}, Manual: {len(result_2['manual_sources'])})")
    
    if result_2['manual_sources']:
        print("\n🔧 Manual Solutions Found:")
        for i, source in enumerate(result_2['manual_sources'], 1):
            print(f"  {i}. Issue: {source['issue_category']}")
            print(f"     Confidence: {source['confidence_score']:.1%}")
            print(f"     Method: {source['resolution_method']}")
    
    # Step 7: Test validation system
    print("\n7. 📊 Testing Validation System...")
    validation_tests = [
        {
            "question": "How to fix Samsung TV that won't turn on?",
            "good_answer": "First, ensure the power cable is securely connected. Try a different power outlet. If the power LED is not lit, unplug the TV for 60 seconds, then hold the power button for 30 seconds while unplugged to drain residual power. Plug back in and try turning on with the remote. If issue persists, contact Samsung support.",
            "bad_answer": "Try plugging it in."
        }
    ]
    
    for test in validation_tests:
        print(f"\nQuestion: {test['question']}")
        
        # Test good answer
        good_validation = validator.validate_answer(
            test['question'], 
            test['good_answer'], 
            [{"brand": "Samsung", "product_category": "TV", "document_type": "FAQ"}]
        )
        
        # Test bad answer
        bad_validation = validator.validate_answer(
            test['question'], 
            test['bad_answer'], 
            [{"brand": "Samsung", "product_category": "TV", "document_type": "FAQ"}]
        )
        
        print(f"Good Answer Score: {good_validation['overall_score']:.1%} {'✅' if good_validation['is_valid'] else '❌'}")
        print(f"Bad Answer Score: {bad_validation['overall_score']:.1%} {'✅' if bad_validation['is_valid'] else '❌'}")
        
        if bad_validation['suggestions']:
            print(f"Bad Answer Suggestions: {'; '.join(bad_validation['suggestions'])}")
    
    # Step 8: Test feedback analytics
    print("\n8. 📈 Testing Feedback Analytics...")
    feedback_stats = feedback_manager.get_feedback_statistics()
    manual_stats = manual_knowledge.get_manual_knowledge_stats()
    
    print(f"Total Feedback Entries: {feedback_stats.get('total_feedback_entries', 0)}")
    print(f"Manual Knowledge Entries: {manual_stats.get('total_manual_entries', 0)}")
    print(f"High Confidence Solutions: {manual_stats.get('high_confidence_entries', 0)}")
    
    if feedback_stats.get('feedback_by_type'):
        print("Feedback by Type:", feedback_stats['feedback_by_type'])
    
    # Step 9: Test search similar issues
    print("\n9. 🔍 Testing Similar Issues Search...")
    similar_issues = feedback_manager.search_similar_issues("TV power problems", limit=3)
    print(f"Found {len(similar_issues)} similar issues for 'TV power problems'")
    
    for issue in similar_issues:
        print(f"  - {issue['question'][:60]}... (Score: {issue['relevance_score']:.2f})")
    
    # Step 10: Generate comprehensive stats
    print("\n10. 📊 Comprehensive System Stats...")
    comprehensive_stats = enhanced_engine.get_comprehensive_stats()
    
    print("System Status:")
    print(f"  Original Documents: {comprehensive_stats['original_knowledge']['document_count']}")
    print(f"  Manual Solutions: {comprehensive_stats['manual_knowledge'].get('total_manual_entries', 0)}")
    print(f"  Validation Available: {'✅' if comprehensive_stats['validation_available'] else '❌'}")
    print(f"  OpenAI Available: {'✅' if comprehensive_stats['openai_available'] else '❌'}")
    print(f"  Cognee Available: {'✅' if comprehensive_stats['cognee_available'] else '❌'}")
    
    print("\n🎉 Enhanced Features Test Complete!")
    print("\n✨ Key Features Demonstrated:")
    print("  ✅ Answer validation with scoring")
    print("  ✅ Feedback logging to CSV")
    print("  ✅ Manual knowledge integration")
    print("  ✅ Enhanced query engine with dual knowledge sources")
    print("  ✅ Confidence scoring and indicators")
    print("  ✅ Similar issues search")
    print("  ✅ Comprehensive analytics")
    
    print(f"\n📁 Data Files Created:")
    print(f"  📄 feedback_data/feedback_log.csv - Feedback tracking")
    print(f"  🗃️  manual_knowledge_db/ - Manual solutions database")
    print(f"  📊 sample_data/ - Sample SOPs and FAQs")

if __name__ == "__main__":
    test_enhanced_features() 