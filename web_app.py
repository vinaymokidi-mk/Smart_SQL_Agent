from flask import Flask, render_template, request, jsonify, session
import os
import json
import sqlite3
from werkzeug.utils import secure_filename
from utils import (
    call_llm, parse_sql_from_yaml, validate_sql_query, 
    format_query_results, process_uploaded_file, get_schema_from_db,
    get_db_connection
)
import uuid
import traceback
import config

app = Flask(__name__)
app.secret_key = config.SECRET_KEY

# Configuration from config.py
UPLOAD_FOLDER = config.UPLOAD_FOLDER
ALLOWED_EXTENSIONS = config.ALLOWED_EXTENSIONS
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = config.MAX_FILE_SIZE

# Ensure upload directory exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    """Check if file has an allowed extension."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_session_data():
    """Get or create session data with proper initialization."""
    if 'session_id' not in session:
        session['session_id'] = str(uuid.uuid4())
        # Use configured Gemini API key by default
        session['api_key'] = config.get_gemini_api_key()
        session['db_path'] = None
        session['file_name'] = None
        session['schema'] = None
        session['tables'] = []
    return session

def execute_query(query, db_path):
    """
    Execute SQL query and return results with comprehensive error handling.
    
    Args:
        query: SQL query string
        db_path: Path to SQLite database
        
    Returns:
        Dictionary with success status, results, columns, and row count
    """
    try:
        # Validate query first
        if not validate_sql_query(query):
            return {
                'success': False,
                'error': 'Query failed security validation. Only SELECT queries are allowed.'
            }
        
        # Connect to database
        conn = get_db_connection(db_path)
        cursor = conn.cursor()
        
        try:
            # Execute query with timeout
            cursor.execute(query)
            
            # Check if it's a SELECT query
            sql_upper = query.strip().upper()
            is_select = sql_upper.startswith(("SELECT", "WITH"))
            
            if is_select:
                results = cursor.fetchall()
                columns = [desc[0] for desc in cursor.description] if cursor.description else []
                row_count = len(results)
            else:
                results = []
                columns = []
                row_count = 0
            
            return {
                'success': True,
                'results': results,
                'columns': columns,
                'row_count': row_count
            }
            
        except sqlite3.OperationalError as e:
            return {
                'success': False,
                'error': f'SQL execution error: {str(e)}'
            }
        except sqlite3.DatabaseError as e:
            return {
                'success': False,
                'error': f'Database error: {str(e)}'
            }
        finally:
            conn.close()
        
    except Exception as e:
        return {
            'success': False,
            'error': f'Query execution failed: {str(e)}'
        }

def generate_sql_from_natural_language(natural_query, schema, api_key, tables_info=None):
    """
    Generate SQL from natural language using LLM with robust error handling.
    
    Args:
        natural_query: Natural language question
        schema: Database schema string
        api_key: OpenAI API key
        tables_info: Optional list of table names for better context
        
    Returns:
        Dictionary with success status and SQL query or error message
    """
    try:
        if not natural_query or not natural_query.strip():
            return {
                'success': False,
                'error': 'Query cannot be empty'
            }
        
        if not schema or not schema.strip():
            return {
                'success': False,
                'error': 'Database schema is not available'
            }
        
        # Build enhanced prompt with table context
        tables_context = ""
        if tables_info:
            tables_context = f"\nAvailable tables: {', '.join(tables_info)}\n"
        
        prompt = f"""
You are an expert SQL developer. Convert the following natural language question into a SQLite query.

Database Schema:
{schema}
{tables_context}
Question: "{natural_query}"

CRITICAL RULES:
1. Generate ONLY SELECT queries (no INSERT, UPDATE, DELETE, DROP, etc.)
2. Use proper SQLite syntax (not MySQL or PostgreSQL specific features)
3. Use table and column names EXACTLY as they appear in the schema
4. Include appropriate JOINs if querying multiple tables
5. Use meaningful column aliases for readability
6. Handle NULL values appropriately
7. Add appropriate WHERE clauses, GROUP BY, ORDER BY as needed
8. Return ONLY a YAML block with the SQL query - NO explanations

Output format (YAML only):
```yaml
sql: |
  SELECT column1, column2
  FROM table_name
  WHERE condition
```

Generate the SQL query now:"""
        
        # Call LLM with error handling
        llm_response = call_llm(prompt, api_key=api_key)
        
        if not llm_response or not llm_response.strip():
            raise ValueError("LLM returned empty response")
        
        # Parse SQL from YAML response
        sql_query = parse_sql_from_yaml(llm_response)
        
        if not sql_query or not sql_query.strip():
            raise ValueError("Failed to extract SQL query from LLM response")
        
        # Validate the generated SQL
        if not validate_sql_query(sql_query):
            raise ValueError("Generated SQL query failed security validation (only SELECT queries allowed)")
        
        return {
            'success': True,
            'sql': sql_query.strip()
        }
        
    except ValueError as e:
        return {
            'success': False,
            'error': str(e)
        }
    except Exception as e:
        error_msg = str(e)
        if 'API key' in error_msg or '401' in error_msg:
            error_msg = 'Invalid API key. Please check your OpenAI API key.'
        elif 'rate limit' in error_msg.lower():
            error_msg = 'Rate limit exceeded. Please try again in a moment.'
        elif 'quota' in error_msg.lower():
            error_msg = 'API quota exceeded. Please check your OpenAI account.'
        
        return {
            'success': False,
            'error': f'SQL generation failed: {error_msg}'
        }

