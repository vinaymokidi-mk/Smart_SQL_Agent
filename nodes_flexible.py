import sqlite3
import time
from typing import Any, Tuple, List
from pocketflow import Node
from utils import call_llm, parse_sql_from_yaml, validate_sql_query, format_query_results
from data_manager import data_manager

class GetSchema(Node):
    """
    Node to retrieve database schema information for LLM context.
    Works with any data source managed by DataSourceManager.
    """
    
    def prep(self, shared: dict) -> str:
        """Read data source name from shared store."""
        return shared.get("source_name", data_manager.get_active_source())
    
    def exec(self, source_name: str) -> str:
        """
        Get schema information from the specified data source.
        
        Args:
            source_name: Name of the data source
            
        Returns:
            Formatted schema string with table and column information
        """
        if not source_name:
            raise ValueError("No data source specified and no active source found")
        
        try:
            schema = data_manager.get_schema(source_name)
            return schema
        except Exception as e:
            raise ValueError(f"Could not retrieve schema from '{source_name}': {e}")
    
    def post(self, shared: dict, prep_res: str, exec_res: str) -> None:
        """Store schema in shared store and display it."""
        shared["schema"] = exec_res
        shared["source_name"] = prep_res
        
        print(f"\n===== DATABASE SCHEMA ({prep_res}) =====\n")
        print(exec_res)
        print("\n===========================\n")

class GenerateSQL(Node):
    """
    Node to convert natural language query to SQL using LLM.
    Enhanced to work with any data source type.
    """
    
    def __init__(self, max_retries: int = 3, wait: int = 1):
        super().__init__(max_retries=max_retries, wait=wait)
    
    def prep(self, shared: dict) -> Tuple[str, str, str]:
        """Read natural query, schema, and source info from shared store."""
        return shared["natural_query"], shared["schema"], shared.get("source_name", "unknown")
    
    def exec(self, prep_res: Tuple[str, str, str]) -> str:
        """
        Generate SQL query from natural language using LLM.
        
        Args:
            prep_res: Tuple of (natural_query, schema, source_name)
            
        Returns:
            Generated SQL query string
        """
        natural_query, schema, source_name = prep_res
        
        # Get source type for better context
        source_type = "database"
        try:
            if source_name in data_manager.config["data_sources"]:
                source_config = data_manager.config["data_sources"][source_name]
                source_type = source_config["type"]
        except:
            pass
        
        prompt = f"""
You are a SQL expert. Convert the following natural language question into a SQL query.

Data Source: {source_name} ({source_type})
Database Schema:
{schema}

Question: "{natural_query}"

Rules:
1. Only generate SELECT queries (no INSERT, UPDATE, DELETE, DROP, etc.)
2. Use proper SQLite syntax (compatible with most databases)
3. Include appropriate JOINs if needed
4. Use meaningful column aliases
5. Handle NULL values appropriately
6. Be specific about table and column names from the schema
7. Return ONLY a YAML block with the SQL query

Respond with:
```yaml
sql: |
  SELECT ...
```

SQL Query:"""
        
        llm_response = call_llm(prompt)
        sql_query = parse_sql_from_yaml(llm_response)
        
        # Validate the generated SQL
        if not validate_sql_query(sql_query):
            raise ValueError("Generated SQL query failed security validation")
        
        return sql_query
    
    def exec_fallback(self, prep_res: Tuple[str, str, str], exc: Exception) -> str:
        """Provide fallback SQL for common queries."""
        natural_query, schema, source_name = prep_res
        
        # Simple fallback patterns
        query_lower = natural_query.lower()
        
        if "count" in query_lower or "how many" in query_lower:
            return "SELECT COUNT(*) as count FROM (SELECT 1 LIMIT 1)"
        elif "list" in query_lower or "show" in query_lower or "all" in query_lower:
            # Try to find a table name from schema
            lines = schema.split('\n')
            table_name = None
            for line in lines:
                if line.startswith('Table:'):
                    table_name = line.split('Table:')[1].strip()
                    break
            
            if table_name:
                return f"SELECT * FROM {table_name} LIMIT 10"
            else:
                return "SELECT 1 as result"
        else:
            return "SELECT 1 as result"
    
    def post(self, shared: dict, prep_res: Tuple[str, str, str], exec_res: str) -> None:
        """Store generated SQL and reset debug attempts."""
        shared["generated_sql"] = exec_res
        shared["debug_attempts"] = 0
        
        print(f"\n===== GENERATED SQL (Attempt {shared.get('debug_attempts', 0) + 1}) =====\n")
        print(exec_res)
        print("\n==========================================\n")

