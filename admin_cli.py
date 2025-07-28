#!/usr/bin/env python3
"""
CLI Admin Tool for Enhanced RAG Knowledge Base
Provides command-line access to raw data from all databases
"""

import sys
import argparse
import json
import pandas as pd
from pathlib import Path
from admin.raw_data_viewer import RawDataViewer

def print_table(data, title="Data"):
    """Print data in a formatted table"""
    print(f"\n📊 {title}")
    print("=" * (len(title) + 3))
    
    if isinstance(data, list) and data:
        df = pd.DataFrame(data)
        print(df.to_string(index=False))
    elif isinstance(data, dict):
        for key, value in data.items():
            print(f"{key}: {value}")
    else:
        print("No data to display")

def system_overview(viewer):
    """Display system overview"""
    print("🔧 Admin Panel - System Overview")
    print("=" * 40)
    
    overview = viewer.get_system_overview()
    
    if 'system_stats' in overview:
        stats = overview['system_stats']
        print(f"\n📊 System Statistics:")
        print(f"   Total Databases: {stats.get('total_databases', 0)}")
        print(f"   Connected: {stats.get('connected_databases', 0)}")
        print(f"   Total Storage: {stats.get('total_storage_mb', 0)} MB")
    
    print(f"\n🗄️ Database Status:")
    for db_name, db_info in overview.items():
        if isinstance(db_info, dict) and 'status' in db_info:
            print(f"\n{db_name.replace('_', ' ').title()}:")
            for key, value in db_info.items():
                print(f"  {key}: {value}")

def view_lancedb(viewer, table_name=None, limit=50):
    """View LanceDB data"""
    print("🗄️ LanceDB Raw Data")
    print("=" * 25)
    
    if not table_name:
        # Show available tables
        data = viewer.get_lancedb_raw_data(limit=1)
        tables = data.get('available_tables', [])
        print(f"\nAvailable Tables ({len(tables)}):")
        for i, table in enumerate(tables, 1):
            print(f"  {i}. {table}")
        return
    
    data = viewer.get_lancedb_raw_data(table_name, limit)
    
    if data.get('error'):
        print(f"❌ Error: {data['error']}")
        return
    
    # Schema
    if 'schema' in data:
        print(f"\n📋 Schema for '{table_name}':")
        for field in data['schema']['fields']:
            print(f"  {field['name']}: {field['type']}")
    
    # Data
    if data.get('data'):
        table_data = data['data']
        print(f"\n📊 Data (showing {len(table_data['sample_data'])} of {table_data['rows']} rows):")
        print_table(table_data['sample_data'])

def view_manual_knowledge(viewer, limit=50):
    """View manual knowledge data"""
    print("🧠 Manual Knowledge Raw Data")
    print("=" * 30)
    
    data = viewer.get_manual_knowledge_raw_data(limit)
    
    if data.get('error'):
        print(f"❌ Error: {data['error']}")
        return
    
    print(f"\nTotal Rows: {data.get('total_rows', 0)}")
    print(f"Columns: {', '.join(data.get('columns', []))}")
    
    if data.get('sample_data'):
        print_table(data['sample_data'], f"Manual Knowledge Data (showing {len(data['sample_data'])} rows)")
    else:
        print("\n📭 No manual knowledge data found")

def view_cognee_sqlite(viewer, table_name=None, limit=50):
    """View Cognee SQLite data"""
    print("💾 Cognee SQLite Raw Data")
    print("=" * 30)
    
    if not table_name:
        # Show overview
        data = viewer.get_cognee_sqlite_raw_data()
        if data.get('error'):
            print(f"❌ Error: {data['error']}")
            return
        
        tables = data.get('available_tables', [])
        print(f"\nAvailable Tables ({len(tables)}):")
        for i, table in enumerate(tables, 1):
            print(f"  {i}. {table}")
        
        if data.get('tables_summary'):
            print(f"\n📊 Table Summary:")
            for table, count in data['tables_summary'].items():
                print(f"  {table}: {count} rows")
        return
    
    data = viewer.get_cognee_sqlite_raw_data(table_name, limit)
    
    if data.get('error'):
        print(f"❌ Error: {data['error']}")
        return
    
    # Schema
    if 'schema' in data:
        print(f"\n📋 Schema for '{table_name}':")
        for col in data['schema']['columns']:
            nullable = "nullable" if col['nullable'] else "not null"
            print(f"  {col['name']}: {col['type']} ({nullable})")
    
    # Data
    if data.get('data') and data['data']['sample_data']:
        table_data = data['data']
        print(f"\n📊 Data (showing {len(table_data['sample_data'])} of {table_data['total_rows']} rows):")
        print_table(table_data['sample_data'])

def view_kuzu(viewer):
    """View Kuzu graph database info"""
    print("🕸️ Kuzu Graph Database")
    print("=" * 25)
    
    data = viewer.get_kuzu_raw_data()
    
    if data.get('error'):
        print(f"❌ Error: {data['error']}")
        return
    
    print(f"\nDatabase Path: {data.get('database_path', 'Unknown')}")
    print(f"Database Size: {data.get('size_mb', 0)} MB")
    
    if data.get('files'):
        print(f"\n📁 Database Files ({len(data['files'])}):")
        for file_info in data['files']:
            print(f"  {file_info['name']} ({file_info['size_mb']} MB) {file_info['type']}")
    
    if data.get('kuzu_info'):
        print(f"\n💡 Connection Info: {data['kuzu_info']}")

