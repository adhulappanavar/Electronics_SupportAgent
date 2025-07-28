#!/usr/bin/env python3
"""
Cognee-Enhanced Streamlit Web Interface
Properly uses Cognee as AI Memory Engine with LanceDB backend
"""

import streamlit as st
import asyncio
import sys
from pathlib import Path
from datetime import datetime
import pandas as pd

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from rag_engine.cognee_enhanced_engine import CogneeEnhancedRAGEngine
from admin.raw_data_viewer import RawDataViewer

# Page configuration
st.set_page_config(
    page_title="🧠 Cognee-Enhanced RAG Knowledge Base",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

def main():
    """Main Streamlit application"""
    st.title("🧠 Cognee-Enhanced RAG Knowledge Base")
    st.markdown("**AI Memory Engine** with Knowledge Graphs and Manual Learning")
    
    # Initialize the enhanced RAG engine
    if 'rag_engine' not in st.session_state:
        with st.spinner("🧠 Initializing Cognee AI Memory Engine..."):
            st.session_state.rag_engine = CogneeEnhancedRAGEngine()
        st.success("✅ AI Memory Engine initialized!")
    
    # Sidebar
    with st.sidebar:
        st.header("🔧 System Configuration")
        
        # System status
        system_status = st.session_state.rag_engine.get_system_status()
        st.subheader("📊 System Status")
        
        capabilities = system_status.get("capabilities", {})
        for capability, status in capabilities.items():
            st.markdown(f"**{capability.replace('_', ' ').title()}**: {status}")
        
        st.divider()
        
        # Query options
        st.subheader("⚙️ Query Options")
        use_validation = st.checkbox("🔍 Enable Answer Validation", value=True)
        
        # Context filters (optional)
        st.subheader("🎯 Context Filters")
        brand_filter = st.selectbox("Brand", ["", "Samsung", "LG"], index=0)
        product_filter = st.selectbox("Product", ["", "TV", "Refrigerator", "Washing Machine", "Speaker"], index=0)
        
        # Quick actions
        st.subheader("⚡ Quick Actions")
        if st.button("🔄 Refresh System Status"):
            st.rerun()
    
    # Main interface tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "💬 AI Memory Chat", 
        "📊 System Analytics", 
        "🧠 Memory Insights", 
        "🔧 Admin Panel"
    ])
    
    with tab1:
        ai_memory_chat_interface(brand_filter, product_filter, use_validation)
    
    with tab2:
        system_analytics_interface()
    
    with tab3:
        memory_insights_interface()
    
    with tab4:
        admin_panel_interface()

