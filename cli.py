#!/usr/bin/env python3
"""
CLI interface for managing data sources and running text-to-SQL queries.
"""

import argparse
import sys
import os
from pathlib import Path
from data_manager import data_manager
from main import run_text_to_sql

def add_database_source(args):
    """Add a database data source."""
    try:
        data_manager.add_database_source(
            name=args.name,
            db_type=args.db_type,
            connection_string=args.connection_string,
            description=args.description
        )
        print(f"✅ Added database source: {args.name}")
    except Exception as e:
        print(f"❌ Error adding database source: {e}")

def add_excel_source(args):
    """Add an Excel data source."""
    try:
        data_manager.add_excel_source(
            name=args.name,
            file_path=args.file_path,
            sheet_name=args.sheet_name,
            description=args.description
        )
        print(f"✅ Added Excel source: {args.name}")
    except Exception as e:
        print(f"❌ Error adding Excel source: {e}")

def list_sources(args):
    """List all data sources."""
    sources = data_manager.list_sources()
    
    if not sources:
        print("No data sources configured.")
        return
    
    print("\n📊 Available Data Sources:")
    print("=" * 60)
    
    for source in sources:
        status = "🟢 Active" if source["active"] else "⚪ Inactive"
        print(f"Name: {source['name']}")
        print(f"Type: {source['type']}")
        print(f"Status: {status}")
        print(f"Description: {source['description']}")
        print("-" * 40)

def set_active_source(args):
    """Set the active data source."""
    try:
        data_manager.set_active_source(args.name)
        print(f"✅ Set active data source: {args.name}")
    except Exception as e:
        print(f"❌ Error setting active source: {e}")

def remove_source(args):
    """Remove a data source."""
    try:
        data_manager.remove_source(args.name)
        print(f"✅ Removed data source: {args.name}")
    except Exception as e:
        print(f"❌ Error removing source: {e}")

def show_schema(args):
    """Show schema for a data source."""
    try:
        schema = data_manager.get_schema(args.name)
        print(f"\n📋 Schema for '{args.name}':")
        print("=" * 50)
        print(schema)
        print("=" * 50)
    except Exception as e:
        print(f"❌ Error getting schema: {e}")

def run_query(args):
    """Run a text-to-SQL query."""
    try:
        # Get active source or use specified source
        source_name = args.source or data_manager.get_active_source()
        
        if not source_name:
            print("❌ No active data source. Please set one first.")
            print("Use: python cli.py set-active <source-name>")
            return
        
        # Get connection for the source
        conn = data_manager.get_connection(source_name)
        db_path = conn.cursor().connection.filename if hasattr(conn.cursor().connection, 'filename') else f"temp_{source_name}.db"
        conn.close()
        
        # Run the query
        result = run_text_to_sql(
            natural_query=args.query,
            db_path=db_path,
            max_debug_retries=args.max_retries,
            use_debug_loop=not args.no_debug
        )
        
        if result.get("final_error"):
            print(f"❌ Query failed: {result['final_error']}")
            sys.exit(1)
        else:
            print("✅ Query executed successfully!")
            
    except Exception as e:
        print(f"❌ Error running query: {e}")
        sys.exit(1)

def interactive_mode(args):
    """Run in interactive mode."""
    print("\n🤖 Text-to-SQL Interactive Mode")
    print("=" * 40)
    print("Commands:")
    print("  /help - Show help")
    print("  /sources - List data sources")
    print("  /schema [source] - Show schema")
    print("  /active [source] - Set active source")
    print("  /quit - Exit")
    print("  Any other text will be treated as a query")
    print("=" * 40)
    
    while True:
        try:
            user_input = input("\n💬 Enter query or command: ").strip()
            
            if not user_input:
                continue
            
            if user_input.lower() in ['/quit', '/exit', '/q']:
                print("👋 Goodbye!")
                break
            
            elif user_input.lower() == '/help':
                print("Available commands:")
                print("  /help - Show this help")
                print("  /sources - List data sources")
                print("  /schema [source] - Show schema")
                print("  /active [source] - Set active source")
                print("  /quit - Exit")
                print("  Any other text will be treated as a query")
            
            elif user_input.lower() == '/sources':
                list_sources(None)
            
            elif user_input.lower().startswith('/schema'):
                parts = user_input.split()
                source_name = parts[1] if len(parts) > 1 else data_manager.get_active_source()
                if source_name:
                    show_schema(type('Args', (), {'name': source_name})())
                else:
                    print("❌ No active data source")
            
            elif user_input.lower().startswith('/active'):
                parts = user_input.split()
                if len(parts) > 1:
                    set_active_source(type('Args', (), {'name': parts[1]})())
                else:
                    print("❌ Please specify source name")
            
            else:
                # Treat as query
                run_query(type('Args', (), {
                    'query': user_input,
                    'source': None,
                    'max_retries': 3,
                    'no_debug': False
                })())
                
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")

