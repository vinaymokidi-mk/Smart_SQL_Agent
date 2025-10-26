#!/usr/bin/env python3
"""
Direct SQL query interface for your Excel data
"""

import sqlite3
from data_manager import data_manager

def run_direct_sql(sql_query, source_name="my_sales_data"):
    """Run SQL query directly on your data"""
    print(f"🔍 Running SQL: {sql_query}")
    print("=" * 60)
    
    try:
        conn = data_manager.get_connection(source_name)
        cursor = conn.cursor()
        
        cursor.execute(sql_query)
        results = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description] if cursor.description else []
        
        if results:
            # Format as table
            if columns:
                col_widths = []
                for i, col_name in enumerate(columns):
                    max_width = len(col_name)
                    for row in results:
                        if i < len(row):
                            max_width = max(max_width, len(str(row[i])))
                    col_widths.append(max_width)
                
                # Header
                header_parts = []
                separator_parts = []
                for i, (col_name, width) in enumerate(zip(columns, col_widths)):
                    header_parts.append(col_name.ljust(width))
                    separator_parts.append("-" * width)
                
                header = " | ".join(header_parts)
                separator = " | ".join(separator_parts)
                
                # Rows
                rows = []
                for row in results:
                    row_parts = []
                    for i, width in enumerate(col_widths):
                        value = str(row[i]) if i < len(row) else ""
                        row_parts.append(value.ljust(width))
                    rows.append(" | ".join(row_parts))
                
                print(header)
                print(separator)
                for row in rows:
                    print(row)
            else:
                print(results)
        else:
            print("No results found")
            
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def interactive_sql():
    """Interactive SQL interface"""
    print("\n🎮 INTERACTIVE SQL MODE")
    print("=" * 40)
    print("Write SQL queries directly on your Excel data!")
    print("Examples:")
    print("  SELECT * FROM sales")
    print("  SELECT product_name, quantity FROM sales")
    print("  SELECT region, COUNT(*) FROM sales GROUP BY region")
    print("  SELECT salesperson, SUM(total_amount) FROM sales GROUP BY salesperson")
    print("\nCommands:")
    print("  /help - Show examples")
    print("  /quit - Exit")
    print("=" * 40)
    
    while True:
        try:
            user_input = input("\n💬 Enter SQL query: ").strip()
            
            if not user_input:
                continue
            
            if user_input.lower() in ['/quit', '/exit', '/q']:
                print("👋 Goodbye!")
                break
            
            elif user_input.lower() == '/help':
                print("\nExample SQL queries:")
                print("  SELECT * FROM sales")
                print("  SELECT COUNT(*) FROM sales")
                print("  SELECT product_name, quantity FROM sales")
                print("  SELECT region, COUNT(*) FROM sales GROUP BY region")
                print("  SELECT salesperson, SUM(total_amount) FROM sales GROUP BY salesperson")
                print("  SELECT * FROM sales WHERE region = 'North'")
                print("  SELECT product_name, SUM(quantity) FROM sales GROUP BY product_name ORDER BY SUM(quantity) DESC")
            
            else:
                run_direct_sql(user_input)
                
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    interactive_sql()
