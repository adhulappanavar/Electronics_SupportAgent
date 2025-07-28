#!/usr/bin/env python3
"""
Test script to populate Cognee with sample data and verify everything works
"""

import sys
import os
import asyncio
from pathlib import Path
from datetime import datetime

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from cognee_integration.cognee_manager import CogneeManager

def create_test_documents():
    """Create sample documents for testing Cognee"""
    
    # Create test documents directory
    test_dir = Path("test_cognee_documents")
    test_dir.mkdir(exist_ok=True)
    
    # Sample documents content
    documents = {
        "samsung_tv_troubleshooting.txt": """
Samsung TV Troubleshooting Guide

Power Issues:
1. Check power cable connection
2. Ensure power outlet is working
3. Try different power outlet
4. Check for standby LED indicator
5. Perform soft reset by unplugging for 60 seconds

Display Problems:
1. Check HDMI cable connections
2. Try different HDMI port
3. Adjust picture settings
4. Check for loose connections
5. Update TV firmware

Audio Issues:
1. Check volume settings
2. Verify audio output selection
3. Test with different audio source
4. Check speaker connections
5. Reset audio settings to default

Smart TV Features:
1. Ensure internet connection is stable
2. Update Smart Hub software
3. Clear app cache
4. Reset Smart Hub if needed
5. Check Samsung account settings
""",

        "lg_refrigerator_maintenance.txt": """
LG Refrigerator Maintenance Guide

Temperature Control:
1. Set refrigerator to 37°F (3°C)
2. Set freezer to 0°F (-18°C)
3. Allow 24 hours for temperature stabilization
4. Check door seals regularly
5. Keep vents unobstructed

Ice Maker Troubleshooting:
1. Ensure ice maker is turned ON
2. Check water supply connection
3. Replace water filter every 6 months
4. Clear ice blockages carefully
5. Reset ice maker if needed

Energy Efficiency:
1. Keep refrigerator 75% full for optimal efficiency
2. Clean condenser coils every 6 months
3. Check door seals for air leaks
4. Avoid frequent door opening
5. Set appropriate temperatures

Common Error Codes:
- Er IF: Ice Fan error - contact service
- Er FF: Freezer Fan error - check for obstructions  
- Er CF: Communication error - unplug and restart
- Er dH: Defrost Heater error - schedule service
""",

        "samsung_washing_machine_guide.txt": """
Samsung Washing Machine User Guide

Loading Instructions:
1. Sort clothes by color and fabric type
2. Do not overload the machine
3. Distribute clothes evenly in drum
4. Close door securely before starting
5. Select appropriate wash cycle

Cycle Selection:
- Normal: For everyday cotton items
- Quick Wash: For lightly soiled items (15-30 min)
- Delicate: For fine fabrics and lingerie
- Heavy Duty: For heavily soiled items
- Eco Wash: Energy-efficient cleaning

Maintenance:
1. Clean door seal monthly
2. Run cleaning cycle monthly with washing machine cleaner
3. Leave door open after use to air dry
4. Clean lint filter regularly
5. Check water hoses for leaks

Error Codes:
- UE: Unbalanced load - redistribute clothes
- 5E: Drain issue - check drain hose
- 4E: Water supply issue - check water valves
- dE: Door error - ensure door is properly closed
""",

        "lg_speaker_setup.txt": """
LG Speaker Setup and Configuration

Initial Setup:
1. Unbox speaker and check contents
2. Connect power adapter
3. Download LG Wi-Fi Speaker app
4. Press and hold Wi-Fi button for 5 seconds
5. Follow app instructions for network setup

Bluetooth Pairing:
1. Press Bluetooth button on speaker
2. Enable Bluetooth on your device
3. Select LG speaker from device list
4. Confirm pairing when prompted
5. Play test audio to verify connection

Wi-Fi Connection:
1. Ensure speaker is in pairing mode
2. Open LG Wi-Fi Speaker app
3. Select "Add Speaker"
4. Choose your Wi-Fi network
5. Enter Wi-Fi password when prompted

Sound Optimization:
1. Position speaker away from walls
2. Adjust EQ settings in app
3. Enable Sound Sync for TV connection
4. Test different audio modes
5. Update speaker firmware regularly

Troubleshooting:
- No sound: Check volume levels and connections
- Connection drops: Move closer to router
- App issues: Update app to latest version
- Reset: Hold power button for 10 seconds
"""
    }
    
    # Write documents to files
    created_files = []
    for filename, content in documents.items():
        file_path = test_dir / filename
        with open(file_path, 'w') as f:
            f.write(content)
        created_files.append(str(file_path))
        print(f"📄 Created: {file_path}")
    
    return created_files