def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Text-to-SQL CLI - Connect to any data source and query with natural language",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Add Excel file
  python cli.py add-excel sales_data.xlsx --name sales --description "Sales data"
  
  # Add SQLite database
  python cli.py add-db --name mydb --db-type sqlite --connection-string mydb.db
  
  # Add PostgreSQL database
  python cli.py add-db --name prod --db-type postgresql --connection-string "host=localhost dbname=mydb user=user password=pass"
  
  # List sources
  python cli.py list
  
  # Set active source
  python cli.py set-active sales
  
  # Show schema
  python cli.py schema sales
  
  # Run query
  python cli.py query "Show me top 10 customers by revenue"
  
  # Interactive mode
  python cli.py interactive
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Add database source
    db_parser = subparsers.add_parser('add-db', help='Add database data source')
    db_parser.add_argument('--name', required=True, help='Source name')
    db_parser.add_argument('--db-type', required=True, choices=['sqlite', 'postgresql', 'mysql'], help='Database type')
    db_parser.add_argument('--connection-string', required=True, help='Database connection string')
    db_parser.add_argument('--description', default='', help='Description')
    db_parser.set_defaults(func=add_database_source)
    
    # Add Excel source
    excel_parser = subparsers.add_parser('add-excel', help='Add Excel data source')
    excel_parser.add_argument('file_path', help='Path to Excel file')
    excel_parser.add_argument('--name', help='Source name (defaults to filename)')
    excel_parser.add_argument('--sheet-name', help='Specific sheet name (defaults to all sheets)')
    excel_parser.add_argument('--description', default='', help='Description')
    excel_parser.set_defaults(func=add_excel_source)
    
    # List sources
    list_parser = subparsers.add_parser('list', help='List all data sources')
    list_parser.set_defaults(func=list_sources)
    
    # Set active source
    active_parser = subparsers.add_parser('set-active', help='Set active data source')
    active_parser.add_argument('name', help='Source name')
    active_parser.set_defaults(func=set_active_source)
    
    # Remove source
    remove_parser = subparsers.add_parser('remove', help='Remove data source')
    remove_parser.add_argument('name', help='Source name')
    remove_parser.set_defaults(func=remove_source)
    
    # Show schema
    schema_parser = subparsers.add_parser('schema', help='Show data source schema')
    schema_parser.add_argument('name', help='Source name')
    schema_parser.set_defaults(func=show_schema)
    
    # Run query
    query_parser = subparsers.add_parser('query', help='Run text-to-SQL query')
    query_parser.add_argument('query', help='Natural language query')
    query_parser.add_argument('--source', help='Data source name (uses active if not specified)')
    query_parser.add_argument('--max-retries', type=int, default=3, help='Maximum debug retries')
    query_parser.add_argument('--no-debug', action='store_true', help='Disable debug loop')
    query_parser.set_defaults(func=run_query)
    
    # Interactive mode
    interactive_parser = subparsers.add_parser('interactive', help='Run in interactive mode')
    interactive_parser.set_defaults(func=interactive_mode)
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Handle Excel file path for add-excel command
    if args.command == 'add-excel':
        if not args.name:
            args.name = Path(args.file_path).stem
    
    args.func(args)

if __name__ == "__main__":
    main()
