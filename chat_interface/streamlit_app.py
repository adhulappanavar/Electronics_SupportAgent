import streamlit as st
import sys
import os
from pathlib import Path

# Add parent directory to path to import modules
sys.path.append(str(Path(__file__).parent.parent))

from rag_engine.query_engine import RAGQueryEngine
from database.lancedb_manager import LanceDBManager
from processors.document_processor import DocumentProcessor
from config import SUPPORTED_BRANDS, PRODUCT_CATEGORIES, DOCUMENT_TYPES

# Page configuration
st.set_page_config(
    page_title="Electronics Support Knowledge Base",
    page_icon="🔧",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'query_engine' not in st.session_state:
    st.session_state.query_engine = RAGQueryEngine()
    st.session_state.db_manager = LanceDBManager()
    st.session_state.doc_processor = DocumentProcessor()

if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

def main():
    st.title("🔧 Electronics Support Knowledge Base")
    st.markdown("Ask questions about Samsung and LG products - TVs, Refrigerators, Washing Machines, Speakers, and more!")
    
    # Sidebar for filters and settings
    with st.sidebar:
        st.header("Search Filters")
        
        brand_filter = st.selectbox(
            "Brand",
            options=["All"] + SUPPORTED_BRANDS,
            index=0
        )
        
        product_filter = st.selectbox(
            "Product Category", 
            options=["All"] + PRODUCT_CATEGORIES,
            index=0
        )
        
        doc_type_filter = st.selectbox(
            "Document Type",
            options=["All"] + DOCUMENT_TYPES,
            index=0
        )
        
        use_cognee = st.checkbox("Use Cognee AI", value=False, help="Enhanced AI-powered responses")
        
        st.divider()
        
        # Knowledge base stats
        st.header("Knowledge Base Stats")
        stats = st.session_state.query_engine.get_stats()
        st.metric("Total Documents", stats["total_documents"])
        st.write(f"**LanceDB Status:** {stats['lancedb_status']}")
        st.write(f"**OpenAI Available:** {'✅' if stats['openai_available'] else '❌'}")
        
        st.divider()
        
        # Data management
        st.header("Data Management")
        
        if st.button("Load Sample Data"):
            load_sample_data()
        
        uploaded_files = st.file_uploader(
            "Upload Documents",
            accept_multiple_files=True,
            type=['txt', 'pdf', 'docx', 'md']
        )
        
        if uploaded_files and st.button("Process Uploaded Files"):
            process_uploaded_files(uploaded_files)
        
        if st.button("Clear Database", type="secondary"):
            if st.session_state.db_manager.clear_database():
                st.success("Database cleared!")
                st.rerun()
    
    # Main chat interface
    col1, col2 = st.columns([3, 1])
    
    with col1:
        # Chat input
        user_question = st.text_input(
            "Ask your question:",
            placeholder="e.g., How do I fix my Samsung TV that won't turn on?",
            key="user_input"
        )
        
        if user_question and st.button("Ask", type="primary"):
            process_question(user_question, brand_filter, product_filter, doc_type_filter, use_cognee)
    
    with col2:
        if st.button("Clear Chat", type="secondary"):
            st.session_state.chat_history = []
            st.rerun()
    
    # Display chat history
    st.divider()
    display_chat_history()

def process_question(question, brand_filter, product_filter, doc_type_filter, use_cognee):
    """Process user question and display response"""
    with st.spinner("Searching knowledge base..."):
        # Prepare filters
        filters = {}
        if brand_filter != "All":
            filters["brand"] = brand_filter
        if product_filter != "All":
            filters["product_category"] = product_filter
        if doc_type_filter != "All":
            filters["document_type"] = doc_type_filter
        
        # Query the knowledge base
        result = st.session_state.query_engine.query(
            question, 
            filters=filters if filters else None,
            use_cognee=use_cognee
        )
        
        # Add to chat history
        st.session_state.chat_history.append({
            "question": question,
            "response": result["response"],
            "sources": result["sources"],
            "found_documents": result["found_documents"],
            "filters": filters
        })
        
        st.rerun()

def display_chat_history():
    """Display the chat history"""
    if not st.session_state.chat_history:
        st.info("👋 Welcome! Ask a question about Samsung or LG products to get started.")
        return
    
    for i, chat in enumerate(reversed(st.session_state.chat_history)):
        with st.container():
            # Question
            st.markdown(f"**🤔 Question {len(st.session_state.chat_history) - i}:** {chat['question']}")
            
            # Response
            st.markdown(f"**🤖 Answer:**")
            st.markdown(chat['response'])
            
            # Sources
            if chat['sources']:
                with st.expander(f"📚 Sources ({len(chat['sources'])} documents found)"):
                    for j, source in enumerate(chat['sources'][:3], 1):
                        st.write(f"**{j}.** {source['brand']} {source['product_category']} - {source['document_type']}")
                        st.write(f"   📄 File: {source['file_name']}")
                        if source['score']:
                            st.write(f"   📊 Relevance Score: {source['score']:.3f}")
            
            # Applied filters
            if chat['filters']:
                st.caption(f"🔍 Filters applied: {', '.join([f'{k}: {v}' for k, v in chat['filters'].items()])}")
            
            st.divider()

def load_sample_data():
    """Load sample data into the knowledge base"""
    with st.spinner("Loading sample data..."):
        try:
            # Create sample data
            from sample_data.create_sample_data import create_sample_data
            sample_dir = create_sample_data()
            
            # Process and add to database
            documents = st.session_state.doc_processor.process_directory(str(sample_dir))
            success = st.session_state.db_manager.add_documents(documents)
            
            if success:
                st.success(f"✅ Successfully loaded {len(documents)} document chunks!")
            else:
                st.error("❌ Failed to load sample data")
                
        except Exception as e:
            st.error(f"❌ Error loading sample data: {str(e)}")

def process_uploaded_files(uploaded_files):
    """Process uploaded files and add to knowledge base"""
    with st.spinner(f"Processing {len(uploaded_files)} files..."):
        try:
            # Save uploaded files temporarily
            temp_dir = Path("temp_uploads")
            temp_dir.mkdir(exist_ok=True)
            
            processed_docs = []
            
            for file in uploaded_files:
                # Save file
                file_path = temp_dir / file.name
                with open(file_path, "wb") as f:
                    f.write(file.getbuffer())
                
                # Process file
                metadata = {"uploaded": True}
                documents = st.session_state.doc_processor.process_document(str(file_path), metadata)
                processed_docs.extend(documents)
                
                # Clean up
                file_path.unlink()
            
            # Add to database
            if processed_docs:
                success = st.session_state.db_manager.add_documents(processed_docs)
                if success:
                    st.success(f"✅ Successfully processed {len(processed_docs)} document chunks from {len(uploaded_files)} files!")
                else:
                    st.error("❌ Failed to add documents to database")
            else:
                st.warning("⚠️ No documents were processed")
                
            # Clean up temp directory
            if temp_dir.exists():
                import shutil
                shutil.rmtree(temp_dir, ignore_errors=True)
                
        except Exception as e:
            st.error(f"❌ Error processing files: {str(e)}")

if __name__ == "__main__":
    main() 