"""
SQL Agent Web Application - Fixed Version
Provides a web interface for natural language to SQL conversion with dynamic API key management
"""

from flask import Flask, render_template, request, jsonify, session
import os
import json
import pandas as pd
import sqlite3
from werkzeug.utils import secure_filename
import tempfile
import uuid
import re
from typing import Dict, Any, List, Tuple
from openai import OpenAI
import yaml

app = Flask(__name__)
app.secret_key = os.urandom(24)  # Generate secure random secret key

# Configuration
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'xlsx', 'xls', 'csv'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Ensure upload directory exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# ===============================
# Utility Functions
# ===============================

def allowed_file(filename: str) -> bool:
    """Check if file extension is allowed."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def clean_column_name(col_name: str) -> str:
    """Clean column names for SQL compatibility."""
    cleaned = re.sub(r'[^a-zA-Z0-9_]', '_', str(col_name))
    if cleaned[0].isdigit():
        cleaned = f"col_{cleaned}"
    return cleaned.lower()


def get_session_data() -> dict:
    """Get or create session data."""
    if 'session_id' not in session:
        session['session_id'] = str(uuid.uuid4())
        session['api_key'] = None
        session['api_key_valid'] = False
        session['current_file'] = None
        session['file_name'] = None
        session['schema'] = None
        session['db_path'] = None
    return session


def test_openai_connection(api_key: str) -> Tuple[bool, str]:
    """
    Test OpenAI API key by making a simple request.
    
    Returns:
        Tuple of (success: bool, message: str)
    """
    try:
        client = OpenAI(api_key=api_key)
        
        # Make a minimal test request
        response = client.chat.completions.create(
            model="gpt-4o-mini",  # Use cheaper model for testing
            messages=[{"role": "user", "content": "Say 'OK' if you can read this."}],
            max_tokens=10,
            temperature=0
        )
        
        if response and response.choices and len(response.choices) > 0:
            return True, "API key validated successfully! Connection established."
        else:
            return False, "API key test returned invalid response."
            
    except Exception as e:
        error_msg = str(e)
        if '401' in error_msg or 'Incorrect API key' in error_msg:
            return False, "Invalid API key. Please check your OpenAI API key."
        elif 'rate_limit' in error_msg.lower():
            return False, "Rate limit exceeded. Your key is valid but currently rate-limited."
        elif 'insufficient_quota' in error_msg.lower():
            return False, "API key is valid but has insufficient quota/credits."
        else:
            return False, f"Connection test failed: {error_msg}"


def call_llm(prompt: str, api_key: str, model: str = "gpt-4o-mini") -> str:
    """
    Call OpenAI LLM with the given prompt.
    
    Args:
        prompt: The input prompt for the LLM
        api_key: OpenAI API key
        model: The model to use
    
    Returns:
        The LLM response as a string
    """
    client = OpenAI(api_key=api_key)
    
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.1
    )
    
    return response.choices[0].message.content


def parse_sql_from_response(llm_response: str) -> str:
    """
    Parse SQL query from LLM response (YAML or plain SQL).
    
    Args:
        llm_response: Raw LLM response
    
    Returns:
        Extracted SQL query string
    """
    try:
        # Try YAML parsing first
        if "```yaml" in llm_response:
            yaml_str = llm_response.split("```yaml")[1].split("```")[0].strip()
            structured_result = yaml.safe_load(yaml_str)
            if isinstance(structured_result, dict) and "sql" in structured_result:
                return structured_result["sql"].strip().rstrip(';')
        
        # Try to extract SQL from code blocks
        if "```sql" in llm_response:
            sql = llm_response.split("```sql")[1].split("```")[0].strip()
            return sql.rstrip(';')
        
        if "```" in llm_response:
            sql = llm_response.split("```")[1].split("```")[0].strip()
            # Remove language identifier if present
            if sql.startswith(('sql', 'SQL')):
                sql = sql[3:].strip()
            return sql.rstrip(';')
        
        # If no code blocks, look for SELECT statement
        lines = llm_response.split('\n')
        sql_lines = []
        in_sql = False
        for line in lines:
            if 'SELECT' in line.upper() or in_sql:
                in_sql = True
                sql_lines.append(line)
                if ';' in line:
                    break
        
        if sql_lines:
            return '\n'.join(sql_lines).strip().rstrip(';')
        
        # Last resort: return cleaned response
        return llm_response.strip().rstrip(';')
        
    except Exception as e:
        raise ValueError(f"Error parsing SQL from response: {e}")


def validate_sql_query(sql_query: str) -> Tuple[bool, str]:
    """
    Validate SQL query for security.
    
    Returns:
        Tuple of (is_valid: bool, error_message: str)
    """
    sql_upper = sql_query.upper().strip()
    
    # Check for dangerous operations
    dangerous_keywords = [
        'DROP', 'DELETE', 'UPDATE', 'INSERT', 'ALTER',
        'CREATE', 'TRUNCATE', 'EXEC', 'EXECUTE', 'PRAGMA'
    ]
    
    for keyword in dangerous_keywords:
        if re.search(r'\b' + keyword + r'\b', sql_upper):
            return False, f"Query contains prohibited keyword: {keyword}"
    
    # Must start with SELECT or WITH (for CTEs)
    if not (sql_upper.startswith('SELECT') or sql_upper.startswith('WITH')):
        return False, "Only SELECT queries are allowed"
    
    # Check for suspicious patterns
    suspicious_patterns = ['--', '/*', '*/', 'xp_', 'sp_']
    for pattern in suspicious_patterns:
        if pattern in sql_query:
            return False, f"Query contains suspicious pattern: {pattern}"
    
    return True, ""


# ===============================
# File Processing Functions
# ===============================

def process_uploaded_file(file_path: str, filename: str, session_id: str) -> Dict[str, Any]:
    """
    Process uploaded file and create SQLite database.
    
    Returns:
        Dictionary with success status and file information
    """
    try:
        # Read file based on extension
        file_ext = filename.rsplit('.', 1)[1].lower()
        
        if file_ext == 'csv':
            df = pd.read_csv(file_path)
        else:  # xlsx or xls
            df = pd.read_excel(file_path)
        
        # Clean column names
        original_columns = list(df.columns)
        df.columns = [clean_column_name(col) for col in df.columns]
        
        # Create column mapping for reference
        column_mapping = dict(zip(df.columns, original_columns))
        
        # Create temporary SQLite database
        db_path = os.path.join(UPLOAD_FOLDER, f"temp_{session_id}.db")
        
        # Remove old database if exists
        if os.path.exists(db_path):
            os.remove(db_path)
        
        # Save to SQLite
        conn = sqlite3.connect(db_path)
        table_name = 'data'
        df.to_sql(table_name, conn, index=False, if_exists='replace')
        conn.close()
        
        # Get schema
        schema = get_database_schema(db_path)
        
        # Get data preview
        preview = df.head(10).to_dict('records')
        
        return {
            'success': True,
            'db_path': db_path,
            'table_name': table_name,
            'schema': schema,
            'rows': len(df),
            'columns': list(df.columns),
            'original_columns': original_columns,
            'column_mapping': column_mapping,
            'preview': preview,
            'message': f'Successfully loaded {len(df)} rows with {len(df.columns)} columns'
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': f'Error processing file: {str(e)}'
        }


def get_database_schema(db_path: str) -> str:
    """
    Extract and format database schema.
    
    Args:
        db_path: Path to SQLite database
    
    Returns:
        Formatted schema string
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Get all tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';")
        tables = cursor.fetchall()
        
        schema_parts = []
        for table_tuple in tables:
            table_name = table_tuple[0]
            schema_parts.append(f"Table: {table_name}")
            
            # Get column information
            cursor.execute(f"PRAGMA table_info({table_name});")
            columns = cursor.fetchall()
            
            for col in columns:
                col_name = col[1]
                col_type = col[2]
                nullable = "NOT NULL" if col[3] else "NULL"
                schema_parts.append(f"  - {col_name} ({col_type}, {nullable})")
            
            # Get sample data to help with context
            cursor.execute(f"SELECT * FROM {table_name} LIMIT 3;")
            sample_rows = cursor.fetchall()
            if sample_rows:
                schema_parts.append(f"  Sample data (first 3 rows):")
                for row in sample_rows:
                    schema_parts.append(f"    {row}")
            
            schema_parts.append("")
        
        return "\n".join(schema_parts).strip()
        
    finally:
        conn.close()