def view_feedback(viewer, limit=50):
    """View feedback data"""
    print("📝 Feedback Raw Data")
    print("=" * 25)
    
    data = viewer.get_feedback_raw_data(limit)
    
    if data.get('error'):
        print(f"❌ Error: {data['error']}")
        return
    
    print(f"\nFile Path: {data.get('file_path', 'Unknown')}")
    print(f"File Size: {data.get('file_size_mb', 0)} MB")
    print(f"Total Rows: {data.get('total_rows', 0)}")
    print(f"Columns: {', '.join(data.get('columns', []))}")
    
    if data.get('sample_data'):
        print_table(data['sample_data'], f"Feedback Data (showing {len(data['sample_data'])} rows)")
    else:
        print("\n📭 No feedback data found")

def search_databases(viewer, search_term, limit=25):
    """Search across all databases"""
    print(f"🔍 Searching for '{search_term}' across all databases")
    print("=" * 50)
    
    results = viewer.search_across_databases(search_term, limit)
    
    if results.get('error'):
        print(f"❌ Search error: {results['error']}")
        return
    
    total_results = 0
    
    for db_name, db_results in results.items():
        if db_name != 'search_term' and isinstance(db_results, list):
            if db_results:
                print(f"\n🗄️ {db_name.replace('_', ' ').title()} - {len(db_results)} results:")
                print_table(db_results[:5])  # Show only first 5 results for CLI
                if len(db_results) > 5:
                    print(f"   ... and {len(db_results) - 5} more results")
                total_results += len(db_results)
            else:
                print(f"\n🗄️ {db_name.replace('_', ' ').title()}: No results")
    
    print(f"\n📊 Total results: {total_results}")

def export_data(viewer, database, table=None, output_file=None):
    """Export database data to file"""
    print(f"📤 Exporting {database} data...")
    
    if database == "lancedb":
        if not table:
            print("❌ Table name required for LanceDB export")
            return
        data = viewer.get_lancedb_raw_data(table, limit=10000)
        export_data = data.get('data', {}).get('sample_data', [])
    elif database == "manual":
        data = viewer.get_manual_knowledge_raw_data(limit=10000)
        export_data = data.get('sample_data', [])
    elif database == "cognee":
        if not table:
            print("❌ Table name required for Cognee export")
            return
        data = viewer.get_cognee_sqlite_raw_data(table, limit=10000)
        export_data = data.get('data', {}).get('sample_data', [])
    elif database == "feedback":
        data = viewer.get_feedback_raw_data(limit=10000)
        export_data = data.get('sample_data', [])
    else:
        print(f"❌ Unknown database: {database}")
        return
    
    if not export_data:
        print("❌ No data to export")
        return
    
    # Generate filename if not provided
    if not output_file:
        table_suffix = f"_{table}" if table else ""
        output_file = f"{database}{table_suffix}_export.csv"
    
    # Export to CSV
    df = pd.DataFrame(export_data)
    df.to_csv(output_file, index=False)
    print(f"✅ Exported {len(export_data)} rows to {output_file}")

def main():
    parser = argparse.ArgumentParser(description="Admin CLI for Enhanced RAG Knowledge Base")
    parser.add_argument("command", choices=[
        "overview", "lancedb", "manual", "cognee", "kuzu", "feedback", "search", "export"
    ], help="Admin command to execute")
    
    # Optional arguments
    parser.add_argument("--table", type=str, help="Table name (for lancedb, cognee)")
    parser.add_argument("--limit", type=int, default=50, help="Number of rows to display")
    parser.add_argument("--search-term", type=str, help="Search term (for search command)")
    parser.add_argument("--output", type=str, help="Output file (for export command)")
    parser.add_argument("--database", type=str, choices=["lancedb", "manual", "cognee", "feedback"], 
                       help="Database to export (for export command)")
    
    args = parser.parse_args()
    
    # Initialize viewer
    print("🔧 Initializing Admin Panel...")
    try:
        viewer = RawDataViewer()
    except Exception as e:
        print(f"❌ Failed to initialize admin panel: {e}")
        return 1
    
    # Execute command
    try:
        if args.command == "overview":
            system_overview(viewer)
        
        elif args.command == "lancedb":
            view_lancedb(viewer, args.table, args.limit)
        
        elif args.command == "manual":
            view_manual_knowledge(viewer, args.limit)
        
        elif args.command == "cognee":
            view_cognee_sqlite(viewer, args.table, args.limit)
        
        elif args.command == "kuzu":
            view_kuzu(viewer)
        
        elif args.command == "feedback":
            view_feedback(viewer, args.limit)
        
        elif args.command == "search":
            if not args.search_term:
                print("❌ Search term required. Use --search-term")
                return 1
            search_databases(viewer, args.search_term, args.limit)
        
        elif args.command == "export":
            if not args.database:
                print("❌ Database required for export. Use --database")
                return 1
            export_data(viewer, args.database, args.table, args.output)
        
    except Exception as e:
        print(f"❌ Command failed: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 