@app.route('/')
def index():
    """Main page - entry point for the application"""
    session_data = get_session_data()
    return render_template('index.html', 
                         has_api_key=bool(session_data.get('api_key')),
                         has_file=bool(session_data.get('db_path')),
                         file_name=session_data.get('file_name', ''))

@app.route('/upload', methods=['POST'])
def upload_file():
    """
    Handle file upload with comprehensive validation and error handling.
    Only processes file when uploaded, extracts schema automatically.
    """
    try:
        session_data = get_session_data()
        
        # Validate file in request
        if 'file' not in request.files:
            return jsonify({
                'success': False,
                'error': 'No file provided. Please select a file to upload.'
            })
        
        file = request.files['file']
        
        # Validate file selection
        if file.filename == '':
            return jsonify({
                'success': False, 
                'error': 'No file selected. Please choose a file.'
            })
        
        # Validate file type
        if not allowed_file(file.filename):
            return jsonify({
                'success': False,
                'error': f'Invalid file type. Allowed types: {", ".join(ALLOWED_EXTENSIONS)}'
            })
        
        # Secure filename and save
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{session_data['session_id']}_{filename}")
        
        try:
            file.save(file_path)
        except Exception as e:
            return jsonify({
                'success': False,
                'error': f'Failed to save file: {str(e)}'
            })
        
        # Process the uploaded file
        try:
            result = process_uploaded_file(file_path)
            
            if not result['success']:
                # Clean up file if processing failed
                if os.path.exists(file_path):
                    os.remove(file_path)
                return jsonify({
                    'success': False,
                    'error': f'Failed to process file: {result.get("error", "Unknown error")}'
                })
            
            # Store in session
            session_data['db_path'] = result['db_path']
            session_data['file_name'] = filename
            session_data['schema'] = result['schema']
            session_data['tables'] = result.get('tables', [])
            
            # Build success message
            tables_info = f"{len(result['tables'])} table(s)" if len(result['tables']) > 1 else "1 table"
            message = f'File uploaded successfully! Loaded {result["total_rows"]} rows across {tables_info}.'
            
            return jsonify({
                'success': True,
                'message': message,
                'schema': result['schema'],
                'tables': result['tables'],
                'total_rows': result['total_rows'],
                'total_columns': result['total_columns'],
                'metadata': result['metadata']
            })
            
        except Exception as e:
            # Clean up file if processing failed
            if os.path.exists(file_path):
                os.remove(file_path)
            
            error_msg = str(e)
            if 'permission' in error_msg.lower():
                error_msg = 'Permission denied. Please check file permissions.'
            elif 'empty' in error_msg.lower():
                error_msg = 'File appears to be empty or corrupted.'
            
            return jsonify({
                'success': False,
                'error': f'File processing error: {error_msg}'
            })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Upload failed: {str(e)}'
        })