def execute_sql_query(db_path: str, sql_query: str) -> Dict[str, Any]:
    """
    Execute SQL query against database.
    
    Returns:
        Dictionary with query results or error
    """
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute(sql_query)
        results = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description] if cursor.description else []
        
        conn.close()
        
        return {
            'success': True,
            'results': results,
            'columns': columns,
            'row_count': len(results)
        }
        
    except sqlite3.Error as e:
        return {
            'success': False,
            'error': f'SQL execution error: {str(e)}'
        }
    except Exception as e:
        return {
            'success': False,
            'error': f'Unexpected error: {str(e)}'
        }


def generate_sql_from_natural_language(natural_query: str, schema: str, api_key: str) -> Dict[str, Any]:
    """
    Generate SQL from natural language using LLM.
    
    Returns:
        Dictionary with generated SQL or error
    """
    try:
        prompt = f"""You are a SQL expert. Convert the following natural language question into a SQLite SQL query.

Database Schema:
{schema}

Natural Language Question: "{natural_query}"

Important Rules:
1. Generate ONLY SELECT queries (no INSERT, UPDATE, DELETE, DROP, etc.)
2. Use proper SQLite syntax
3. Use appropriate JOINs, WHERE clauses, GROUP BY, ORDER BY as needed
4. Return ONLY the SQL query without any explanations
5. Do not use markdown formatting or code blocks in your response
6. Make the query as accurate as possible based on the question

Generate the SQL query now:"""
        
        llm_response = call_llm(prompt, api_key)
        sql_query = parse_sql_from_response(llm_response)
        
        # Validate the generated SQL
        is_valid, error_msg = validate_sql_query(sql_query)
        if not is_valid:
            return {
                'success': False,
                'error': f'Generated SQL failed validation: {error_msg}'
            }
        
        return {
            'success': True,
            'sql': sql_query
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': f'SQL generation failed: {str(e)}'
        }


