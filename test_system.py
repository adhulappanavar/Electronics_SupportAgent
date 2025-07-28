#!/usr/bin/env python3
"""
Test script to demonstrate the RAG Knowledge Base functionality
"""

from database.lancedb_manager import LanceDBManager
from processors.document_processor import DocumentProcessor
from sample_data.create_sample_data import create_sample_data

def test_system():
    print("🔧 RAG Knowledge Base - System Test")
    print("=" * 50)
    
    # 1. Initialize components
    print("\n1. 🚀 Initializing components...")
    db_manager = LanceDBManager()
    processor = DocumentProcessor()
    
    # 2. Create and process sample data
    print("\n2. 📁 Creating sample data...")
    sample_dir = create_sample_data()
    
    print("\n3. 📄 Processing documents...")
    documents = processor.process_directory(str(sample_dir))
    print(f"   Processed {len(documents)} document chunks")
    
    # 4. Add to vector database
    print("\n4. 💾 Adding to vector database...")
    success = db_manager.add_documents(documents)
    if success:
        print("   ✅ Documents added successfully")
    else:
        print("   ❌ Failed to add documents")
    
    # 5. Test search functionality
    print("\n5. 🔍 Testing search functionality...")
    test_queries = [
        "Samsung TV WiFi connection",
        "LG washing machine error codes", 
        "refrigerator temperature settings",
        "speaker Bluetooth pairing"
    ]
    
    for query in test_queries:
        print(f"\n   Query: '{query}'")
        results = db_manager.search(query, limit=2)
        if results:
            for i, result in enumerate(results, 1):
                brand = result.get('brand', 'Unknown')
                product = result.get('product_category', 'Unknown')
                doc_type = result.get('document_type', 'Unknown')
                content_preview = result['content'][:100] + "..."
                print(f"   {i}. {brand} {product} {doc_type}")
                print(f"      {content_preview}")
        else:
            print("      No results found")
    
    # 6. Database stats
    print(f"\n6. 📊 Database Stats:")
    count = db_manager.get_document_count()
    print(f"   Total document chunks: {count}")
    
    print("\n✅ System test completed!")
    print("\n🌐 To use the web interface:")
    print("   python main.py --mode web")
    print("\n💬 To use CLI mode:")
    print("   python main.py --mode cli")

if __name__ == "__main__":
    test_system() 