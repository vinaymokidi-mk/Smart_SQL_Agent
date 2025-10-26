# SQL Agent - Robust Natural Language to SQL System

A powerful, production-ready web application that converts natural language questions into SQL queries and returns results from your Excel/CSV data files.

## 🌟 Key Features

- **File Upload & Auto Schema Detection**: Upload Excel (.xlsx, .xls) or CSV files, and the system automatically extracts and analyzes the schema
- **Natural Language Queries**: Ask questions about your data in plain English
- **Robust Error Handling**: Comprehensive validation and error messages at every step
- **Security First**: Only SELECT queries allowed, with SQL injection protection
- **Multi-Sheet Support**: Handles Excel files with multiple sheets
- **Session Management**: Each user gets their own isolated session
- **Clean Column Names**: Automatically sanitizes column names for SQL compatibility

## 📋 Requirements

- Python 3.8+
- OpenAI API Key
- Required Python packages (see `requirements.txt`)

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Start the Web Application

```bash
python web_app.py
```

The application will start on `http://localhost:5000`

### 3. Use the Application

1. **Set API Key**: Enter your OpenAI API key in the left panel
2. **Upload File**: Drag & drop or click to upload your Excel/CSV file
3. **Ask Questions**: Type natural language questions about your data
4. **View Results**: See the generated SQL and query results

## 💡 Example Queries

Once you've uploaded your data, you can ask questions like:

- "Show me the top 10 customers by revenue"
- "What is the average order value by region?"
- "How many products are in each category?"
- "List all orders from last month"
- "What are the total sales by product category?"

## 🏗️ Architecture

### Core Components

1. **`web_app.py`**: Flask web application with session management
2. **`utils.py`**: Robust utility functions for:
   - File processing and validation
   - Schema extraction
   - SQL generation
   - Query validation and execution
3. **`templates/index.html`**: Modern, responsive web interface

### Data Flow

```
User Uploads File
    ↓
File Validation & Processing
    ↓
Schema Extraction (Automatic)
    ↓
User Asks Question
    ↓
LLM Generates SQL
    ↓
SQL Validation
    ↓
Query Execution
    ↓
Results Display
```

## 🔒 Security Features

### SQL Injection Protection

- ✅ Only SELECT queries allowed
- ✅ No INSERT, UPDATE, DELETE, DROP operations
- ✅ No SQL comments or multiple statements
- ✅ Regex-based pattern matching for dangerous keywords
- ✅ YAML-based response parsing to prevent code injection

### File Upload Security

- ✅ Allowed file types: .xlsx, .xls, .csv only
- ✅ File size limit: 16MB
- ✅ Secure filename sanitization
- ✅ Session-based file isolation
- ✅ Automatic cleanup of temporary files

## 🛠️ Utility Functions

### File Processing

```python
process_uploaded_file(file_path, file_type=None)
```
- Validates file exists and is readable
- Auto-detects file type if not provided
- Handles multi-sheet Excel files
- Cleans column names for SQL compatibility
- Converts to SQLite database
- Extracts schema automatically
- Returns comprehensive metadata

### Schema Extraction

```python
get_schema_from_db(db_path)
```
- Connects to SQLite database
- Extracts all table names
- Gets column information (name, type, nullable)
- Formats for LLM consumption

### SQL Generation

```python
generate_sql_from_natural_language(natural_query, schema, api_key, tables_info=None)
```
- Validates inputs
- Constructs detailed prompt for LLM
- Calls OpenAI API with error handling
- Parses YAML response
- Validates generated SQL
- Returns clean SQL query or error

### Query Execution

```python
execute_query(query, db_path)
```
- Validates SQL query
- Connects to database
- Executes with timeout protection
- Returns results with column names
- Comprehensive error handling

## 📊 Supported File Formats

### Excel Files (.xlsx, .xls)

- **Single Sheet**: Creates one table named `data`
- **Multiple Sheets**: Each sheet becomes a separate table
- **Column Names**: Automatically cleaned and SQL-safe
- **Data Types**: Auto-detected by pandas

### CSV Files (.csv)

- Creates one table named `data`
- Handles various CSV dialects
- Auto-detects delimiters

## 🔧 Configuration

### Flask Configuration

```python
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'xlsx', 'xls', 'csv'}
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
```

### OpenAI Configuration

- Model: `gpt-4o` (default)
- Temperature: `0.1` (for consistent SQL generation)
- Max Tokens: `2000`

## 🚨 Error Handling

The system provides clear, actionable error messages for:

- **File Upload**: File type, size, permissions, corruption
- **API Key**: Invalid, rate limits, quota exceeded
- **SQL Generation**: Empty responses, parsing failures, validation errors
- **Query Execution**: Syntax errors, missing tables/columns, database errors

## 📝 Session Management

Each user session maintains:

- `session_id`: Unique identifier
- `api_key`: OpenAI API key (session-scoped)
- `db_path`: Path to temporary SQLite database
- `file_name`: Original filename
- `schema`: Extracted database schema
- `tables`: List of table names

## 🧪 Testing

### Manual Testing

1. **Valid File Upload**
   - Upload a valid Excel/CSV file
   - Verify schema is displayed
   - Check success message

2. **Invalid File Upload**
   - Try uploading .txt or .pdf
   - Verify error message

3. **Query Processing**
   - Ask simple questions
   - Verify SQL generation
   - Check results accuracy

4. **Error Cases**
   - Query without API key
   - Query without file
   - Invalid natural language query

## 🐛 Troubleshooting

### Common Issues

**"API key validation failed"**
- Verify your OpenAI API key is correct
- Check if you have credits in your OpenAI account

**"Database file not found"**
- Re-upload your file
- Check session hasn't expired

**"Query failed security validation"**
- The LLM generated a non-SELECT query
- Try rephrasing your question

**"Failed to process file"**
- Check file isn't corrupted
- Verify file has actual data
- Ensure column names are valid

## 🎯 Best Practices

### For Users

1. **Clear Questions**: Be specific about what you want to know
2. **File Quality**: Use clean, well-structured data files
3. **Column Names**: Use descriptive column headers
4. **Data Size**: Keep files under 16MB for best performance

### For Developers

1. **Always Validate**: Check inputs at every step
2. **Fail Gracefully**: Provide helpful error messages
3. **Log Everything**: Use logging for debugging
4. **Clean Up**: Remove temporary files after use
5. **Test Thoroughly**: Cover edge cases and error paths

## 📈 Performance

- **File Upload**: < 5 seconds for most files
- **Schema Extraction**: < 1 second
- **SQL Generation**: 2-5 seconds (depends on LLM)
- **Query Execution**: < 1 second for typical queries

## 🔮 Future Enhancements

- [ ] Support for more file formats (Parquet, JSON)
- [ ] Query result export (CSV, Excel)
- [ ] Query history and caching
- [ ] Chart/visualization generation
- [ ] Multi-user authentication
- [ ] Database persistence options
- [ ] Advanced analytics capabilities

## 📄 License

This project is part of the PocketFlow framework.

## 🙏 Acknowledgments

Built with:
- [Flask](https://flask.palletsprojects.com/)
- [OpenAI API](https://openai.com/)
- [Pandas](https://pandas.pydata.org/)
- [SQLite](https://www.sqlite.org/)
- [PocketFlow](https://github.com/the-pocket/PocketFlow)

