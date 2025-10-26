import sys
import os
import sqlite3
from typing import Dict, Any
from flow import create_text_to_sql_flow

# Default database file
DEFAULT_DB_FILE = "ecommerce.db"


def run_text_to_sql(
    natural_query: str, 
    db_path: str = DEFAULT_DB_FILE, 
    max_debug_retries: int = 3,
    use_debug_loop: bool = True
) -> Dict[str, Any]:
    """
    Run the text-to-SQL workflow.
    
    Args:
        natural_query: Natural language question to convert to SQL
        db_path: Path to SQLite database file
        max_debug_retries: Maximum number of debug attempts
        use_debug_loop: Whether to use debug loop or simple flow
        
    Returns:
        Dictionary containing workflow results
    """
    # Ensure database exists
    if not os.path.exists(db_path) or os.path.getsize(db_path) == 0:
        print(f"Database at {db_path} missing or empty.")
        return {"final_error": f"Database not found at {db_path}"}
    
    # Initialize shared store
    shared = {
        "db_path": db_path,
        "natural_query": natural_query,
        "max_debug_attempts": max_debug_retries,
        "debug_attempts": 0,
        "final_result": None,
        "final_error": None,
        "result_columns": [],
        "execution_error": None
    }
    
    # Display workflow information
    print(f"\n{'='*50}")
    print(f"TEXT-TO-SQL WORKFLOW")
    print(f"{'='*50}")
    print(f"Query: '{natural_query}'")
    print(f"Database: {db_path}")
    print(f"Max Debug Retries: {max_debug_retries}")
    print(f"Debug Loop: {'Enabled' if use_debug_loop else 'Disabled'}")
    print(f"{'='*50}")
    
    # Create and run flow
    if use_debug_loop:
        flow = create_text_to_sql_flow()
    else:
        from flow import create_simple_text_to_sql_flow
        flow = create_simple_text_to_sql_flow()
    
    try:
        flow.run(shared)
    except Exception as e:
        print(f"Workflow execution error: {e}")
        shared["final_error"] = f"Workflow execution failed: {e}"
    
    # Display final results
    print(f"\n{'='*50}")
    if shared.get("final_error"):
        print("WORKFLOW COMPLETED WITH ERROR")
        print(f"Error: {shared['final_error']}")
    elif shared.get("final_result") is not None:
        print("WORKFLOW COMPLETED SUCCESSFULLY")
        print("Results displayed above.")
    else:
        print("WORKFLOW COMPLETED (UNKNOWN STATE)")
    print(f"{'='*50}")
    
    return shared

def main():
    """Main entry point for the application."""
    # Check for OpenAI API key
    if not os.getenv("OPENAI_API_KEY"):
        print("Error: OPENAI_API_KEY environment variable not set.")
        print("Please set your OpenAI API key:")
        print("export OPENAI_API_KEY='your-api-key-here'")
        sys.exit(1)
    
    # Get query from command line arguments or use default
    if len(sys.argv) > 1:
        query = " ".join(sys.argv[1:])
    else:
        query = "Show me the total number of customers by city"
    
    # Run the workflow
    try:
        result = run_text_to_sql(query)
        
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
