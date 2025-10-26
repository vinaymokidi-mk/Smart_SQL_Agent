import os
import sqlite3
import yaml
import re
from typing import Optional, Tuple, Any, List
import config

def call_llm(prompt: str, model: str = None, api_key: Optional[str] = None) -> str:
    """
    Call Gemini AI with the given prompt.
    
    Args:
        prompt: The input prompt for the LLM
        model: The model to use (default: gemini-1.5-flash)
        api_key: Optional API key (overrides environment variable)
    
    Returns:
        The LLM response as a string
        
    Raises:
        ValueError: If API key is not provided
        Exception: If API call fails
    """
    # Get API key from: parameter > environment variable > config file
    key = api_key or os.getenv("GEMINI_API_KEY") or config.get_gemini_api_key()
    if not key:
        raise ValueError("Gemini API key not configured. Please check config.py or set GEMINI_API_KEY environment variable.")
    
    # Get model from config if not specified
    if model is None:
        model = config.GEMINI_MODEL
    
    try:
        # Import Google's Generative AI library
        import google.generativeai as genai
        
        # Configure the API key
        genai.configure(api_key=key)
        
        # Create the model
        model_instance = genai.GenerativeModel(model)
        
        # Generate content
        response = model_instance.generate_content(
            prompt,
            generation_config=genai.GenerationConfig(
                temperature=config.LLM_TEMPERATURE,
                max_output_tokens=config.LLM_MAX_TOKENS,
            )
        )
        
        return response.text
        
    except ImportError:
        raise Exception("Google Generative AI library not installed. Run: pip install google-generativeai")
    except Exception as e:
        error_msg = str(e)
        if '400' in error_msg or 'invalid' in error_msg.lower() or 'api_key' in error_msg.lower():
            raise ValueError("Invalid API key. Please check your Gemini API key at https://aistudio.google.com/app/apikey")
        elif 'quota' in error_msg.lower() or 'limit' in error_msg.lower():
            raise Exception("API quota exceeded or rate limit hit. Please wait a moment or check your quota at https://aistudio.google.com/")
        elif 'blocked' in error_msg.lower() or 'safety' in error_msg.lower():
            raise Exception("Content blocked by safety filters. Try rephrasing your question.")
        else:
            raise Exception(f"Gemini API call failed: {error_msg}")

def get_db_connection(db_path: str) -> sqlite3.Connection:
    """
    Create a database connection to SQLite database.
    
    Args:
        db_path: Path to the SQLite database file
    
    Returns:
        SQLite connection object
        
    Raises:
        FileNotFoundError: If database file doesn't exist
        Exception: If connection fails
    """
    if not os.path.exists(db_path):
        raise FileNotFoundError(f"Database file not found: {db_path}")
    
    try:
        conn = sqlite3.connect(db_path)
        # Test the connection
        conn.execute("SELECT 1")
        return conn
    except Exception as e:
        raise Exception(f"Failed to connect to database: {str(e)}")

def clean_column_name(col_name: str) -> str:
    """
    Clean column names for SQL compatibility.
    
    Args:
        col_name: Original column name
        
    Returns:
        SQL-safe column name
    """
    # Remove special characters and replace spaces with underscores
    cleaned = re.sub(r'[^a-zA-Z0-9_]', '_', str(col_name))
    
    # Remove consecutive underscores
    cleaned = re.sub(r'_+', '_', cleaned)
    
    # Remove leading/trailing underscores
    cleaned = cleaned.strip('_')
    
    # If starts with number, prepend 'col_'
    if cleaned and cleaned[0].isdigit():
        cleaned = f"col_{cleaned}"
    
    # If empty after cleaning, use a default
    if not cleaned:
        cleaned = "unnamed_column"
    
    # Convert to lowercase for consistency
    return cleaned.lower()

