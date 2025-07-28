import streamlit as st
import sys
import os
from pathlib import Path
from datetime import datetime
import pandas as pd # Added for admin panel

# Add parent directory to path to import modules
sys.path.append(str(Path(__file__).parent.parent))

from rag_engine.enhanced_query_engine import EnhancedQueryEngine
from database.manual_knowledge_manager import ManualKnowledgeManager
from feedback.feedback_manager import FeedbackManager
from validation.answer_validator import AnswerValidator
from config import SUPPORTED_BRANDS, PRODUCT_CATEGORIES, DOCUMENT_TYPES

# Page configuration
st.set_page_config(
    page_title="Enhanced Electronics Support Knowledge Base",
    page_icon="🔧",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'enhanced_query_engine' not in st.session_state:
    st.session_state.enhanced_query_engine = EnhancedQueryEngine()
    st.session_state.manual_knowledge = ManualKnowledgeManager()
    st.session_state.feedback_manager = FeedbackManager()

if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

if 'feedback_mode' not in st.session_state:
    st.session_state.feedback_mode = False

def main():
    st.title("🔧 Enhanced Electronics Support Knowledge Base")
    st.markdown("Advanced RAG system with validation, feedback learning, and manual knowledge integration")
    
    # Sidebar for settings and management
    with st.sidebar:
        st.header("⚙️ Settings")
        
        # Query settings
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
        
        # Advanced options
        st.divider()
        st.subheader("🔬 Advanced Options")
        
        use_cognee = st.checkbox("Use Cognee AI", value=False)
        validation_enabled = st.checkbox("Enable Answer Validation", value=True)
        
        st.divider()
        
        # Knowledge base stats
        st.header("📊 Knowledge Base Stats")
        stats = st.session_state.enhanced_query_engine.get_comprehensive_stats()
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Original Docs", stats["original_knowledge"]["document_count"])
        with col2:
            st.metric("Manual Solutions", stats["manual_knowledge"].get("total_manual_entries", 0))
        
        # Validation status
        st.write(f"**Validation:** {'✅ Enabled' if validation_enabled else '❌ Disabled'}")
        st.write(f"**Manual Knowledge:** {'✅ Active' if stats['manual_knowledge'].get('total_manual_entries', 0) > 0 else '⚠️ Empty'}")
        
        st.divider()
        
        # Management options
        st.header("🛠️ Management")
        
        if st.button("🔄 Sync Manual Knowledge"):
            with st.spinner("Syncing manual knowledge..."):
                sync_count = st.session_state.manual_knowledge.sync_from_feedback()
                st.success(f"✅ Synced {sync_count} manual knowledge entries")
                st.rerun()
        
        if st.button("View Feedback Stats"):
            show_feedback_stats()
        
        if st.button("Export Reports"):
            export_reports()
    
    # Main interface tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["💬 Chat Interface", "📝 Feedback Management", "📈 Analytics", "🧠 Cognee Data", "🔧 Admin Panel"])
    
    with tab1:
        chat_interface(brand_filter, product_filter, doc_type_filter, use_cognee, validation_enabled)
    
    with tab2:
        feedback_management_interface()
    
    with tab3:
        analytics_interface()
    
    with tab4:
        cognee_data_interface()
    
    with tab5:
        admin_panel_interface()

def chat_interface(brand_filter, product_filter, doc_type_filter, use_cognee, validation_enabled):
    """Main chat interface with enhanced features"""
    
    # Chat input
    col1, col2 = st.columns([3, 1])
    
    with col1:
        user_question = st.text_input(
            "Ask your question:",
            placeholder="e.g., Samsung TV won't turn on - tried the manual steps but still not working",
            key="user_input"
        )
    
    with col2:
        if st.button("Ask", type="primary"):
            if user_question:
                process_enhanced_question(user_question, brand_filter, product_filter, doc_type_filter, use_cognee, validation_enabled)
        
        if st.button("Clear Chat", type="secondary"):
            st.session_state.chat_history = []
            st.rerun()
    
    # Display chat history
    st.divider()
    display_enhanced_chat_history()

def process_enhanced_question(question, brand_filter, product_filter, doc_type_filter, use_cognee, validation_enabled):
    """Process question with enhanced features"""
    with st.spinner("🔍 Searching knowledge bases and generating response..."):
        # Prepare filters
        filters = {}
        if brand_filter != "All":
            filters["brand"] = brand_filter
        if product_filter != "All":
            filters["product_category"] = product_filter
        if doc_type_filter != "All":
            filters["document_type"] = doc_type_filter
        
        # Query with enhanced engine
        result = st.session_state.enhanced_query_engine.query_with_validation(
            question, 
            filters=filters if filters else None,
            use_cognee=use_cognee,
            validation_enabled=validation_enabled
        )
        
        # Add to chat history
        chat_entry = {
            "question": question,
            "result": result,
            "filters": filters,
            "timestamp": datetime.now().isoformat(),
            "needs_feedback": False
        }
        
        st.session_state.chat_history.append(chat_entry)
        st.rerun()

def display_enhanced_chat_history():
    """Display chat history with enhanced information"""
    if not st.session_state.chat_history:
        st.info("👋 Welcome! Ask a question about Samsung or LG products to get started.")
        return
    
    for i, chat in enumerate(reversed(st.session_state.chat_history)):
        with st.container():
            # Question
            st.markdown(f"**🤔 Question {len(st.session_state.chat_history) - i}:** {chat['question']}")
            
            result = chat['result']
            
            # Response with confidence indicators
            confidence = result.get('confidence_indicators', {})
            
            col1, col2, col3 = st.columns([3, 1, 1])
            
            with col1:
                st.markdown(f"**🤖 Answer:**")
                st.markdown(result['response'])
            
            with col2:
                # Confidence indicators
                st.markdown("**🎯 Confidence**")
                overall_conf = confidence.get('overall_confidence', 0.5)
                st.progress(overall_conf)
                st.caption(f"{overall_conf:.1%}")
                
                if confidence.get('has_manual_solutions'):
                    st.success("✅ Manual solution")
                
                if result.get('validation') and result['validation'].get('is_valid'):
                    st.success("✅ Validated")
                elif result.get('validation'):
                    st.warning("⚠️ Needs review")
            
            with col3:
                # Feedback actions
                st.markdown("**📝 Feedback**")
                
                feedback_key = f"feedback_{len(st.session_state.chat_history) - i}"
                
                if st.button("👍 Helpful", key=f"helpful_{i}"):
                    log_positive_feedback(chat)
                
                if st.button("👎 Not helpful", key=f"not_helpful_{i}"):
                    show_feedback_form(chat, i)
            
            # Validation details
            if result.get('validation') and st.checkbox(f"Show validation details", key=f"validation_{i}"):
                validation = result['validation']
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Completeness", f"{validation['criteria_scores'].get('completeness', 0):.1%}")
                with col2:
                    st.metric("Accuracy", f"{validation['criteria_scores'].get('accuracy', 0):.1%}")
                with col3:
                    st.metric("Relevance", f"{validation['criteria_scores'].get('relevance', 0):.1%}")
                
                if validation.get('suggestions'):
                    st.warning("**Suggestions:** " + "; ".join(validation['suggestions']))
            
            # Sources with enhanced information
            if result.get('original_sources') or result.get('manual_sources'):
                with st.expander(f"📚 Sources ({result['total_sources']} total)"):
                    
                    # Manual sources (higher priority)
                    if result.get('manual_sources'):
                        st.markdown("**🔧 Manual Solutions (from support agents):**")
                        for j, source in enumerate(result['manual_sources'], 1):
                            st.write(f"**{j}.** {source['brand']} {source['product_category']} - {source['issue_category']}")
                            st.write(f"   📊 Confidence: {source['confidence_score']:.1%}")
                            st.write(f"   🔧 Method: {source['resolution_method']}")
                    
                    # Original documentation sources
                    if result.get('original_sources'):
                        st.markdown("**📖 Original Documentation:**")
                        for j, source in enumerate(result['original_sources'], 1):
                            st.write(f"**{j}.** {source['brand']} {source['product_category']} - {source['document_type']}")
                            st.write(f"   📄 File: {source['file_name']}")
            
            # Applied filters
            if chat['filters']:
                st.caption(f"🔍 Filters: {', '.join([f'{k}: {v}' for k, v in chat['filters'].items()])}")
            
            st.divider()

def show_feedback_form(chat, chat_index):
    """Show feedback form for unsatisfactory answers"""
    st.session_state[f'show_feedback_{chat_index}'] = True

def feedback_management_interface():
    """Interface for managing feedback and manual knowledge"""
    st.header("📝 Feedback Management")
    
    # Feedback form for manual corrections
    with st.expander("➕ Add Manual Solution", expanded=False):
        with st.form("manual_feedback_form"):
            st.subheader("Report Issue and Provide Solution")
            
            col1, col2 = st.columns(2)
            
            with col1:
                user_question = st.text_area("Customer Question:", placeholder="What was the customer asking?")
                original_answer = st.text_area("Original System Answer:", placeholder="What did the system respond?")
                manual_solution = st.text_area("Correct Solution:", placeholder="What was the actual solution?")
            
            with col2:
                support_agent = st.text_input("Support Agent Name:")
                brand = st.selectbox("Brand:", SUPPORTED_BRANDS)
                product_category = st.selectbox("Product:", PRODUCT_CATEGORIES)
                issue_category = st.text_input("Issue Category:", placeholder="e.g., connectivity, power, display")
                resolution_method = st.selectbox("Resolution Method:", 
                    ["Phone support", "Email support", "Chat support", "Escalation", "Field technician"])
                customer_satisfaction = st.selectbox("Customer Satisfaction:", 
                    ["very_satisfied", "satisfied", "neutral", "dissatisfied", "very_dissatisfied"])
                tags = st.text_input("Tags (comma-separated):", placeholder="verified, complex, escalation")
                notes = st.text_area("Additional Notes:")
            
            submitted = st.form_submit_button("Submit Feedback")
            
            if submitted and user_question and manual_solution:
                metadata = {
                    'brand': brand,
                    'product_category': product_category,
                    'issue_category': issue_category,
                    'resolution_method': resolution_method,
                    'customer_satisfaction': customer_satisfaction,
                    'tags': [tag.strip() for tag in tags.split(',') if tag.strip()],
                    'notes': notes,
                    'feedback_type': 'manual_correction',
                    'timestamp': datetime.now().isoformat(),
                    'original_sources': []
                }
                
                feedback_id = st.session_state.manual_knowledge.add_real_time_feedback(
                    user_question=user_question,
                    original_answer=original_answer,
                    manual_solution=manual_solution,
                    support_agent=support_agent,
                    metadata=metadata
                )
                
                st.success(f"✅ Feedback logged successfully! ID: {feedback_id}")
                st.rerun()
    
    # Recent feedback display
    st.subheader("📊 Recent Feedback")
    
    # Search similar issues
    search_query = st.text_input("🔍 Search similar issues:", placeholder="Enter keywords to find similar past issues")
    
    if search_query:
        similar_issues = st.session_state.feedback_manager.search_similar_issues(search_query, limit=5)
        
        if similar_issues:
            st.write(f"Found {len(similar_issues)} similar issues:")
            for issue in similar_issues:
                with st.expander(f"Issue: {issue['question'][:100]}... (Score: {issue['relevance_score']:.2f})"):
                    st.write(f"**Question:** {issue['question']}")
                    st.write(f"**Solution:** {issue['manual_solution']}")
                    st.write(f"**Satisfaction:** {issue['customer_satisfaction']}")
                    st.write(f"**Date:** {issue['timestamp']}")
        else:
            st.info("No similar issues found.")

def analytics_interface():
    """Analytics and reporting interface"""
    st.header("📈 Analytics & Reports")
    
    # Knowledge base overview
    col1, col2, col3 = st.columns(3)
    
    stats = st.session_state.enhanced_query_engine.get_comprehensive_stats()
    feedback_stats = st.session_state.feedback_manager.get_feedback_statistics()
    manual_stats = st.session_state.manual_knowledge.get_manual_knowledge_stats()
    
    with col1:
        st.metric("Total Documents", stats["original_knowledge"]["document_count"])
        st.metric("Manual Solutions", manual_stats.get("total_manual_entries", 0))
    
    with col2:
        st.metric("Total Feedback", feedback_stats.get("total_feedback_entries", 0))
        st.metric("High Confidence Solutions", manual_stats.get("high_confidence_entries", 0))
    
    with col3:
        avg_confidence = manual_stats.get("avg_confidence_score", 0)
        st.metric("Avg Confidence", f"{avg_confidence:.1%}")
        st.metric("Recent Entries", manual_stats.get("recent_entries", 0))
    
    # Detailed analytics
    if feedback_stats.get("total_feedback_entries", 0) > 0:
        st.subheader("📊 Feedback Breakdown")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if feedback_stats.get("feedback_by_type"):
                st.bar_chart(feedback_stats["feedback_by_type"])
                st.caption("Feedback by Type")
        
        with col2:
            if feedback_stats.get("feedback_by_brand"):
                st.bar_chart(feedback_stats["feedback_by_brand"])
                st.caption("Feedback by Brand")

# Utility functions
def sync_manual_knowledge():
    """Sync manual knowledge from feedback"""
    with st.spinner("Syncing manual knowledge..."):
        count = st.session_state.manual_knowledge.sync_from_feedback()
        st.success(f"✅ Synced {count} manual learning entries!")

def show_feedback_stats():
    """Show feedback statistics"""
    stats = st.session_state.feedback_manager.get_feedback_statistics()
    st.json(stats)

def export_reports():
    """Export comprehensive reports"""
    with st.spinner("Generating reports..."):
        success = st.session_state.feedback_manager.export_feedback_report()
        if success:
            st.success("✅ Reports exported to feedback_data/feedback_report.json")

def log_positive_feedback(chat):
    """Log positive feedback"""
    st.success("👍 Thank you for the feedback!")

def cognee_data_interface():
    """Interface for viewing Cognee data and usage"""
    st.header("🧠 Cognee AI Data & Usage")
    
    # Get Cognee manager
    cognee_manager = st.session_state.enhanced_query_engine.cognee_manager
    
    # Tabs for different views
    cognee_tab1, cognee_tab2, cognee_tab3, cognee_tab4 = st.tabs(["📊 Status", "📈 Usage", "🗄️ Databases", "🔍 Data Explorer"])
    
    with cognee_tab1:
        st.subheader("🔍 Cognee System Status")
        
        if st.button("🔄 Refresh Status"):
            st.rerun()
        
        with st.spinner("Getting Cognee status..."):
            status = cognee_manager.get_status()
        
        # Configuration
        st.subheader("⚙️ Configuration")
        config = status.get('configuration', {})
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Cognee Version", status.get('cognee_version', 'unknown'))
        with col2:
            st.metric("LLM Provider", config.get('llm_provider', 'unknown'))
        with col3:
            st.metric("Vector Engine", config.get('vector_engine', 'unknown'))
        
        # API Key status
        api_key_status = "✅ Set" if config.get('api_key_set') else "❌ Not Set"
        st.info(f"**Cognee API Key**: {api_key_status}")
        
        # System Information
        if 'system_info' in status:
            st.subheader("🖥️ System Information")
            system_info = status['system_info']
            
            if 'system_directory' in system_info:
                st.code(f"System Directory: {system_info['system_directory']}")
                st.metric("System Size", f"{system_info.get('system_size_mb', 0)} MB")
    
    with cognee_tab2:
        st.subheader("📈 Cognee Usage Statistics")
        
        if st.button("🔄 Refresh Usage Stats"):
            st.rerun()
        
        with st.spinner("Getting usage statistics..."):
            stats = cognee_manager.get_usage_statistics()
        
        if 'error' in stats:
            st.error(f"Error getting stats: {stats['error']}")
        else:
            # Document statistics
            if 'documents' in stats:
                doc_stats = stats['documents']
                st.subheader("📚 Document Statistics")
                
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Total Documents", doc_stats.get('total_documents', 0))
                with col2:
                    doc_tables = doc_stats.get('document_tables', [])
                    st.metric("Document Tables", len(doc_tables))
                
                if doc_tables:
                    st.write("**Document Tables:**")
                    for table in doc_tables:
                        st.write(f"• {table}")
            
            # Storage statistics
            if 'storage' in stats:
                storage_stats = stats['storage']
                st.subheader("💾 Storage Statistics")
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Vector DB", f"{storage_stats.get('vector_db_size_mb', 0)} MB")
                with col2:
                    st.metric("Graph DB", f"{storage_stats.get('graph_db_size_mb', 0)} MB")
                with col3:
                    st.metric("Total", f"{storage_stats.get('total_size_mb', 0)} MB")
    
    with cognee_tab3:
        st.subheader("🗄️ Cognee Database Details")
        
        if st.button("🔄 Refresh Database Info"):
            st.rerun()
        
        with st.spinner("Getting database information..."):
            db_info = cognee_manager._get_database_info()
        
        if 'error' in db_info:
            st.error(f"Error getting database info: {db_info['error']}")
        else:
            # SQLite Database
            if 'sqlite' in db_info and db_info['sqlite']:
                sqlite_info = db_info['sqlite']
                
                st.subheader("📊 SQLite Database")
                st.code(f"Path: {sqlite_info.get('path', 'Not found')}")
                if 'database_file' in sqlite_info:
                    st.code(f"Database File: {sqlite_info['database_file']}")
                
                if 'tables' in sqlite_info and sqlite_info['tables']:
                    st.write(f"**Tables ({len(sqlite_info['tables'])}):**")
                    
                    # Create a dataframe for better display
                    table_data = []
                    for table_name, table_info in sqlite_info['tables'].items():
                        table_data.append({
                            "Table Name": table_name,
                            "Rows": table_info['row_count'],
                            "Columns": len(table_info['columns']),
                            "Sample Columns": ", ".join([col['name'] for col in table_info['columns'][:3]])
                        })
                    
                    if table_data:
                        st.dataframe(table_data)
            
            # Vector Database
            if 'vector' in db_info and db_info['vector']:
                vector_info = db_info['vector']
                st.subheader("🎯 Vector Database (LanceDB)")
                st.code(f"Path: {vector_info.get('path', 'Not found')}")
                st.metric("Size", f"{vector_info.get('size_mb', 0)} MB")
            
            # Graph Database
            if 'graph' in db_info and db_info['graph']:
                graph_info = db_info['graph']
                st.subheader("🕸️ Graph Database (Kuzu)")
                st.code(f"Path: {graph_info.get('path', 'Not found')}")
                st.metric("Size", f"{graph_info.get('size_mb', 0)} MB")
    
    with cognee_tab4:
        st.subheader("🔍 Cognee Data Explorer")
        
        # Get available tables first
        with st.spinner("Getting available tables..."):
            explorer_data = cognee_manager.explore_data()
        
        if 'error' in explorer_data:
            st.error(f"Error: {explorer_data['error']}")
        else:
            available_tables = explorer_data.get('tables', [])
            
            if available_tables:
                # Table selector
                selected_table = st.selectbox(
                    "Select a table to explore:",
                    options=["All Tables"] + available_tables
                )
                
                # Limit selector
                limit = st.slider("Number of rows to display:", 1, 50, 10)
                
                if st.button("🔍 Explore Data"):
                    table_to_explore = None if selected_table == "All Tables" else selected_table
                    
                    with st.spinner("Exploring data..."):
                        data = cognee_manager.explore_data(table_to_explore, limit)
                    
                    if 'error' in data:
                        st.error(f"Error: {data['error']}")
                    else:
                        # Display data
                        if 'data' in data and data['data']:
                            for table_name, table_data in data['data'].items():
                                st.subheader(f"🗂️ Table: {table_name}")
                                
                                if 'error' in table_data:
                                    st.error(f"Error in table {table_name}: {table_data['error']}")
                                    continue
                                
                                # Show columns
                                st.write(f"**Columns:** {', '.join(table_data['columns'])}")
                                
                                # Show sample data
                                if 'sample_data' in table_data and table_data['sample_data']:
                                    st.write(f"**Sample Data ({len(table_data['sample_data'])} rows):**")
                                    st.dataframe(table_data['sample_data'])
                                else:
                                    st.info("No data found in this table")
                        else:
                            st.info("No data to display")
            else:
                st.warning("No tables found in Cognee database")
        
        # Query tester
        st.subheader("🧪 Test Cognee Query")
        test_query = st.text_input("Enter a query to test:")
        
        if st.button("🔍 Test Query") and test_query:
            with st.spinner("Testing query..."):
                try:
                    result = cognee_manager.query(test_query)
                    st.subheader("📄 Query Result:")
                    st.write(result)
                except Exception as e:
                    st.error(f"Query failed: {e}")

def admin_panel_interface():
    """Admin panel for viewing raw database data"""
    st.header("🔧 Admin Panel - Raw Database Access")
    st.warning("⚠️ This panel shows raw database data. Use carefully in production environments.")
    
    # Initialize the raw data viewer
    if 'raw_data_viewer' not in st.session_state:
        from admin.raw_data_viewer import RawDataViewer
        st.session_state.raw_data_viewer = RawDataViewer()
    
    viewer = st.session_state.raw_data_viewer
    
    # Admin tabs
    admin_tab1, admin_tab2, admin_tab3, admin_tab4, admin_tab5, admin_tab6 = st.tabs([
        "📊 System Overview", 
        "🗄️ LanceDB", 
        "🧠 Manual Knowledge", 
        "💾 Cognee SQLite", 
        "🕸️ Kuzu Graph", 
        "🔍 Search All"
    ])
    
    with admin_tab1:
        st.subheader("📊 System Overview")
        
        if st.button("🔄 Refresh Overview"):
            st.rerun()
        
        with st.spinner("Getting system overview..."):
            overview = viewer.get_system_overview()
        
        # Display system stats
        if 'system_stats' in overview:
            stats = overview['system_stats']
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Total Databases", stats.get('total_databases', 0))
            with col2:
                st.metric("Connected", stats.get('connected_databases', 0))
            with col3:
                st.metric("Total Storage", f"{stats.get('total_storage_mb', 0)} MB")
        
        # Database status grid
        st.subheader("🗄️ Database Status")
        
        for db_name, db_info in overview.items():
            if isinstance(db_info, dict) and 'status' in db_info:
                with st.expander(f"{db_name.replace('_', ' ').title()} - {db_info['status']}"):
                    for key, value in db_info.items():
                        if key != 'status':
                            st.write(f"**{key.replace('_', ' ').title()}**: {value}")
    
    with admin_tab2:
        st.subheader("🗄️ LanceDB Raw Data")
        
        # Table selector
        lancedb_overview = viewer.get_lancedb_raw_data(limit=1)
        available_tables = lancedb_overview.get('available_tables', [])
        
        if available_tables:
            selected_table = st.selectbox("Select LanceDB Table:", available_tables, key="lancedb_table")
            limit = st.slider("Number of rows to display:", 10, 500, 50, key="lancedb_limit")
            
            if st.button("🔍 Load LanceDB Data"):
                with st.spinner("Loading LanceDB data..."):
                    data = viewer.get_lancedb_raw_data(selected_table, limit)
                
                if data.get('error'):
                    st.error(f"Error: {data['error']}")
                else:
                    # Schema info
                    if 'schema' in data:
                        st.subheader("📋 Table Schema")
                        schema_df = pd.DataFrame(data['schema']['fields'])
                        st.dataframe(schema_df)
                    
                    # Data info
                    if data.get('data'):
                        table_data = data['data']
                        st.subheader(f"📊 Data (showing {len(table_data['sample_data'])} of {table_data['rows']} rows)")
                        
                        # Convert to DataFrame for better display
                        if table_data['sample_data']:
                            df = pd.DataFrame(table_data['sample_data'])
                            st.dataframe(df, use_container_width=True)
                            
                            # Download button
                            csv = df.to_csv(index=False)
                            st.download_button(
                                label="📥 Download as CSV",
                                data=csv,
                                file_name=f"{selected_table}_data.csv",
                                mime="text/csv"
                            )
                        else:
                            st.info("No data found in table")
        else:
            st.warning("No LanceDB tables found")
    
    with admin_tab3:
        st.subheader("🧠 Manual Knowledge Raw Data")
        
        limit = st.slider("Number of rows to display:", 10, 500, 50, key="manual_limit")
        
        if st.button("🔍 Load Manual Knowledge Data"):
            with st.spinner("Loading manual knowledge data..."):
                data = viewer.get_manual_knowledge_raw_data(limit)
            
            if data.get('error'):
                st.error(f"Error: {data['error']}")
            else:
                st.metric("Total Rows", data.get('total_rows', 0))
                
                if data.get('sample_data'):
                    df = pd.DataFrame(data['sample_data'])
                    st.dataframe(df, use_container_width=True)
                    
                    # Download button
                    csv = df.to_csv(index=False)
                    st.download_button(
                        label="📥 Download as CSV",
                        data=csv,
                        file_name="manual_knowledge_data.csv",
                        mime="text/csv"
                    )
                else:
                    st.info("No manual knowledge data found")
    
    with admin_tab4:
        st.subheader("💾 Cognee SQLite Raw Data")
        
        # Get available tables
        cognee_overview = viewer.get_cognee_sqlite_raw_data()
        available_tables = cognee_overview.get('available_tables', [])
        
        if available_tables:
            selected_table = st.selectbox("Select Cognee Table:", ["Overview"] + available_tables, key="cognee_table")
            
            if selected_table == "Overview":
                if st.button("🔍 Load Cognee Overview"):
                    with st.spinner("Loading Cognee overview..."):
                        data = viewer.get_cognee_sqlite_raw_data()
                    
                    if data.get('tables_summary'):
                        st.subheader("📊 Tables Summary")
                        summary_df = pd.DataFrame([
                            {"Table": table, "Rows": count}
                            for table, count in data['tables_summary'].items()
                        ])
                        st.dataframe(summary_df)
            else:
                limit = st.slider("Number of rows to display:", 10, 500, 50, key="cognee_limit")
                
                if st.button("🔍 Load Cognee Table Data"):
                    with st.spinner("Loading Cognee table data..."):
                        data = viewer.get_cognee_sqlite_raw_data(selected_table, limit)
                    
                    if data.get('error'):
                        st.error(f"Error: {data['error']}")
                    else:
                        # Schema
                        if 'schema' in data:
                            st.subheader("📋 Table Schema")
                            schema_df = pd.DataFrame(data['schema']['columns'])
                            st.dataframe(schema_df)
                        
                        # Data
                        if data.get('data') and data['data']['sample_data']:
                            table_data = data['data']
                            st.subheader(f"📊 Data (showing {len(table_data['sample_data'])} of {table_data['total_rows']} rows)")
                            
                            df = pd.DataFrame(table_data['sample_data'])
                            st.dataframe(df, use_container_width=True)
                            
                            # Download button
                            csv = df.to_csv(index=False)
                            st.download_button(
                                label="📥 Download as CSV",
                                data=csv,
                                file_name=f"cognee_{selected_table}_data.csv",
                                mime="text/csv"
                            )
        else:
            st.warning("No Cognee tables found or database not accessible")
    
    with admin_tab5:
        st.subheader("🕸️ Kuzu Graph Database")
        
        if st.button("🔍 Load Kuzu Information"):
            with st.spinner("Loading Kuzu data..."):
                data = viewer.get_kuzu_raw_data()
            
            if data.get('error'):
                st.error(f"Error: {data['error']}")
            else:
                st.code(f"Database Path: {data.get('database_path', 'Unknown')}")
                st.metric("Database Size", f"{data.get('size_mb', 0)} MB")
                
                if data.get('files'):
                    st.subheader("📁 Database Files")
                    files_df = pd.DataFrame(data['files'])
                    st.dataframe(files_df)
                
                if data.get('kuzu_info'):
                    st.info(data['kuzu_info'])
    
    with admin_tab6:
        st.subheader("🔍 Search Across All Databases")
        
        search_term = st.text_input("Enter search term:", placeholder="e.g., Samsung, troubleshooting, error")
        search_limit = st.slider("Max results per database:", 10, 100, 25)
        
        if st.button("🔍 Search All Databases") and search_term:
            with st.spinner(f"Searching for '{search_term}' across all databases..."):
                results = viewer.search_across_databases(search_term, search_limit)
            
            if results.get('error'):
                st.error(f"Search error: {results['error']}")
            else:
                # Display results by database
                for db_name, db_results in results.items():
                    if db_name != 'search_term' and isinstance(db_results, list) and db_results:
                        with st.expander(f"{db_name.replace('_', ' ').title()} - {len(db_results)} results"):
                            df = pd.DataFrame(db_results)
                            st.dataframe(df, use_container_width=True)
                            
                            # Download results
                            csv = df.to_csv(index=False)
                            st.download_button(
                                label=f"📥 Download {db_name} results",
                                data=csv,
                                file_name=f"search_{db_name}_{search_term}.csv",
                                mime="text/csv",
                                key=f"download_{db_name}"
                            )
                
                # Summary
                total_results = sum(len(results[db]) for db in results if isinstance(results[db], list))
                st.success(f"Found {total_results} total results across all databases")

if __name__ == "__main__":
    main() 