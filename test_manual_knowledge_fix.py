#!/usr/bin/env python3
"""
Test script to verify manual knowledge creation is working properly
after fixing the LanceDB API issue.
"""

import sys
import os
from datetime import datetime

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database.manual_knowledge_manager import ManualKnowledgeManager
from feedback.feedback_manager import FeedbackManager

def test_manual_knowledge_creation():
    """Test that manual knowledge is created properly from feedback"""
    
    print("🧪 Testing Manual Knowledge Creation Fix")
    print("=" * 50)
    
    # Initialize managers
    print("📚 Initializing Manual Knowledge Manager...")
    manual_knowledge = ManualKnowledgeManager()
    
    # Get initial stats
    initial_stats = manual_knowledge.get_manual_knowledge_stats()
    initial_count = initial_stats.get('total_manual_entries', 0)
    print(f"📊 Initial manual knowledge entries: {initial_count}")
    
    # Create test feedback with satisfied customer
    print("\n📝 Creating test feedback with satisfied customer...")
    
    test_question = "Samsung TV screen flickering after firmware update"
    test_original_answer = "Try unplugging the TV for 30 seconds"
    test_manual_solution = """Specific fix for Samsung TV flickering after firmware update:
    1. Go to Settings > Support > Device Care > Self Diagnosis
    2. Run Picture Test to confirm issue
    3. Navigate to Settings > Picture > Expert Settings
    4. Change Auto Motion Plus from 'Auto' to 'Off'
    5. Set Judder Reduction to 0
    6. Set Blur Reduction to 0
    7. Restart TV to apply changes
    
    This resolves firmware-related motion processing conflicts causing flickering."""
    
    test_agent = "Test Agent (Fix Verification)"
    
    # Create metadata with satisfied customer
    test_metadata = {
        'brand': 'Samsung',
        'product_category': 'TV',
        'issue_category': 'display',
        'resolution_method': 'phone',
        'customer_satisfaction': 'very_satisfied',  # This should trigger manual knowledge creation
        'tags': ['firmware', 'flickering', 'motion_plus', 'verified_fix'],
        'notes': 'Customer confirmed this completely resolved the issue',
        'feedback_type': 'manual_correction',
        'timestamp': datetime.now().isoformat(),
        'original_sources': []
    }
    
    # Add real-time feedback
    print("🔄 Adding real-time feedback...")
    feedback_id = manual_knowledge.add_real_time_feedback(
        user_question=test_question,
        original_answer=test_original_answer,
        manual_solution=test_manual_solution,
        support_agent=test_agent,
        metadata=test_metadata
    )
    
    print(f"📋 Feedback ID: {feedback_id}")
    
    # Check if manual knowledge was created
    print("\n🔍 Checking manual knowledge database...")
    updated_stats = manual_knowledge.get_manual_knowledge_stats()
    updated_count = updated_stats.get('total_manual_entries', 0)
    
    print(f"📊 Updated manual knowledge entries: {updated_count}")
    print(f"📈 New entries added: {updated_count - initial_count}")
    
    if updated_count > initial_count:
        print("✅ SUCCESS: Manual knowledge entry was created!")
        
        # Test searching for the new manual knowledge
        print("\n🔍 Testing search for new manual knowledge...")
        search_results = manual_knowledge.search_manual_knowledge(
            query="Samsung TV flickering firmware",
            limit=5
        )
        
        print(f"🔍 Search returned {len(search_results)} results")
        
        # Look for our specific entry
        found_entry = None
        for result in search_results:
            if result['id'] == feedback_id:
                found_entry = result
                break
        
        if found_entry:
            print("✅ SUCCESS: Manual knowledge entry is searchable!")
            print(f"   📋 ID: {found_entry['id']}")
            print(f"   🎯 Confidence: {found_entry['confidence_score']:.2f}")
            print(f"   📝 Solution preview: {found_entry['solution'][:100]}...")
        else:
            print("⚠️ WARNING: Manual knowledge entry exists but not found in search")
    else:
        print("❌ FAILURE: Manual knowledge entry was NOT created!")
        print("🔍 Possible issues:")
        print("   - Customer satisfaction condition not met")
        print("   - Error in _add_manual_entry method")
        print("   - Database connectivity issue")
    
    # Test with unsatisfied customer (should not create manual knowledge)
    print("\n📝 Testing with unsatisfied customer (should NOT create manual knowledge)...")
    
    test_metadata_unsatisfied = test_metadata.copy()
    test_metadata_unsatisfied['customer_satisfaction'] = 'dissatisfied'
    test_metadata_unsatisfied['notes'] = 'Customer still experiencing issues'
    
    feedback_id_2 = manual_knowledge.add_real_time_feedback(
        user_question="Another test question",
        original_answer="Another answer",
        manual_solution="Another solution",
        support_agent=test_agent,
        metadata=test_metadata_unsatisfied
    )
    
    # Check that manual knowledge was NOT created
    final_stats = manual_knowledge.get_manual_knowledge_stats()
    final_count = final_stats.get('total_manual_entries', 0)
    
    if final_count == updated_count:
        print("✅ SUCCESS: Unsatisfied customer feedback correctly did NOT create manual knowledge")
    else:
        print("❌ FAILURE: Unsatisfied customer feedback incorrectly created manual knowledge")
    
    # Display final summary
    print("\n📊 Final Summary:")
    print(f"   🔢 Total manual knowledge entries: {final_count}")
    print(f"   📈 Entries added in this test: {final_count - initial_count}")
    print(f"   ✅ Expected: 1 entry added (only satisfied customer)")
    
    if final_count - initial_count == 1:
        print("🎉 TEST PASSED: Manual knowledge creation is working correctly!")
        return True
    else:
        print("❌ TEST FAILED: Manual knowledge creation needs further investigation")
        return False

if __name__ == "__main__":
    success = test_manual_knowledge_creation()
    sys.exit(0 if success else 1) 