def ai_memory_chat_interface(brand_filter, product_filter, use_validation):
    """Main chat interface using Cognee AI memory"""
    st.header("💬 AI Memory Chat Interface")
    
    # Chat examples
    with st.expander("💡 Example Queries"):
        examples = [
            "Samsung TV won't turn on after power outage",
            "How to connect LG refrigerator to WiFi?",
            "Washing machine showing error code E1",
            "Bluetooth speaker not pairing with phone",
            "TV screen flickering after firmware update"
        ]
        for example in examples:
            if st.button(f"📝 {example}", key=f"example_{hash(example)}"):
                st.session_state.chat_input = example
    
    # Chat input
    query = st.chat_input("Ask a question about your appliances...", key="main_chat")
    
    # Handle example button clicks
    if hasattr(st.session_state, 'chat_input'):
        query = st.session_state.chat_input
        del st.session_state.chat_input
    
    if query:
        # Create context
        context = {}
        if brand_filter:
            context['brand'] = brand_filter
        if product_filter:
            context['product_category'] = product_filter
        
        # Display user message
        with st.chat_message("user"):
            st.write(query)
        
        # Process query
        with st.chat_message("assistant"):
            with st.spinner("🧠 Querying AI memory system..."):
                # Run async query
                response = asyncio.run(st.session_state.rag_engine.intelligent_query(
                    query, context, use_validation
                ))
            
            # Display response
            st.markdown("### 🤖 AI Memory Response")
            st.write(response.get("answer", "No response available"))
            
            # Show system information
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### 🔍 Sources Used")
                if response.get("ai_memory_used"):
                    st.success("🧠 AI Memory: Used")
                if response.get("manual_knowledge_used"):
                    st.success("📚 Manual Knowledge: Used (Human-validated)")
                
                breakdown = response.get("source_breakdown", {})
                if breakdown:
                    st.metric("Manual Solutions", breakdown.get("manual_solutions", 0))
                    st.metric("AI Memory Results", breakdown.get("ai_memory_results", 0))
                    st.metric("Total Sources", breakdown.get("total_sources", 0))
            
            with col2:
                st.markdown("#### 📊 Response Quality")
                confidence = response.get("confidence_score", 0)
                st.metric("Confidence Score", f"{confidence:.1%}")
                
                if response.get("validation") and use_validation:
                    validation = response["validation"]
                    st.metric("Validation Score", f"{validation.get('overall_score', 0):.1%}")
                    
                    # Show validation details
                    with st.expander("🔍 Validation Details"):
                        for metric, score in validation.get("detailed_scores", {}).items():
                            st.metric(metric.replace("_", " ").title(), f"{score:.1%}")
            
            # Knowledge graph insights
            if response.get("knowledge_graph_insights"):
                st.markdown("#### 🕸️ Knowledge Graph Insights")
                insights = response["knowledge_graph_insights"]
                if insights:
                    for insight in insights:
                        st.info(f"🔗 {insight}")
                else:
                    st.info("🔍 Related concepts will appear here as the knowledge graph grows")
            
            # Feedback interface
            st.markdown("#### 📝 Feedback")
            feedback_col1, feedback_col2 = st.columns(2)
            
            with feedback_col1:
                satisfaction = st.selectbox(
                    "How satisfied are you with this answer?",
                    ["", "Very Satisfied", "Satisfied", "Neutral", "Dissatisfied", "Very Dissatisfied"],
                    key=f"satisfaction_{hash(query)}"
                )
            
            with feedback_col2:
                if satisfaction and satisfaction != "":
                    if st.button("💾 Submit Feedback", key=f"submit_{hash(query)}"):
                        # This would integrate with the feedback system
                        st.success("✅ Feedback submitted! Thank you for helping improve the AI memory.")

def system_analytics_interface():
    """System analytics and performance metrics"""
    st.header("📊 System Analytics")
    
    # Get system status
    status = st.session_state.rag_engine.get_system_status()
    
    # System overview metrics
    st.subheader("🎯 System Overview")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        manual_stats = status.get("manual_knowledge", {})
        st.metric("Manual Solutions", manual_stats.get("total_entries", 0))
        st.metric("Recent Entries", manual_stats.get("recent_entries", 0))
    
    with col2:
        feedback_stats = status.get("feedback_system", {})
        st.metric("Total Feedback", feedback_stats.get("total_feedback", 0))
        st.metric("Manual Corrections", feedback_stats.get("manual_corrections", 0))
    
    with col3:
        avg_confidence = manual_stats.get("avg_confidence", 0)
        satisfaction = feedback_stats.get("satisfaction_rate", 0)
        st.metric("Avg Confidence", f"{avg_confidence:.1%}")
        st.metric("Satisfaction Rate", f"{satisfaction:.1%}")
    
    # AI Memory Engine Status
    st.subheader("🧠 AI Memory Engine")
    memory_stats = status.get("ai_memory_engine", {})
    
    if memory_stats and not memory_stats.get("error"):
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 🔧 Integration Status")
            integration = memory_stats.get("integration_status", {})
            for system, status_val in integration.items():
                st.markdown(f"**{system.replace('_', ' ').title()}**: {status_val}")
        
        with col2:
            st.markdown("#### 🎯 Capabilities")
            capabilities = memory_stats.get("semantic_capabilities", {})
            for capability, status_val in capabilities.items():
                st.markdown(f"**{capability.replace('_', ' ').title()}**: {status_val}")
    else:
        st.error("❌ AI Memory Engine status unavailable")

