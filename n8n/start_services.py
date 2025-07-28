#!/usr/bin/env python3
"""
Startup script for the Enhanced n8n RAG System
Starts both LanceDB and Cognee services with proper monitoring
"""

import subprocess
import time
import requests
import sys
import os
from threading import Thread

def check_port(port):
    """Check if a port is already in use"""
    try:
        response = requests.get(f"http://localhost:{port}/health", timeout=2)
        return response.status_code == 200
    except:
        return False

def start_service(script_name, port, service_name):
    """Start a service and monitor it"""
    print(f"🚀 Starting {service_name} on port {port}...")
    
    if check_port(port):
        print(f"⚠️ Port {port} already in use - {service_name} might already be running")
        return None
    
    try:
        process = subprocess.Popen([
            sys.executable, script_name
        ], cwd=os.path.dirname(os.path.abspath(__file__)))
        
        # Wait a bit for service to start
        time.sleep(3)
        
        # Check if service is healthy
        if check_port(port):
            print(f"✅ {service_name} started successfully on port {port}")
            return process
        else:
            print(f"❌ {service_name} failed to start properly")
            process.terminate()
            return None
            
    except Exception as e:
        print(f"❌ Error starting {service_name}: {e}")
        return None

def monitor_services(processes):
    """Monitor running services"""
    print("\n🔍 Monitoring services (Press Ctrl+C to stop all services)...")
    
    try:
        while True:
            for name, process in processes.items():
                if process and process.poll() is not None:
                    print(f"⚠️ {name} has stopped unexpectedly!")
            
            time.sleep(5)
            
    except KeyboardInterrupt:
        print("\n🛑 Stopping all services...")
        for name, process in processes.items():
            if process:
                print(f"Stopping {name}...")
                process.terminate()
                time.sleep(2)
                if process.poll() is None:
                    process.kill()
        print("✅ All services stopped")

def test_system():
    """Run basic system tests"""
    print("\n🧪 Running system tests...")
    
    tests = [
        ("LanceDB Health", "http://localhost:8000/health"),
        ("Cognee Health", "http://localhost:9000/health"),
        ("LanceDB Stats", "http://localhost:8000/stats"),
        ("Cognee Status", "http://localhost:9000/status")
    ]
    
    for test_name, url in tests:
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                print(f"✅ {test_name}: PASS")
            else:
                print(f"⚠️ {test_name}: FAIL (Status: {response.status_code})")
        except Exception as e:
            print(f"❌ {test_name}: ERROR ({e})")
    
    # Test manual knowledge addition
    print("\n🔧 Testing manual knowledge addition...")
    try:
        test_data = {
            "question": "Test question for system startup",
            "answer": "This is a test answer to verify the system is working",
            "confidence_score": 0.8,
            "brand": "Test",
            "product_category": "System",
            "tags": ["test", "startup"]
        }
        
        response = requests.post(
            "http://localhost:8000/add_manual_knowledge",
            json=test_data,
            timeout=10
        )
        
        if response.status_code == 200:
            print("✅ Manual knowledge addition: PASS")
        else:
            print(f"⚠️ Manual knowledge addition: FAIL (Status: {response.status_code})")
            
    except Exception as e:
        print(f"❌ Manual knowledge test: ERROR ({e})")

def main():
    print("=" * 60)
    print("🧠 Enhanced n8n RAG System Startup")
    print("=" * 60)
    
    # Check Python dependencies
    required_packages = ['fastapi', 'uvicorn', 'lancedb', 'sentence-transformers', 'openai']
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"❌ Missing required packages: {', '.join(missing_packages)}")
        print("Please install them with: pip install " + " ".join(missing_packages))
        return 1
    
    # Start services
    processes = {}
    
    # Start LanceDB service
    lancedb_process = start_service("lance_code.py", 8000, "LanceDB Manual Knowledge Service")
    processes["LanceDB"] = lancedb_process
    
    # Start Cognee service
    cognee_process = start_service("congnee_code.py", 9000, "Cognee Enhanced RAG Service")
    processes["Cognee"] = cognee_process
    
    # Check if both services started
    running_services = [name for name, proc in processes.items() if proc is not None]
    
    if len(running_services) == 0:
        print("❌ No services started successfully. Exiting.")
        return 1
    elif len(running_services) == 1:
        print(f"⚠️ Only {running_services[0]} started. Continuing with partial system...")
    else:
        print("✅ All services started successfully!")
    
    # Wait for services to fully initialize
    print("⏳ Waiting for services to fully initialize...")
    time.sleep(5)
    
    # Run tests
    test_system()
    
    # Print status
    print("\n" + "=" * 60)
    print("🎯 System Status")
    print("=" * 60)
    print("Services running:")
    for name, process in processes.items():
        if process:
            print(f"  ✅ {name}")
        else:
            print(f"  ❌ {name}")
    
    print(f"\n🌐 Available endpoints:")
    if processes["LanceDB"]:
        print(f"  📊 LanceDB API: http://localhost:8000")
        print(f"  📊 LanceDB Health: http://localhost:8000/health")
        print(f"  📊 LanceDB Stats: http://localhost:8000/stats")
    
    if processes["Cognee"]:
        print(f"  🧠 Cognee API: http://localhost:9000")
        print(f"  🧠 Cognee Health: http://localhost:9000/health")
        print(f"  🧠 Cognee Status: http://localhost:9000/status")
    
    print(f"\n📝 Next steps:")
    print(f"  1. Import the workflow.json into your n8n instance")
    print(f"  2. Update the webhook URL in curlcommands.txt")
    print(f"  3. Test the system using the curl commands")
    print(f"  4. Set your OpenAI API key: export OPENAI_API_KEY=your_key")
    
    # Monitor services
    if any(processes.values()):
        monitor_services(processes)
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 