# ===============================
# Flask Routes
# ===============================

@app.route('/')
def index():
    """Main page."""
    session_data = get_session_data()
    return render_template('index_fixed.html')


@app.route('/set_api_key', methods=['POST'])
def set_api_key():
    """Set and validate OpenAI API key."""
    session_data = get_session_data()
    
    data = request.get_json()
    api_key = data.get('api_key', '').strip()
    
    if not api_key:
        return jsonify({'success': False, 'error': 'API key is required'})
    
    if not api_key.startswith('sk-'):
        return jsonify({'success': False, 'error': 'Invalid API key format. OpenAI keys start with "sk-"'})
    
    # Test the API key
    success, message = test_openai_connection(api_key)
    
    if success:
        session['api_key'] = api_key
        session['api_key_valid'] = True
        return jsonify({'success': True, 'message': message})
    else:
        session['api_key'] = None
        session['api_key_valid'] = False
        return jsonify({'success': False, 'error': message})


@app.route('/upload', methods=['POST'])
def upload_file():
    """Handle file upload and processing."""
    session_data = get_session_data()
    
    if 'file' not in request.files:
        return jsonify({'success': False, 'error': 'No file provided'})
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'success': False, 'error': 'No file selected'})
    
    if not allowed_file(file.filename):
        return jsonify({'success': False, 'error': 'Invalid file type. Please upload .xlsx, .xls, or .csv files.'})
    
    # Save file
    filename = secure_filename(file.filename)
    timestamp = uuid.uuid4().hex[:8]
    filename = f"{timestamp}_{filename}"
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(file_path)
    
    # Process the file
    result = process_uploaded_file(file_path, file.filename, session['session_id'])
    
    if result['success']:
        # Store in session
        session['current_file'] = file_path
        session['file_name'] = file.filename
        session['schema'] = result['schema']
        session['db_path'] = result['db_path']
        session['table_name'] = result['table_name']
        session['columns'] = result['columns']
        
        return jsonify({
            'success': True,
            'message': result['message'],
            'schema': result['schema'],
            'preview': result['preview'],
            'columns': result['columns'],
            'rows': result['rows']
        })
    else:
        # Clean up file on error
        if os.path.exists(file_path):
            os.remove(file_path)
        return jsonify({'success': False, 'error': result['error']})


