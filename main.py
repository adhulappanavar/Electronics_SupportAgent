#!/usr/bin/env python3
"""
RAG Knowledge Base for Electronics Support
Main application entry point
"""

import os
import sys
import argparse
from pathlib import Path
from typing import Optional

from database.lancedb_manager import LanceDBManager
from processors.document_processor import DocumentProcessor
from rag_engine.query_engine import RAGQueryEngine
from sample_data.create_sample_data import create_sample_data

def setup_environment():
    """Setup environment and check requirements"""
    # Check if .env exists
    env_file = Path(".env")
    if not env_file.exists():
        print("⚠️  No .env file found. Creating from template...")
        print("Please edit .env file with your API keys before running.")
        
        # Copy from template
        template_file = Path(".env.example")
        if template_file.exists():
            import shutil
            shutil.copy(template_file, env_file)
            return False
    
    return True

def initialize_knowledge_base(load_sample: bool = False) -> RAGQueryEngine:
    """Initialize the knowledge base"""
    print("🚀 Initializing RAG Knowledge Base...")
    
    # Initialize components
    db_manager = LanceDBManager()
    doc_processor = DocumentProcessor()
    query_engine = RAGQueryEngine()
    
    print("✅ Components initialized successfully")
    
    # Load sample data if requested
    if load_sample:
        print("📁 Creating and loading sample data...")
        sample_dir = create_sample_data()
        
        print("📄 Processing sample documents...")
        documents = doc_processor.process_directory(str(sample_dir))
        
        if documents:
            print(f"💾 Adding {len(documents)} document chunks to database...")
            success = db_manager.add_documents(documents)
            if success:
                print("✅ Sample data loaded successfully!")
            else:
                print("❌ Failed to load sample data")
        else:
            print("⚠️  No documents found in sample data")
    
    # Print stats
    stats = query_engine.get_stats()
    print(f"\n📊 Knowledge Base Stats:")
    print(f"   Documents: {stats['total_documents']}")
    print(f"   LanceDB: {stats['lancedb_status']}")
    print(f"   OpenAI: {'Available' if stats['openai_available'] else 'Not configured'}")
    
    return query_engine

def run_cli_mode(query_engine: RAGQueryEngine):
    """Run in command-line interface mode"""
    print("\n💬 CLI Mode - Type 'quit' to exit")
    print("Example queries:")
    print("  - How do I fix my Samsung TV that won't turn on?")
    print("  - What's the procedure for cleaning LG refrigerator?")
    print("  - Samsung washing machine error codes")
    
    while True:
        try:
            question = input("\n🤔 Your question: ").strip()
            
            if question.lower() in ['quit', 'exit', 'q']:
                break
            
            if not question:
                continue
            
            print("🔍 Searching knowledge base...")
            result = query_engine.query(question)
            
            print(f"\n🤖 Answer:")
            print(result['response'])
            
            if result['sources']:
                print(f"\n📚 Sources ({len(result['sources'])} documents):")
                for i, source in enumerate(result['sources'][:3], 1):
                    print(f"  {i}. {source['brand']} {source['product_category']} - {source['document_type']}")
                    print(f"     📄 {source['file_name']}")
        
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"❌ Error: {e}")
    
    print("\n👋 Goodbye!")

def run_web_interface():
    """Launch the Streamlit web interface"""
    print("🌐 Launching web interface...")
    os.system("streamlit run chat_interface/streamlit_app.py")

def main():
    """Main application entry point"""
    parser = argparse.ArgumentParser(description="RAG Knowledge Base for Electronics Support")
    parser.add_argument("--mode", choices=["web", "cli"], default="web", 
                       help="Interface mode (default: web)")
    parser.add_argument("--load-sample", action="store_true", 
                       help="Load sample data on startup")
    parser.add_argument("--setup", action="store_true",
                       help="Run initial setup only")
    
    args = parser.parse_args()
    
    print("🔧 Electronics Support Knowledge Base")
    print("=====================================")
    
    # Setup environment
    if not setup_environment():
        print("Please configure your .env file and run again.")
        return
    
    # Initialize knowledge base
    query_engine = initialize_knowledge_base(load_sample=args.load_sample)
    
    if args.setup:
        print("✅ Setup complete!")
        return
    
    # Run interface
    if args.mode == "cli":
        run_cli_mode(query_engine)
    else:
        run_web_interface()

if __name__ == "__main__":
    main() 