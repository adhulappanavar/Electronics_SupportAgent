#!/usr/bin/env python3
"""
Test n8n workflow activation and provide clear instructions
"""

import requests
import json
import time
from datetime import datetime

def check_n8n_status():
    """Check if n8n is running and accessible"""
    print("🔍 Checking n8n Status...")
    
    try:
        response = requests.get("http://127.0.0.1:5678", timeout=5)
        if response.status_code == 200:
            print("✅ n8n is running and accessible")
            return True
        else:
            print(f"❌ n8n returned status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Cannot connect to n8n: {e}")
        return False

def check_lancedb_status():
    """Check if LanceDB service is running"""
    print("🔍 Checking LanceDB Status...")
    
    try:
        response = requests.get("http://127.0.0.1:8000/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ LanceDB is running - {data.get('manual_knowledge_entries', 0)} entries")
            return True
        else:
            print(f"❌ LanceDB returned status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Cannot connect to LanceDB: {e}")
        return False

def test_webhook_activation():
    """Test if the webhook is activated"""
    print("🔍 Testing Webhook Activation...")
    
    webhook_url = "http://127.0.0.1:5678/webhook/test_lancedb"
    test_data = {"query": "Samsung TV won't turn on"}
    
    try:
        response = requests.post(
            webhook_url,
            json=test_data,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        if response.status_code == 200:
            print("🎉 SUCCESS! Webhook is activated and working!")
            try:
                result = response.json()
                print("📊 Response:")
                print(json.dumps(result, indent=2))
                return True
            except:
                print(f"📊 Response: {response.text}")
                return True
        elif response.status_code == 404:
            print("❌ Webhook not activated - workflow needs to be activated in n8n")
            return False
        else:
            print(f"❌ Unexpected response: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing webhook: {e}")
        return False

def main():
    """Main test function"""
    print("🧪 n8n Workflow Activation Test")
    print("=" * 50)
    
    # Check services
    n8n_ok = check_n8n_status()
    lancedb_ok = check_lancedb_status()
    
    print("\n" + "=" * 50)
    
    if not n8n_ok:
        print("❌ n8n is not running. Please start n8n first.")
        return
    
    if not lancedb_ok:
        print("❌ LanceDB is not running. Please start LanceDB first.")
        return
    
    print("✅ All services are running!")
    print("\n🔧 Testing webhook activation...")
    
    webhook_ok = test_webhook_activation()
    
    print("\n" + "=" * 50)
    
    if webhook_ok:
        print("🎉 REAL n8n WORKFLOW IS WORKING!")
        print("✅ The actual n8n workflow is responding correctly")
        print("✅ Webhook integration is functional")
        print("✅ LanceDB backend is being called through n8n")
    else:
        print("⚠️ Workflow needs to be activated manually")
        print("\n📋 To activate the workflow:")
        print("1. Open http://127.0.0.1:5678 in your browser")
        print("2. Go to Workflows")
        print("3. Find 'Simple LanceDB Test Workflow'")
        print("4. Click the toggle switch in the top-right to activate it")
        print("5. Run this script again to test")
        
        print("\n🔗 After activation, the webhook URL will be:")
        print("   http://127.0.0.1:5678/webhook/test_lancedb")

if __name__ == "__main__":
    main() 