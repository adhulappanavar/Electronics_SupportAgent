#!/usr/bin/env python3
"""
Main Application - Cognee-Enhanced RAG System
Properly uses Cognee as AI memory engine with LanceDB backend
"""

import asyncio
import argparse
from pathlib import Path
from rag_engine.cognee_enhanced_engine import CogneeEnhancedRAGEngine

async def initialize_system():
    """Initialize the Cognee-enhanced RAG system"""
    print("🚀 Initializing Cognee-Enhanced RAG Knowledge Base")
    print("=" * 50)
    
    # Initialize the enhanced engine
    engine = CogneeEnhancedRAGEngine()
    
    # Get system status
    status = engine.get_system_status()
    print("\n📊 System Status:")
    print(f"   System Type: {status.get('system_type', 'Unknown')}")
    print(f"   AI Memory: {status.get('capabilities', {}).get('ai_memory', '❌')}")
    print(f"   Knowledge Graphs: {status.get('capabilities', {}).get('knowledge_graphs', '❌')}")
    print(f"   Manual Learning: {status.get('capabilities', {}).get('manual_learning', '❌')}")
    
    return engine

async def process_sample_documents(engine):
    """Process sample documents into Cognee's AI memory"""
    print("\n🧠 Processing Documents into AI Memory")
    print("=" * 40)
    
    # Get sample document paths
    sample_dir = Path("sample_data")
    if not sample_dir.exists():
        print("❌ Sample data directory not found. Please run create_sample_data.py first.")
        return False
    
    # Collect all sample documents
    documents = []
    for brand_dir in sample_dir.iterdir():
        if brand_dir.is_dir():
            for product_dir in brand_dir.iterdir():
                if product_dir.is_dir():
                    for doc_type_dir in product_dir.iterdir():
                        if doc_type_dir.is_dir():
                            for doc_file in doc_type_dir.glob("*.txt"):
                                documents.append(str(doc_file))
    
    if not documents:
        print("❌ No sample documents found")
        return False
    
    print(f"📄 Found {len(documents)} documents to process")
    
    # Process documents into Cognee's AI memory
    result = await engine.process_documents(documents)
    
    if result.get("success"):
        print("✅ Documents successfully processed into AI memory")
        print(f"   - Files processed: {result.get('files_processed', 0)}")
        print(f"   - Knowledge graph built: {result.get('knowledge_graph_built', False)}")
        print(f"   - Memory system: {result.get('memory_system', 'Unknown')}")
        return True
    else:
        print(f"❌ Error processing documents: {result.get('error')}")
        return False

async def interactive_mode(engine):
    """Interactive chat mode using Cognee AI memory"""
    print("\n💬 Interactive AI Memory Chat")
    print("=" * 35)
    print("Ask questions about your documents. Type 'quit' to exit.")
    print("Examples:")
    print("  - 'Samsung TV won't turn on'")
    print("  - 'How to connect LG fridge to WiFi?'")
    print("  - 'Washing machine error codes'")
    print()
    
    while True:
        try:
            query = input("You: ").strip()
            
            if query.lower() in ['quit', 'exit', 'q']:
                break
            
            if not query:
                continue
            
            print("\n🧠 Querying AI memory system...")
            
            # Query using Cognee's AI memory
            response = await engine.intelligent_query(
                query, 
                context=None,  # Could add brand/product detection here
                use_validation=True
            )
            
            # Display response
            print(f"\n🤖 AI Memory Response:")
            print("-" * 30)
            print(response.get("answer", "No response available"))
            
            # Show additional info
            if response.get("ai_memory_used"):
                print(f"\n🧠 AI Memory: ✅ Used")
            if response.get("manual_knowledge_used"):
                print(f"📚 Manual Knowledge: ✅ Used (Human-validated)")
            
            if response.get("source_breakdown"):
                breakdown = response["source_breakdown"]
                print(f"\n📊 Sources:")
                print(f"   - Manual solutions: {breakdown.get('manual_solutions', 0)}")
                print(f"   - AI memory results: {breakdown.get('ai_memory_results', 0)}")
                print(f"   - Total sources: {breakdown.get('total_sources', 0)}")
            
            if response.get("confidence_score"):
                confidence = response["confidence_score"]
                print(f"\n🎯 Confidence: {confidence:.1%}")
            
            if response.get("validation"):
                validation = response["validation"]
                print(f"\n✅ Validation Score: {validation.get('overall_score', 0):.1%}")
            
            print("\n" + "="*50)
            
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")
    
    print("\n👋 Goodbye!")

async def demo_mode(engine):
    """Demo mode showing Cognee's AI memory capabilities"""
    print("\n🎭 Demo Mode - AI Memory Capabilities")
    print("=" * 40)
    
    # Demo queries that show different capabilities
    demo_queries = [
        {
            "query": "Samsung TV won't turn on",
            "description": "Testing manual knowledge priority"
        },
        {
            "query": "How to setup a smart TV?", 
            "description": "Testing AI memory understanding"
        },
        {
            "query": "Bluetooth speaker pairing issues",
            "description": "Testing cross-product knowledge"
        }
    ]
    
    for i, demo in enumerate(demo_queries, 1):
        print(f"\n📝 Demo Query {i}: {demo['description']}")
        print(f"Question: '{demo['query']}'")
        
        response = await engine.intelligent_query(demo["query"], use_validation=True)
        
        print(f"\n🤖 Response: {response.get('answer', 'No response')[:200]}...")
        
        # Show what systems were used
        systems_used = []
        if response.get("ai_memory_used"):
            systems_used.append("🧠 AI Memory")
        if response.get("manual_knowledge_used"):
            systems_used.append("📚 Manual Knowledge")
        
        if systems_used:
            print(f"🔍 Systems Used: {', '.join(systems_used)}")
        
        print(f"🎯 Confidence: {response.get('confidence_score', 0):.1%}")
        print("-" * 40)

async def main():
    """Main application entry point"""
    parser = argparse.ArgumentParser(description="Cognee-Enhanced RAG Knowledge Base")
    parser.add_argument("--mode", choices=["init", "interactive", "demo", "web"], 
                       default="init", help="Application mode")
    parser.add_argument("--process-docs", action="store_true", 
                       help="Process sample documents into AI memory")
    parser.add_argument("--port", type=int, default=8504, 
                       help="Port for web interface")
    
    args = parser.parse_args()
    
    try:
        # Initialize system
        engine = await initialize_system()
        
        # Process documents if requested
        if args.process_docs or args.mode == "init":
            success = await process_sample_documents(engine)
            if not success and args.mode == "init":
                print("⚠️ Document processing failed, but continuing...")
        
        # Run specified mode
        if args.mode == "interactive":
            await interactive_mode(engine)
        elif args.mode == "demo":
            await demo_mode(engine)
        elif args.mode == "web":
            print(f"\n🌐 Starting web interface on port {args.port}...")
            print("Note: You'll need to update the Streamlit app to use CogneeEnhancedRAGEngine")
            print(f"Run: streamlit run chat_interface/enhanced_streamlit_app.py --server.port {args.port}")
        else:
            print("\n✅ System initialized successfully!")
            print("\nNext steps:")
            print("  - Interactive mode: python main_cognee_enhanced.py --mode interactive")
            print("  - Demo mode: python main_cognee_enhanced.py --mode demo")
            print("  - Web interface: python main_cognee_enhanced.py --mode web")
            print("  - Process documents: python main_cognee_enhanced.py --process-docs")
    
    except Exception as e:
        print(f"\n❌ Application error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    asyncio.run(main()) 