def parse_sql_from_yaml(llm_response: str) -> str:
    """
    Parse SQL query from LLM YAML response.
    
    Args:
        llm_response: Raw LLM response containing YAML
    
    Returns:
        Extracted SQL query string
    
    Raises:
        ValueError: If YAML parsing fails or SQL key is missing
    """
    try:
        # Extract YAML block from response
        if "```yaml" in llm_response:
            yaml_str = llm_response.split("```yaml")[1].split("```")[0].strip()
        else:
            yaml_str = llm_response.strip()
        
        # Parse YAML
        structured_result = yaml.safe_load(yaml_str)
        
        if not isinstance(structured_result, dict) or "sql" not in structured_result:
            raise ValueError("Invalid YAML structure: missing 'sql' key")
        
        sql_query = structured_result["sql"].strip().rstrip(';')
        return sql_query
        
    except yaml.YAMLError as e:
        raise ValueError(f"YAML parsing error: {e}")
    except Exception as e:
        raise ValueError(f"Error parsing SQL from response: {e}")

def validate_sql_query(sql_query: str) -> bool:
    """
    Comprehensive validation of SQL query to prevent injection attacks.
    
    Args:
        sql_query: SQL query string to validate
    
    Returns:
        True if query appears safe, False otherwise
    """
    if not sql_query or not isinstance(sql_query, str):
        return False
    
    sql_upper = sql_query.upper().strip()
    
    # Check if empty
    if not sql_upper:
        return False
    
    # Must be a SELECT query
    if not sql_upper.startswith(("SELECT", "WITH")):
        return False
    
    # Check for dangerous operations
    dangerous_keywords = [
        "DROP", "DELETE", "UPDATE", "INSERT", "ALTER", 
        "CREATE", "TRUNCATE", "EXEC", "EXECUTE", "PRAGMA",
        "ATTACH", "DETACH"
    ]
    
    for keyword in dangerous_keywords:
        # Use word boundaries to avoid false positives
        pattern = r'\b' + keyword + r'\b'
        if re.search(pattern, sql_upper):
            return False
    
    # Check for suspicious patterns
    suspicious_patterns = [
        (r'--', "SQL comment"),
        (r'/\*', "Block comment start"),
        (r'\*/', "Block comment end"),
        (r'xp_', "Extended procedure"),
        (r'sp_', "System procedure"),
        (r';.*\S', "Multiple statements"),  # Semicolon followed by more content
    ]
    
    for pattern, _ in suspicious_patterns:
        if re.search(pattern, sql_upper):
            return False
    
    return True

def format_query_results(results: List[Tuple], column_names: List[str]) -> str:
    """
    Format query results for display.
    
    Args:
        results: List of result tuples
        column_names: List of column names
    
    Returns:
        Formatted string for display
    """
    if not results:
        return "(No results found)"
    
    if not column_names:
        return str(results)
    
    # Calculate column widths
    col_widths = []
    for i, col_name in enumerate(column_names):
        max_width = len(col_name)
        for row in results:
            if i < len(row):
                max_width = max(max_width, len(str(row[i])))
        col_widths.append(max_width)
    
    # Create header
    header_parts = []
    separator_parts = []
    for i, (col_name, width) in enumerate(zip(column_names, col_widths)):
        header_parts.append(col_name.ljust(width))
        separator_parts.append("-" * width)
    
    header = " | ".join(header_parts)
    separator = " | ".join(separator_parts)
    
    # Create rows
    rows = []
    for row in results:
        row_parts = []
        for i, width in enumerate(col_widths):
            value = str(row[i]) if i < len(row) else ""
            row_parts.append(value.ljust(width))
        rows.append(" | ".join(row_parts))
    
    return "\n".join([header, separator] + rows)

def get_schema_from_db(db_path: str) -> str:
    """
    Extract database schema information.
    
    Args:
        db_path: Path to SQLite database
        
    Returns:
        Formatted schema string
        
    Raises:
        Exception: If schema extraction fails
    """
    try:
        conn = get_db_connection(db_path)
        cursor = conn.cursor()
        
        # Get all table names (excluding SQLite internal tables)
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';")
        tables = cursor.fetchall()
        
        if not tables:
            raise Exception("No tables found in database")
        
        schema_parts = []
        for table_tuple in tables:
            table_name = table_tuple[0]
            schema_parts.append(f"Table: {table_name}")
            
            # Get column information
            cursor.execute(f"PRAGMA table_info({table_name});")
            columns = cursor.fetchall()
            
            if not columns:
                schema_parts.append("  (No columns found)")
                continue
            
            for col in columns:
                col_name = col[1]
                col_type = col[2] if col[2] else "ANY"
                nullable = "NOT NULL" if col[3] else "NULL"
                schema_parts.append(f"  - {col_name} ({col_type}, {nullable})")
            
            # Get sample values for better context
            try:
                cursor.execute(f"SELECT * FROM {table_name} LIMIT 1")
                sample = cursor.fetchone()
                if sample:
                    schema_parts.append(f"  Sample: {len(sample)} columns")
            except:
                pass
            
            schema_parts.append("")  # Empty line between tables
        
        conn.close()
        return "\n".join(schema_parts).strip()
        
    except Exception as e:
        raise Exception(f"Failed to extract schema: {str(e)}")

