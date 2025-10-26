import sys
import os
from typing import Dict, Any
from flow_flexible import create_text_to_sql_flow
from data_manager import data_manager

def run_text_to_sql_flexible(
    natural_query: str, 
    source_name: str = None,
    max_debug_retries: int = 3,
    use_debug_loop: bool = True
) -> Dict[str, Any]:
    """
    Run the text-to-SQL workflow with flexible data sources.
    
    Args:
        natural_query: Natural language question to convert to SQL
        source_name: Name of data source (uses active if not specified)
        max_debug_retries: Maximum number of debug attempts
        use_debug_loop: Whether to use debug loop or simple flow
        
    Returns:
        Dictionary containing workflow results
    """
    # Get source name
    if not source_name:
        source_name = data_manager.get_active_source()
    
    if not source_name:
        print("❌ No data source specified and no active source found.")
        print("Available commands:")
        print("  python cli.py list")
        print("  python cli.py set-active <source-name>")
        return {"final_error": "No data source available"}
    
    # Verify source exists
    if source_name not in data_manager.config["data_sources"]:
        print(f"❌ Data source '{source_name}' not found.")
        print("Available sources:")
        for source in data_manager.list_sources():
            print(f"  - {source['name']} ({source['type']})")
        return {"final_error": f"Data source '{source_name}' not found"}
    
    # Initialize shared store
    shared = {
        "source_name": source_name,
        "natural_query": natural_query,
        "max_debug_attempts": max_debug_retries,
        "debug_attempts": 0,
        "final_result": None,
        "final_error": None,
        "result_columns": [],
        "execution_error": None
    }
    
    # Display workflow information
    source_config = data_manager.config["data_sources"][source_name]
    print(f"\n{'='*60}")
    print(f"TEXT-TO-SQL WORKFLOW (FLEXIBLE)")
    print(f"{'='*60}")
    print(f"Query: '{natural_query}'")
    print(f"Data Source: {source_name} ({source_config['type']})")
    print(f"Max Debug Retries: {max_debug_retries}")
    print(f"Debug Loop: {'Enabled' if use_debug_loop else 'Disabled'}")
    print(f"{'='*60}")
    
    # Create and run flow
    if use_debug_loop:
        flow = create_text_to_sql_flow()
    else:
        from flow_flexible import create_simple_text_to_sql_flow
        flow = create_simple_text_to_sql_flow()
    
    try:
        flow.run(shared)
    except Exception as e:
        print(f"Workflow execution error: {e}")
        shared["final_error"] = f"Workflow execution failed: {e}"
    
    # Display final results
    print(f"\n{'='*60}")
    if shared.get("final_error"):
        print("WORKFLOW COMPLETED WITH ERROR")
        print(f"Error: {shared['final_error']}")
    elif shared.get("final_result") is not None:
        print("WORKFLOW COMPLETED SUCCESSFULLY")
        print("Results displayed above.")
    else:
        print("WORKFLOW COMPLETED (UNKNOWN STATE)")
    print(f"{'='*60}")
    
    return shared


def main():
    """Main entry point for the flexible system."""
    # Check for OpenAI API key
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ Error: OPENAI_API_KEY environment variable not set.")
        print("Please set your OpenAI API key:")
        print("export OPENAI_API_KEY='your-api-key-here'")
        print("\nOr on Windows:")
        print("set OPENAI_API_KEY=your-api-key-here")
        sys.exit(1)
    
    # Check if we have any data sources
    sources = data_manager.list_sources()
    if not sources:
        print("📊 No data sources configured.")
        print("Please configure data sources using the CLI:")
        print("  python cli.py add-excel <name> <file_path>")
        print("  python cli.py set-active <source-name>")
        sys.exit(1)
    
    # Get query from command line arguments or use default
    if len(sys.argv) > 1:
        query = " ".join(sys.argv[1:])
    else:
        query = "Show me all customers from New York"
    
    # Run the workflow
    try:
        result = run_text_to_sql_flexible(query)
        
        # Exit with appropriate code
        if result.get("final_error"):
            sys.exit(1)
        else:
            sys.exit(0)
            
    except KeyboardInterrupt:
        print("\nWorkflow interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
