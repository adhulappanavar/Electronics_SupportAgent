#!/usr/bin/env python3
"""
Simulate n8n workflow execution by making direct API calls
This replicates what the simple_test_workflow.json would do
"""

import requests
import json
from datetime import datetime

def simulate_webhook_input():
    """Simulate webhook input data"""
    return {
        "query": "Samsung TV issue",
        "body": {
            "query": "Samsung TV won't turn on"
        }
    }

def extract_query(webhook_data):
    """Extract query from webhook - simulates Extract Query node"""
    try:
        query = webhook_data.get("body", {}).get("query") or webhook_data.get("query", "test query")
        if not query:
            raise ValueError("Query is required")
        
        print(f"📝 Extracted Query: '{query}'")
        return {"question": query}
    except Exception as e:
        print(f"❌ Error extracting query: {e}")
        raise

def lancedb_search(question_data):
    """Call LanceDB search - simulates LanceDB Search node"""
    try:
        url = "http://127.0.0.1:8000/manual_search"
        payload = {"question": question_data["question"]}
        
        print(f"🔍 Searching LanceDB: {payload}")
        
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()
        
        result = response.json()
        print(f"✅ LanceDB Response: {json.dumps(result, indent=2)}")
        return result
    except Exception as e:
        print(f"❌ Error in LanceDB search: {e}")
        raise

def format_response(query, lancedb_response):
    """Format final response - simulates Format Response node"""
    try:
        final_response = {
            "success": True,
            "query": query,
            "lancedb_response": lancedb_response,
            "timestamp": datetime.now().isoformat()
        }
        
        print(f"📦 Formatted Response: {json.dumps(final_response, indent=2)}")
        return final_response
    except Exception as e:
        print(f"❌ Error formatting response: {e}")
        raise

def main():
    """Main workflow simulation"""
    print("🚀 Simulating n8n Simple LanceDB Test Workflow")
    print("=" * 60)
    
    try:
        # Step 1: Webhook Input
        print("\n1️⃣ Webhook Input")
        webhook_data = simulate_webhook_input()
        print(f"   Input: {webhook_data}")
        
        # Step 2: Extract Query
        print("\n2️⃣ Extract Query")
        question_data = extract_query(webhook_data)
        
        # Step 3: LanceDB Search
        print("\n3️⃣ LanceDB Search")
        lancedb_response = lancedb_search(question_data)
        
        # Step 4: Format Response
        print("\n4️⃣ Format Response")
        final_result = format_response(question_data["question"], lancedb_response)
        
        # Step 5: Return Result (Simulated)
        print("\n5️⃣ Return Result")
        print("✅ Workflow executed successfully!")
        print(f"🎯 Final Output: {json.dumps(final_result, indent=2)}")
        
        return final_result
        
    except Exception as e:
        print(f"\n❌ Workflow failed: {e}")
        return {"success": False, "error": str(e)}

if __name__ == "__main__":
    result = main()
    print(f"\n🎉 Workflow Result: {'SUCCESS' if result.get('success') else 'FAILED'}") 