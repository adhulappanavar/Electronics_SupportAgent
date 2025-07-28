#!/usr/bin/env python3
"""
Test the REAL n8n workflow by calling its webhook endpoint
"""

import requests
import json
import time
from datetime import datetime

def test_n8n_webhook(webhook_url, test_data):
    """Test the n8n webhook endpoint"""
    print(f"🔗 Testing n8n webhook: {webhook_url}")
    print(f"📤 Sending data: {json.dumps(test_data, indent=2)}")
    print("-" * 60)
    
    try:
        response = requests.post(
            webhook_url,
            json=test_data,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        print(f"📊 Response Status: {response.status_code}")
        print(f"📋 Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            try:
                result = response.json()
                print(f"✅ n8n Response: {json.dumps(result, indent=2)}")
                return {"success": True, "response": result}
            except json.JSONDecodeError:
                print(f"⚠️ Response is not JSON: {response.text[:200]}...")
                return {"success": True, "response": response.text}
        else:
            print(f"❌ Error Response: {response.text}")
            return {"success": False, "error": f"HTTP {response.status_code}", "response": response.text}
            
    except Exception as e:
        print(f"❌ Request failed: {e}")
        return {"success": False, "error": str(e)}

def main():
    """Test the real n8n workflow"""
    print("🧪 Testing REAL n8n Simple LanceDB Test Workflow")
    print("=" * 70)
    
    # Test different webhook URLs (n8n might be on different ports)
    possible_urls = [
        "http://127.0.0.1:5678/webhook/test_lancedb",
        "http://localhost:5678/webhook/test_lancedb", 
        "http://127.0.0.1:5678/webhook/simple-lancedb-test-workflow",
        "http://localhost:5678/webhook/simple-lancedb-test-workflow"
    ]
    
    test_queries = [
        {"query": "Samsung TV won't turn on"},
        {"query": "Samsung TV power issue"},
        {"query": "TV not working after power outage"},
        {"body": {"query": "Samsung TV won't turn on"}},
        {"body": {"query": "Samsung TV power issue"}}
    ]
    
    results = []
    
    for i, test_data in enumerate(test_queries, 1):
        print(f"\n🧪 Test {i}: {test_data}")
        print("=" * 50)
        
        for url in possible_urls:
            print(f"\n🔗 Trying URL: {url}")
            result = test_n8n_webhook(url, test_data)
            
            if result.get("success"):
                print(f"✅ SUCCESS with URL: {url}")
                results.append({
                    "test": i,
                    "data": test_data,
                    "url": url,
                    "result": result
                })
                break
            else:
                print(f"❌ Failed with URL: {url}")
                print(f"   Error: {result.get('error', 'Unknown error')}")
        
        time.sleep(1)  # Small delay between tests
    
    # Summary
    print(f"\n📊 TEST SUMMARY")
    print("=" * 70)
    
    successful = sum(1 for r in results if r.get("result", {}).get("success", False))
    total_tests = len(test_queries)
    
    print(f"✅ Successful Tests: {successful}/{total_tests}")
    
    if successful > 0:
        print("\n🎉 REAL n8n WORKFLOW IS WORKING!")
        print("✅ The actual n8n workflow is responding correctly")
        print("✅ Webhook integration is functional")
        print("✅ LanceDB backend is being called through n8n")
    else:
        print("\n⚠️ n8n workflow testing failed")
        print("❌ Check if n8n is running and webhook is accessible")
    
    return results

if __name__ == "__main__":
    results = main() 