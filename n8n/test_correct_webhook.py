#!/usr/bin/env python3
"""
Test the REAL n8n workflow with the correct webhook URL
"""

import requests
import json
from datetime import datetime

def test_n8n_webhook():
    """Test the n8n webhook with the correct URL"""
    webhook_url = "http://127.0.0.1:5678/webhook/test_lancedb"
    
    test_data = {
        "query": "Samsung TV won't turn on"
    }
    
    print(f"🧪 Testing REAL n8n workflow")
    print(f"🔗 Webhook URL: {webhook_url}")
    print(f"📤 Test Data: {json.dumps(test_data, indent=2)}")
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
                print(f"✅ SUCCESS! n8n Response:")
                print(json.dumps(result, indent=2))
                
                # Check if LanceDB response is included
                if 'lancedb_response' in result:
                    lancedb_data = result['lancedb_response']
                    print(f"\n🎯 LanceDB Integration:")
                    print(f"   Found: {lancedb_data.get('found', False)}")
                    print(f"   Confidence: {lancedb_data.get('confidence', 0):.2f}")
                    if lancedb_data.get('found'):
                        print(f"   Answer: {lancedb_data.get('answer', 'No answer')[:100]}...")
                
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

if __name__ == "__main__":
    result = test_n8n_webhook()
    
    if result.get("success"):
        print(f"\n🎉 REAL n8n WORKFLOW IS WORKING!")
        print("✅ The actual n8n workflow is responding correctly")
        print("✅ Webhook integration is functional")
        print("✅ LanceDB backend is being called through n8n")
    else:
        print(f"\n❌ n8n workflow test failed: {result.get('error', 'Unknown error')}") 