class ExecuteSQL(Node):
    """
    Node to execute SQL query against any data source.
    Enhanced to work with DataSourceManager connections.
    """
    
    def prep(self, shared: dict) -> Tuple[str, str]:
        """Read source name and SQL query from shared store."""
        source_name = shared.get("source_name", data_manager.get_active_source())
        return source_name, shared["generated_sql"]
    
    def exec(self, prep_res: Tuple[str, str]) -> Tuple[bool, Any, List[str]]:
        """
        Execute SQL query against the data source.
        
        Args:
            prep_res: Tuple of (source_name, sql_query)
            
        Returns:
            Tuple of (success, results_or_error, column_names)
        """
        source_name, sql_query = prep_res
        
        if not source_name:
            return (False, "No data source specified", [])
        
        try:
            conn = data_manager.get_connection(source_name)
            cursor = conn.cursor()
            
            start_time = time.time()
            cursor.execute(sql_query)
            
            # Check if it's a SELECT query
            sql_upper = sql_query.strip().upper()
            is_select = sql_upper.startswith(("SELECT", "WITH"))
            
            if is_select:
                results = cursor.fetchall()
                column_names = [desc[0] for desc in cursor.description] if cursor.description else []
            else:
                conn.commit()
                results = f"Query executed successfully. Rows affected: {cursor.rowcount}"
                column_names = []
            
            duration = time.time() - start_time
            print(f"SQL executed in {duration:.3f} seconds.")
            
            conn.close()
            return (True, results, column_names)
            
        except sqlite3.Error as e:
            error_msg = f"SQLite Error: {str(e)}"
            print(f"SQL execution failed: {error_msg}")
            return (False, error_msg, [])
            
        except Exception as e:
            error_msg = f"Database Error: {str(e)}"
            print(f"SQL execution failed: {error_msg}")
            return (False, error_msg, [])
    
    def post(self, shared: dict, prep_res: Tuple[str, str], exec_res: Tuple[bool, Any, List[str]]) -> str:
        """
        Process execution results and decide next action.
        
        Returns:
            Action string: None for success, "error_retry" for retry, None for max attempts reached
        """
        success, result_or_error, column_names = exec_res
        
        if success:
            # Store successful results
            shared["final_result"] = result_or_error
            shared["result_columns"] = column_names
            
            print("\n===== SQL EXECUTION SUCCESS =====\n")
            
            if isinstance(result_or_error, list):
                formatted_results = format_query_results(result_or_error, column_names)
                print(formatted_results)
            else:
                print(result_or_error)
            
            print("\n==================================\n")
            return None  # End flow
            
        else:
            # Handle execution failure
            shared["execution_error"] = result_or_error
            shared["debug_attempts"] = shared.get("debug_attempts", 0) + 1
            max_attempts = shared.get("max_debug_attempts", 3)
            
            print(f"\n===== SQL EXECUTION FAILED (Attempt {shared['debug_attempts']}) =====\n")
            print(f"Error: {shared['execution_error']}")
            print("==========================================\n")
            
            if shared["debug_attempts"] >= max_attempts:
                print(f"Maximum debug attempts ({max_attempts}) reached. Stopping.")
                shared["final_error"] = f"Failed to execute SQL after {max_attempts} attempts. Last error: {shared['execution_error']}"
                return None  # End flow with error
            else:
                print("Attempting to debug the SQL...")
                return "error_retry"  # Go to debug node

class DebugSQL(Node):
    """
    Node to analyze SQL errors and generate corrected queries.
    Enhanced to work with any data source.
    """
    
    def __init__(self, max_retries: int = 2, wait: int = 1):
        super().__init__(max_retries=max_retries, wait=wait)
    
    def prep(self, shared: dict) -> Tuple[str, str, str, str, str]:
        """Read all necessary information for debugging."""
        return (
            shared.get("natural_query"),
            shared.get("schema"),
            shared.get("generated_sql"),
            shared.get("execution_error"),
            shared.get("source_name", "unknown")
        )
    
    def exec(self, prep_res: Tuple[str, str, str, str, str]) -> str:
        """
        Analyze error and generate corrected SQL query.
        
        Args:
            prep_res: Tuple of (natural_query, schema, failed_sql, error_message, source_name)
            
        Returns:
            Corrected SQL query string
        """
        natural_query, schema, failed_sql, error_message, source_name = prep_res
        
        prompt = f"""
You are a SQL debugging expert. The following SQLite query failed with an error.

Data Source: {source_name}
Original Question: "{natural_query}"

Database Schema:
{schema}

Failed SQL Query:
```sql
{failed_sql}
```

Error Message: "{error_message}"

Please analyze the error and provide a corrected SQL query that will work with SQLite.

Rules:
1. Only generate SELECT queries (no INSERT, UPDATE, DELETE, DROP, etc.)
2. Use proper SQLite syntax
3. Fix the specific error mentioned
4. Maintain the original intent of the query
5. Be specific about table and column names from the schema
6. Return ONLY a YAML block with the corrected SQL

Respond with:
```yaml
sql: |
  SELECT ... -- corrected query
```

Corrected SQL Query:"""
        
        llm_response = call_llm(prompt)
        corrected_sql = parse_sql_from_yaml(llm_response)
        
        # Validate the corrected SQL
        if not validate_sql_query(corrected_sql):
            raise ValueError("Corrected SQL query failed security validation")
        
        return corrected_sql
    
    def exec_fallback(self, prep_res: Tuple[str, str, str, str, str], exc: Exception) -> str:
        """Provide a simple fallback query if debugging fails."""
        return "SELECT 1 as debug_fallback"
    
    def post(self, shared: dict, prep_res: Tuple[str, str, str, str, str], exec_res: str) -> None:
        """Store corrected SQL and clear error state."""
        shared["generated_sql"] = exec_res
        shared.pop("execution_error", None)  # Clear previous error
        
        print(f"\n===== REVISED SQL (Attempt {shared.get('debug_attempts', 0) + 1}) =====\n")
        print(exec_res)
        print("\n==========================================\n")
