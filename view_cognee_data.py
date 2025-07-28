#!/usr/bin/env python3
"""
CLI tool to view Cognee usage, data, and database information
"""

import sys
import argparse
import json
from pathlib import Path
from cognee_integration.cognee_manager import CogneeManager

def print_json(data, indent=2):
    """Pretty print JSON data"""
    print(json.dumps(data, indent=indent, default=str))

def print_table(title, data):
    """Print data in a table format"""
    print(f"\n📊 {title}")
    print("=" * (len(title) + 3))
    for key, value in data.items():
        if isinstance(value, dict):
            print(f"{key}:")
            for sub_key, sub_value in value.items():
                print(f"  {sub_key}: {sub_value}")
        else:
            print(f"{key}: {value}")

def view_cognee_status():
    """View Cognee system status"""
    print("🔍 Cognee System Status")
    print("=" * 30)
    
    cognee_manager = CogneeManager()
    status = cognee_manager.get_status()
    
    print(f"📦 Cognee Version: {status.get('cognee_version', 'unknown')}")
    
    # Configuration
    if 'configuration' in status:
        print_table("Configuration", status['configuration'])
    
    # Database information
    if 'databases' in status:
        print("\n💾 Database Information")
        print("=" * 25)
        
        for db_type, db_info in status['databases'].items():
            if db_info:
                print(f"\n🗄️ {db_type.upper()} Database:")
                if 'path' in db_info:
                    print(f"  Path: {db_info['path']}")
                if 'size_mb' in db_info:
                    print(f"  Size: {db_info['size_mb']} MB")
                if 'tables' in db_info:
                    print(f"  Tables: {len(db_info['tables'])}")
                    for table_name, table_info in db_info['tables'].items():
                        print(f"    - {table_name}: {table_info['row_count']} rows")
    
    # System information
    if 'system_info' in status:
        print_table("System Information", status['system_info'])

def view_cognee_usage():
    """View Cognee usage statistics"""
    print("📈 Cognee Usage Statistics")
    print("=" * 30)
    
    cognee_manager = CogneeManager()
    stats = cognee_manager.get_usage_statistics()
    
    if 'error' in stats:
        print(f"❌ Error: {stats['error']}")
        return
    
    # Document statistics
    if 'documents' in stats:
        doc_stats = stats['documents']
        print(f"\n📚 Documents:")
        print(f"  Total Documents: {doc_stats.get('total_documents', 0)}")
        if doc_stats.get('document_tables'):
            print(f"  Document Tables: {', '.join(doc_stats['document_tables'])}")
    
    # Storage statistics
    if 'storage' in stats:
        storage_stats = stats['storage']
        print(f"\n💾 Storage:")
        print(f"  Vector DB: {storage_stats.get('vector_db_size_mb', 0)} MB")
        print(f"  Graph DB: {storage_stats.get('graph_db_size_mb', 0)} MB")
        print(f"  Total: {storage_stats.get('total_size_mb', 0)} MB")

def explore_cognee_data(table_name=None, limit=10):
    """Explore data in Cognee database"""
    print("🔬 Cognee Data Explorer")
    print("=" * 25)
    
    cognee_manager = CogneeManager()
    data = cognee_manager.explore_data(table_name, limit)
    
    if 'error' in data:
        print(f"❌ Error: {data['error']}")
        return
    
    # Show available tables
    print(f"\n📋 Available Tables ({len(data['tables'])}):")
    for i, table in enumerate(data['tables'], 1):
        print(f"  {i}. {table}")
    
    # Show data
    if 'data' in data and data['data']:
        print(f"\n📊 Data Preview:")
        for table, table_data in data['data'].items():
            print(f"\n🗂️ Table: {table}")
            
            if 'error' in table_data:
                print(f"  ❌ Error: {table_data['error']}")
                continue
                
            print(f"  Columns: {', '.join(table_data['columns'])}")
            
            if 'row_count' in table_data:
                print(f"  Showing: {table_data['row_count']} rows")
            
            if 'sample_data' in table_data and table_data['sample_data']:
                print("  Sample Data:")
                for i, row in enumerate(table_data['sample_data'][:3], 1):
                    print(f"    Row {i}: {row}")

def view_cognee_databases():
    """View detailed database information"""
    print("🗄️ Cognee Database Details")
    print("=" * 30)
    
    cognee_manager = CogneeManager()
    db_info = cognee_manager._get_database_info()
    
    if 'error' in db_info:
        print(f"❌ Error: {db_info['error']}")
        return
    
    # SQLite Database
    if 'sqlite' in db_info and db_info['sqlite']:
        sqlite_info = db_info['sqlite']
        print(f"\n📊 SQLite Database:")
        print(f"  Path: {sqlite_info.get('path', 'Not found')}")
        print(f"  Database File: {sqlite_info.get('database_file', 'Not found')}")
        
        if 'tables' in sqlite_info:
            print(f"  Tables ({len(sqlite_info['tables'])}):")
            for table_name, table_info in sqlite_info['tables'].items():
                print(f"    📋 {table_name}:")
                print(f"      Rows: {table_info['row_count']}")
                print(f"      Columns: {len(table_info['columns'])}")
                if table_info['columns']:
                    col_names = [col['name'] for col in table_info['columns'][:5]]
                    print(f"      Sample Columns: {', '.join(col_names)}")
    
    # Vector Database
    if 'vector' in db_info and db_info['vector']:
        vector_info = db_info['vector']
        print(f"\n🎯 Vector Database (LanceDB):")
        print(f"  Path: {vector_info.get('path', 'Not found')}")
        print(f"  Size: {vector_info.get('size_mb', 0)} MB")
    
    # Graph Database
    if 'graph' in db_info and db_info['graph']:
        graph_info = db_info['graph']
        print(f"\n🕸️ Graph Database (Kuzu):")
        print(f"  Path: {graph_info.get('path', 'Not found')}")
        print(f"  Size: {graph_info.get('size_mb', 0)} MB")

def test_cognee_query(query):
    """Test a query against Cognee"""
    print(f"🔍 Testing Cognee Query: '{query}'")
    print("=" * 40)
    
    cognee_manager = CogneeManager()
    
    try:
        result = cognee_manager.query(query)
        print(f"\n📄 Result:")
        print(result)
    except Exception as e:
        print(f"❌ Error: {e}")

def main():
    parser = argparse.ArgumentParser(description="View Cognee usage and data")
    parser.add_argument("--status", action="store_true", help="Show Cognee system status")
    parser.add_argument("--usage", action="store_true", help="Show usage statistics")
    parser.add_argument("--databases", action="store_true", help="Show database details")
    parser.add_argument("--explore", action="store_true", help="Explore data in Cognee database")
    parser.add_argument("--table", type=str, help="Specific table to explore")
    parser.add_argument("--limit", type=int, default=10, help="Limit for data exploration")
    parser.add_argument("--query", type=str, help="Test a query against Cognee")
    parser.add_argument("--all", action="store_true", help="Show all information")
    
    args = parser.parse_args()
    
    if args.all or (not any([args.status, args.usage, args.databases, args.explore, args.query])):
        # Show everything by default
        view_cognee_status()
        print("\n" + "="*60)
        view_cognee_usage()
        print("\n" + "="*60)
        view_cognee_databases()
        print("\n" + "="*60)
        explore_cognee_data()
    else:
        if args.status:
            view_cognee_status()
        
        if args.usage:
            view_cognee_usage()
        
        if args.databases:
            view_cognee_databases()
        
        if args.explore:
            explore_cognee_data(args.table, args.limit)
        
        if args.query:
            test_cognee_query(args.query)

if __name__ == "__main__":
    main() 