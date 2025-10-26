from pocketflow import Flow
from nodes_flexible import GetSchema, GenerateSQL, ExecuteSQL, DebugSQL

def create_text_to_sql_flow():
    """
    Creates the flexible text-to-SQL workflow with debug loop.
    
    Flow Structure:
    1. GetSchema -> GenerateSQL -> ExecuteSQL
    2. If ExecuteSQL fails: ExecuteSQL -> DebugSQL -> ExecuteSQL (loop)
    3. Loop continues until success or max attempts reached
    
    Returns:
        Flow: Configured PocketFlow workflow for any data source
    """
    # Create node instances
    get_schema_node = GetSchema()
    generate_sql_node = GenerateSQL(max_retries=3, wait=1)
    execute_sql_node = ExecuteSQL()
    debug_sql_node = DebugSQL(max_retries=2, wait=1)
    
    # Define main flow sequence
    get_schema_node >> generate_sql_node >> execute_sql_node
    
    # Define debug loop connections
    # If ExecuteSQL returns "error_retry", go to DebugSQL
    execute_sql_node - "error_retry" >> debug_sql_node
    
    # After debugging, go back to ExecuteSQL for retry
    debug_sql_node >> execute_sql_node
    
    # Create and return the flow
    text_to_sql_flow = Flow(start=get_schema_node)
    return text_to_sql_flow

def create_simple_text_to_sql_flow():
    """
    Creates a simplified text-to-SQL workflow without debug loop.
    Useful for testing or when debug functionality is not needed.
    
    Returns:
        Flow: Simple linear workflow for any data source
    """
    get_schema_node = GetSchema()
    generate_sql_node = GenerateSQL(max_retries=3, wait=1)
    execute_sql_node = ExecuteSQL()
    
    # Simple linear flow
    get_schema_node >> generate_sql_node >> execute_sql_node
    
    return Flow(start=get_schema_node)

if __name__ == "__main__":
    # Test flow creation
    flow = create_text_to_sql_flow()
    print("Flexible text-to-SQL flow created successfully!")
    print(f"Flow start node: {flow.start}")
    
    # Test simple flow creation
    simple_flow = create_simple_text_to_sql_flow()
    print("Simple flexible text-to-SQL flow created successfully!")