def process_uploaded_file(file_path: str, file_type: str = None) -> dict:
    """
    Process uploaded file and convert to SQLite database.
    
    Args:
        file_path: Path to uploaded file
        file_type: File type ('xlsx', 'xls', 'csv', or auto-detect)
        
    Returns:
        Dictionary with success status, db_path, schema, and metadata
        
    Raises:
        Exception: If file processing fails
    """
    import pandas as pd
    
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
    
    # Auto-detect file type if not provided
    if not file_type:
        file_ext = os.path.splitext(file_path)[1].lower()
        file_type = file_ext.lstrip('.')
    
    try:
        # Read file based on type
        if file_type in ['xlsx', 'xls']:
            # Check if it's a multi-sheet Excel file
            excel_file = pd.ExcelFile(file_path)
            sheet_names = excel_file.sheet_names
            
            if len(sheet_names) == 1:
                # Single sheet - read as one table
                df = pd.read_excel(file_path)
                dfs = {'data': df}
            else:
                # Multiple sheets - each sheet becomes a table
                dfs = {}
                for sheet in sheet_names:
                    df = pd.read_excel(file_path, sheet_name=sheet)
                    # Clean sheet name for use as table name
                    table_name = clean_column_name(sheet)
                    dfs[table_name] = df
                    
        elif file_type == 'csv':
            df = pd.read_csv(file_path)
            dfs = {'data': df}
        else:
            raise ValueError(f"Unsupported file type: {file_type}")
        
        # Validate data
        total_rows = 0
        total_cols = 0
        for table_name, df in dfs.items():
            if df.empty:
                raise ValueError(f"Table '{table_name}' is empty")
            
            # Clean column names
            df.columns = [clean_column_name(col) for col in df.columns]
            
            # Check for duplicate columns
            if len(df.columns) != len(set(df.columns)):
                raise ValueError(f"Duplicate column names found in table '{table_name}'")
            
            dfs[table_name] = df
            total_rows += len(df)
            total_cols += len(df.columns)
        
        # Create temporary SQLite database
        import tempfile
        import uuid
        
        temp_db_path = os.path.join(
            tempfile.gettempdir() if not os.path.exists('uploads') else 'uploads',
            f"temp_{uuid.uuid4().hex[:8]}.db"
        )
        
        # Save to SQLite
        conn = sqlite3.connect(temp_db_path)
        for table_name, df in dfs.items():
            df.to_sql(table_name, conn, index=False, if_exists='replace')
        conn.close()
        
        # Get schema
        schema = get_schema_from_db(temp_db_path)
        
        return {
            'success': True,
            'db_path': temp_db_path,
            'schema': schema,
            'tables': list(dfs.keys()),
            'total_rows': total_rows,
            'total_columns': total_cols,
            'metadata': {
                table: {
                    'rows': len(df),
                    'columns': list(df.columns)
                }
                for table, df in dfs.items()
            }
        }
        
    except pd.errors.EmptyDataError:
        raise ValueError("File is empty or contains no data")
    except pd.errors.ParserError as e:
        raise ValueError(f"Failed to parse file: {str(e)}")
    except Exception as e:
        raise Exception(f"Failed to process file: {str(e)}")

if __name__ == "__main__":
    # Test the LLM call
    test_prompt = "What is the capital of France?"
    try:
        response = call_llm(test_prompt)
        print(f"LLM Response: {response}")
    except Exception as e:
        print(f"Error calling LLM: {e}")
        print("Make sure OPENAI_API_KEY environment variable is set")