@app.route('/set_api_key', methods=['POST'])
def set_api_key():
    """Set Gemini API key (optional - already configured in config.py)"""
    session_data = get_session_data()
    
    data = request.get_json()
    api_key = data.get('api_key', '').strip()
    
    if not api_key:
        return jsonify({'success': False, 'error': 'API key is required'})
    
    # Test the API key with a simple request
    try:
        # Use a very simple test to avoid complex responses
        test_response = call_llm("Reply with just 'OK' if you can read this message.", api_key=api_key)
        
        # Check if we got a valid response (not an error)
        if test_response and len(test_response.strip()) > 0 and 'error' not in test_response.lower():
            session_data['api_key'] = api_key
            return jsonify({'success': True, 'message': 'API key updated successfully for this session!'})
        else:
            return jsonify({'success': False, 'error': 'API key test failed - invalid response'})
            
    except Exception as e:
        error_msg = str(e)
        if '401' in error_msg or 'unauthorized' in error_msg.lower() or 'invalid' in error_msg.lower():
            return jsonify({'success': False, 'error': 'Invalid API key. Please check your OpenAI API key.'})
        elif 'rate limit' in error_msg.lower():
            return jsonify({'success': False, 'error': 'Rate limit exceeded. Please try again later.'})
        else:
            return jsonify({'success': False, 'error': f'API key validation failed: {error_msg}'})

@app.route('/query', methods=['POST'])
def process_query():
    """
    Process natural language query and return SQL results.
    This is called when user asks a question about their data.
    """
    try:
        session_data = get_session_data()
        
        # Get and validate query
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': 'No query data provided'
            })
        
        natural_query = data.get('query', '').strip()
        
        # Validate prerequisites
        if not natural_query:
            return jsonify({
                'success': False, 
                'error': 'Please enter a question about your data'
            })
        
        if not session_data.get('api_key'):
            return jsonify({
                'success': False, 
                'error': 'Please set your OpenAI API key first'
            })
        
        if not session_data.get('db_path'):
            return jsonify({
                'success': False, 
                'error': 'Please upload a file first'
            })
        
        if not session_data.get('schema'):
            return jsonify({
                'success': False, 
                'error': 'Database schema not found. Please re-upload your file'
            })
        
        # Verify database still exists
        if not os.path.exists(session_data['db_path']):
            return jsonify({
                'success': False, 
                'error': 'Database file not found. Please re-upload your file'
            })
        
        # Generate SQL from natural language
        sql_result = generate_sql_from_natural_language(
            natural_query=natural_query,
            schema=session_data['schema'],
            api_key=session_data['api_key'],
            tables_info=session_data.get('tables', [])
        )
        
        if not sql_result['success']:
            return jsonify({
                'success': False, 
                'error': sql_result['error']
            })
        
        # Execute the generated SQL query
        query_result = execute_query(
            query=sql_result['sql'],
            db_path=session_data['db_path']
        )
        
        if not query_result['success']:
            return jsonify({
                'success': False, 
                'error': query_result['error']
            })
        
        # Format results for display
        formatted_results = format_query_results(
            query_result['results'], 
            query_result['columns']
        )
        
        # Return successful response
        return jsonify({
            'success': True,
            'sql': sql_result['sql'],
            'results': query_result['results'],
            'columns': query_result['columns'],
            'formatted_results': formatted_results,
            'row_count': query_result['row_count']
        })
        
    except Exception as e:
        # Log the full error for debugging
        traceback.print_exc()
        return jsonify({
            'success': False, 
            'error': f'Query processing failed: {str(e)}'
        })

@app.route('/api_status')
def get_api_status():
    """Get current status of API key and file upload"""
    session_data = get_session_data()
    
    return jsonify({
        'api_key_set': bool(session_data.get('api_key')),
        'file_uploaded': bool(session_data.get('db_path')),
        'file_name': session_data.get('file_name', ''),
        'tables': session_data.get('tables', [])
    })

@app.route('/schema')
def get_schema():
    """Get current database schema"""
    session_data = get_session_data()
    
    if not session_data.get('schema'):
        return jsonify({
            'success': False, 
            'error': 'No schema available. Please upload a file first.'
        })
    
    return jsonify({
        'success': True,
        'schema': session_data['schema'],
        'tables': session_data.get('tables', [])
    })

if __name__ == '__main__':
    print("🚀 Starting SQL Agent Web UI...")
    print("📊 Open your browser and go to: http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)