def test_cognee_population():
    """Test populating Cognee with documents and verify the data"""
    
    print("🧪 Testing Cognee Data Population")
    print("=" * 50)
    
    # Initialize Cognee manager
    print("🔧 Initializing Cognee Manager...")
    cognee_manager = CogneeManager()
    
    # Get initial status
    print("\n📊 Initial Cognee Status:")
    initial_status = cognee_manager.get_status()
    print(f"   Version: {initial_status.get('cognee_version', 'unknown')}")
    
    initial_stats = cognee_manager.get_usage_statistics()
    initial_docs = initial_stats.get('documents', {}).get('total_documents', 0)
    print(f"   Documents: {initial_docs}")
    
    # Create test documents
    print("\n📝 Creating Test Documents...")
    test_files = create_test_documents()
    print(f"   Created {len(test_files)} test documents")
    
    # Add documents to Cognee
    print("\n🔄 Adding Documents to Cognee...")
    try:
        success = cognee_manager.add_documents(test_files)
        if success:
            print("✅ Documents successfully added to Cognee!")
        else:
            print("❌ Failed to add documents to Cognee")
            return False
    except Exception as e:
        print(f"❌ Error adding documents: {e}")
        return False
    
    # Wait a moment for processing
    print("\n⏳ Waiting for Cognee to process documents...")
    import time
    time.sleep(3)
    
    # Verify documents were added
    print("\n🔍 Verifying Documents in Cognee...")
    updated_stats = cognee_manager.get_usage_statistics()
    updated_docs = updated_stats.get('documents', {}).get('total_documents', 0)
    
    print(f"   Documents before: {initial_docs}")
    print(f"   Documents after: {updated_docs}")
    print(f"   Documents added: {updated_docs - initial_docs}")
    
    if updated_docs > initial_docs:
        print("✅ Documents successfully populated in Cognee!")
    else:
        print("⚠️ Document count unchanged - checking database details...")
    
    # Check database details
    print("\n🗄️ Database Information:")
    db_info = cognee_manager._get_database_info()
    
    for db_type, info in db_info.items():
        if info and 'size_mb' in info:
            print(f"   {db_type.capitalize()} DB: {info['size_mb']} MB")
    
    # Test queries
    print("\n🔍 Testing Queries...")
    test_queries = [
        "Samsung TV troubleshooting",
        "LG refrigerator maintenance", 
        "washing machine error codes",
        "speaker setup instructions"
    ]
    
    query_results = {}
    for query in test_queries:
        print(f"\n   Testing: '{query}'")
        try:
            result = cognee_manager.query(query)
            query_results[query] = result
            if result and "No relevant information found" not in result:
                print(f"   ✅ Result: {result[:100]}...")
            else:
                print(f"   ⚠️ No results found")
        except Exception as e:
            print(f"   ❌ Error: {e}")
            query_results[query] = f"Error: {e}"
    
    # Explore data structure
    print("\n🔬 Exploring Cognee Data Structure...")
    explorer_data = cognee_manager.explore_data()
    
    if 'error' not in explorer_data:
        tables = explorer_data.get('tables', [])
        print(f"   Found {len(tables)} tables in Cognee database")
        
        for table in tables[:5]:  # Show first 5 tables
            print(f"   📋 Table: {table}")
    else:
        print(f"   ❌ Error exploring data: {explorer_data['error']}")
    
    # Final verification
    print("\n📊 Final Verification:")
    final_stats = cognee_manager.get_usage_statistics()
    
    if 'storage' in final_stats:
        storage = final_stats['storage']
        total_size = storage.get('total_size_mb', 0)
        print(f"   Total Storage Used: {total_size} MB")
        
        if total_size > 0:
            print("✅ Cognee has data stored successfully!")
        else:
            print("⚠️ No storage usage detected")
    
    # Summary
    print("\n📋 Test Summary:")
    print(f"   📄 Test Files Created: {len(test_files)}")
    print(f"   🔄 Documents Processed: {'✅ Success' if success else '❌ Failed'}")
    print(f"   📊 Database Tables: {len(tables) if 'tables' in locals() else 'Unknown'}")
    print(f"   🔍 Queries Tested: {len([q for q in query_results.values() if 'Error' not in str(q)])}/{len(test_queries)}")
    
    return True

def cleanup_test_files():
    """Clean up test files"""
    test_dir = Path("test_cognee_documents")
    if test_dir.exists():
        import shutil
        shutil.rmtree(test_dir)
        print(f"🧹 Cleaned up test directory: {test_dir}")

def main():
    """Main test function"""
    try:
        success = test_cognee_population()
        
        if success:
            print("\n🎉 Cognee population test completed!")
            print("\n🔍 You can now verify the data using:")
            print("   python view_cognee_data.py --all")
            print("   Or visit the web interface: http://localhost:8503")
        else:
            print("\n❌ Test failed!")
            
    except Exception as e:
        print(f"\n💥 Test failed with error: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Ask user if they want to keep test files
        try:
            keep_files = input("\n❓ Keep test documents? (y/N): ").lower().strip()
            if keep_files != 'y':
                cleanup_test_files()
        except:
            # If running in non-interactive mode, clean up
            cleanup_test_files()

if __name__ == "__main__":
    main() 