@app.route('/query', methods=['POST'])
def process_query():
    """Process natural language query."""
    session_data = get_session_data()
    
    data = request.get_json()
    natural_query = data.get('query', '').strip()
    
    # Validation
    if not natural_query:
        return jsonify({'success': False, 'error': 'Query is required'})
    
    if not session_data.get('api_key_valid'):
        return jsonify({'success': False, 'error': 'Please set a valid OpenAI API key first'})
    
    if not session_data.get('db_path'):
        return jsonify({'success': False, 'error': 'Please upload a file first'})
    
    try:
        # Generate SQL from natural language
        sql_result = generate_sql_from_natural_language(
            natural_query,
            session_data['schema'],
            session_data['api_key']
        )
        
        if not sql_result['success']:
            return jsonify({'success': False, 'error': sql_result['error']})
        
        # Execute the SQL query
        query_result = execute_sql_query(session_data['db_path'], sql_result['sql'])
        
        if not query_result['success']:
            return jsonify({
                'success': False,
                'error': query_result['error'],
                'sql': sql_result['sql']  # Return SQL even on error for debugging
            })
        
        return jsonify({
            'success': True,
            'sql': sql_result['sql'],
            'results': query_result['results'],
            'columns': query_result['columns'],
            'row_count': query_result['row_count']
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': f'Processing failed: {str(e)}'})


@app.route('/api_status')
def get_api_status():
    """Get current API and file status."""
    session_data = get_session_data()
    
    return jsonify({
        'api_key_set': session_data.get('api_key_valid', False),
        'file_uploaded': bool(session_data.get('db_path')),
        'file_name': session_data.get('file_name'),
        'session_id': session_data.get('session_id')
    })


@app.route('/schema')
def get_schema():
    """Get current database schema."""
    session_data = get_session_data()
    
    if not session_data.get('schema'):
        return jsonify({'success': False, 'error': 'No file uploaded'})
    
    return jsonify({
        'success': True,
        'schema': session_data['schema']
    })


@app.route('/test_query', methods=['POST'])
def test_query():
    """Test endpoint for debugging SQL queries."""
    session_data = get_session_data()
    
    data = request.get_json()
    sql_query = data.get('sql', '').strip()
    
    if not sql_query:
        return jsonify({'success': False, 'error': 'SQL query is required'})
    
    if not session_data.get('db_path'):
        return jsonify({'success': False, 'error': 'No database loaded'})
    
    # Validate query
    is_valid, error_msg = validate_sql_query(sql_query)
    if not is_valid:
        return jsonify({'success': False, 'error': error_msg})
    
    # Execute query
    result = execute_sql_query(session_data['db_path'], sql_query)
    return jsonify(result)


# ===============================
# Error Handlers
# ===============================

@app.errorhandler(413)
def request_entity_too_large(error):
    """Handle file too large error."""
    return jsonify({'success': False, 'error': 'File size exceeds 16MB limit'}), 413


@app.errorhandler(500)
def internal_server_error(error):
    """Handle internal server errors."""
    return jsonify({'success': False, 'error': 'Internal server error occurred'}), 500


# ===============================
# Main Entry Point
# ===============================

if __name__ == '__main__':
    print("=" * 60)
    print("🚀 SQL Agent Web Application Starting...")
    print("=" * 60)
    print("📊 Features:")
    print("   ✓ Dynamic OpenAI API key configuration with validation")
    print("   ✓ Excel/CSV file upload with automatic schema detection")
    print("   ✓ Natural language to SQL query conversion")
    print("   ✓ Real-time query execution with results display")
    print("=" * 60)
    print("🌐 Open your browser and navigate to:")
    print("   http://localhost:5000")
    print("=" * 60)
    print("⚠️  Press CTRL+C to stop the server")
    print("=" * 60)
    
    app.run(debug=True, host='0.0.0.0', port=5000)
