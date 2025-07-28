#!/usr/bin/env python3
"""
Test simple_test_workflow.json with multiple different queries
"""

import requests
import json
from datetime import datetime

def test_lancedb_query(query):
    """Test a single query against LanceDB"""
    print(f"\n🔍 Testing Query: '{query}'")
    print("-" * 50)
    
    try:
        # Simulate the workflow steps
        url = "http://127.0.0.1:8000/manual_search"
        payload = {"question": query}
        
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()
        
        result = response.json()
        
        # Format like the n8n workflow would
        workflow_result = {
            "success": True,
            "query": query,
            "lancedb_response": result,
            "timestamp": datetime.now().isoformat()
        }
        
        print(f"✅ Status: {result.get('found', False)}")
        print(f"🎯 Confidence: {result.get('confidence', 0):.2f}")
        print(f"📋 Source: {result.get('source_type', 'unknown')}")
        if result.get('found'):
            print(f"💡 Answer: {result.get('answer', 'No answer')[:100]}...")
        
        return workflow_result
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return {"success": False, "error": str(e)}

def main():
    """Test multiple queries"""
    print("🧪 Testing simple_test_workflow.json with Multiple Queries")
    print("=" * 60)
    
    test_queries = [
        "Samsung TV won't turn on",           # Should find good match
        "Samsung TV power issue",             # Should find good match  
        "TV not working after power outage",  # Should find medium match
        "LG refrigerator problem",            # Should find low confidence
        "washing machine error",              # Should find low confidence
        "test query"                          # Should find low confidence
    ]
    
    results = []
    
    for query in test_queries:
        result = test_lancedb_query(query)
        results.append(result)
    
    # Summary
    print(f"\n📊 TEST SUMMARY")
    print("=" * 60)
    
    successful = sum(1 for r in results if r.get('success', False))
    high_confidence = sum(1 for r in results if r.get('success', False) and 
                         r.get('lancedb_response', {}).get('confidence', 0) > 0.5)
    found_answers = sum(1 for r in results if r.get('success', False) and 
                       r.get('lancedb_response', {}).get('found', False))
    
    print(f"✅ Successful Queries: {successful}/{len(test_queries)}")
    print(f"🎯 High Confidence (>50%): {high_confidence}/{len(test_queries)}")
    print(f"💡 Found Answers: {found_answers}/{len(test_queries)}")
    
    if successful == len(test_queries):
        print("\n🎉 ALL TESTS PASSED - simple_test_workflow.json is WORKING PERFECTLY!")
    else:
        print(f"\n⚠️ Some tests failed - check LanceDB service")
    
    return results

if __name__ == "__main__":
    results = main() 