def memory_insights_interface():
    """Memory insights and knowledge graph visualization"""
    st.header("🧠 Memory Insights")
    
    # Knowledge Graph Information
    st.subheader("🕸️ Knowledge Graph")
    
    engine = st.session_state.rag_engine
    graph_info = engine.cognee_manager.get_knowledge_graph_info()
    
    if not graph_info.get("error"):
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("Graph Database", graph_info.get("graph_database", "Unknown"))
            st.metric("Graph Size", f"{graph_info.get('graph_size_mb', 0)} MB")
        
        with col2:
            st.markdown(f"**Status**: {graph_info.get('status', 'Unknown')}")
            st.markdown(f"**Description**: {graph_info.get('description', 'N/A')}")
    else:
        st.warning("⚠️ Knowledge graph information unavailable")
    
    # DataPoints Information
    st.subheader("📊 DataPoints (Memory Nodes)")
    
    datapoints_info = engine.cognee_manager.get_datapoints_info()
    
    if not datapoints_info.get("error"):
        st.metric("Total DataPoints", datapoints_info.get("total_datapoints", 0))
        
        # DataPoint types
        if datapoints_info.get("datapoint_types"):
            st.markdown("#### 📋 DataPoint Types")
            types_df = pd.DataFrame(datapoints_info["datapoint_types"])
            st.dataframe(types_df, use_container_width=True)
    else:
        st.warning("⚠️ DataPoints information unavailable")
    
    # Memory Statistics
    st.subheader("📈 Memory Statistics")
    memory_stats = engine.cognee_manager.get_memory_statistics()
    
    if not memory_stats.get("error"):
        st.json(memory_stats)
    else:
        st.error("❌ Memory statistics unavailable")

def admin_panel_interface():
    """Admin panel for system management"""
    st.header("🔧 Admin Panel")
    
    # Initialize raw data viewer
    if 'raw_data_viewer' not in st.session_state:
        st.session_state.raw_data_viewer = RawDataViewer()
    
    viewer = st.session_state.raw_data_viewer
    
    # Quick system overview
    st.subheader("📊 System Overview")
    
    if st.button("🔄 Refresh System Data"):
        # Clear cache and refresh
        if 'raw_data_viewer' in st.session_state:
            del st.session_state.raw_data_viewer
        st.rerun()
    
    # System overview
    overview = viewer.get_system_overview()
    
    if overview:
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
        
        # Database status
        st.subheader("🗄️ Database Status")
        for db_name, db_info in overview.items():
            if isinstance(db_info, dict) and 'status' in db_info:
                with st.expander(f"{db_name.replace('_', ' ').title()} - {db_info['status']}"):
                    for key, value in db_info.items():
                        if key != 'status':
                            st.write(f"**{key.replace('_', ' ').title()}**: {value}")
    
    # Database exploration
    st.subheader("🔍 Database Exploration")
    
    db_option = st.selectbox("Select Database to Explore", [
        "Manual Knowledge", "LanceDB", "Cognee SQLite", "Feedback Data"
    ])
    
    if db_option == "Manual Knowledge":
        if st.button("🔍 Load Manual Knowledge Data"):
            data = viewer.get_manual_knowledge_raw_data(limit=50)
            if not data.get('error'):
                st.metric("Total Rows", data.get('total_rows', 0))
                if data.get('sample_data'):
                    df = pd.DataFrame(data['sample_data'])
                    st.dataframe(df, use_container_width=True)
            else:
                st.error(f"Error: {data['error']}")
    
    elif db_option == "LanceDB":
        lancedb_data = viewer.get_lancedb_raw_data(limit=1)
        tables = lancedb_data.get('available_tables', [])
        
        if tables:
            selected_table = st.selectbox("Select Table", tables)
            if st.button("🔍 Load LanceDB Data"):
                data = viewer.get_lancedb_raw_data(selected_table, limit=50)
                if not data.get('error') and data.get('data'):
                    table_data = data['data']
                    st.metric("Total Rows", table_data.get('rows', 0))
                    if table_data.get('sample_data'):
                        df = pd.DataFrame(table_data['sample_data'])
                        st.dataframe(df, use_container_width=True)
        else:
            st.warning("No LanceDB tables found")

if __name__ == "__main__":
    main() 