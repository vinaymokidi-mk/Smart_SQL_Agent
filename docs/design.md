# Design Doc: Text-to-SQL Workflow with Debug Loop

> Please DON'T remove notes for AI

## Requirements

> Notes for AI: Keep it simple and clear.
> If the requirements are abstract, write concrete user stories

**User Stories:**
1. **As a data analyst**, I want to ask natural language questions about my SQLite database and get accurate SQL results, so I can quickly explore data without writing SQL manually.

2. **As a business user**, I want the system to automatically fix SQL errors when they occur, so I don't need to manually debug failed queries.

3. **As a developer**, I want a robust system that handles edge cases gracefully, so the workflow doesn't crash on unexpected inputs.

**Core Requirements:**
- Convert natural language queries to SQLite-compatible SQL
- Automatically retrieve database schema for context
- Execute SQL queries safely against SQLite database
- Debug and retry failed SQL queries using LLM feedback
- Provide clear error messages and execution results
- Support both SELECT queries (return data) and DML queries (modify data)

## Flow Design

> Notes for AI:
> 1. Consider the design patterns of agent, map-reduce, rag, and workflow. Apply them if they fit.
> 2. Present a concise, high-level description of the workflow.

### Applicable Design Pattern:

**Workflow Pattern**: This is a classic workflow pattern where we decompose the complex task of text-to-SQL into sequential, manageable steps. Each node handles a specific responsibility:
- Schema retrieval
- SQL generation  
- SQL execution
- Error debugging

The debug loop creates a **branching workflow** where execution can loop back based on success/failure conditions.

### Flow high-level Design:

1. **Schema Retrieval Node**: Connect to SQLite database and extract table/column schema information
2. **SQL Generation Node**: Use LLM to convert natural language query + schema into SQLite SQL
3. **SQL Execution Node**: Execute the generated SQL against the database
4. **Debug Loop**: If execution fails, use LLM to analyze error and generate corrected SQL
5. **Result Processing**: Format and display successful results or final error messages

```mermaid
flowchart TD
    start[Start] --> schema[Get Schema]
    schema --> generate[Generate SQL]
    generate --> execute[Execute SQL]
    execute -->|Success| success[Display Results]
    execute -->|Error| debug{Debug Attempts < Max?}
    debug -->|Yes| debugSQL[Debug SQL]
    debug -->|No| failure[Display Error]
    debugSQL --> execute
    success --> end[End]
    failure --> end
```

## Utility Functions

> Notes for AI:
> 1. Understand the utility function definition thoroughly by reviewing the doc.
> 2. Include only the necessary utility functions, based on nodes in the flow.

1. **Call LLM** (`utils/call_llm.py`)
   - *Input*: prompt (str)
   - *Output*: response (str)
   - *Necessity*: Used by SQL Generation and Debug nodes for LLM-powered SQL creation and error correction

2. **Database Connection** (`utils/db_utils.py`)
   - *Input*: db_path (str)
   - *Output*: sqlite3.Connection object
   - *Necessity*: Used by Schema Retrieval and SQL Execution nodes for database operations

3. **SQL Parser** (`utils/sql_utils.py`)
   - *Input*: llm_response (str)
   - *Output*: parsed SQL query (str)
   - *Necessity*: Used by SQL Generation and Debug nodes to extract SQL from LLM YAML responses

## Node Design

### Shared Store

> Notes for AI: Try to minimize data redundancy

The shared store structure is organized as follows:

```python
shared = {
    "db_path": str,                    # Path to SQLite database file
    "natural_query": str,               # Original user question
    "schema": str,                     # Database schema information
    "generated_sql": str,              # Current SQL query to execute
    "debug_attempts": int,             # Number of debug attempts made
    "max_debug_attempts": int,         # Maximum allowed debug attempts
    "execution_error": str,            # Last SQL execution error message
    "final_result": any,               # Successful query results
    "result_columns": list,            # Column names for SELECT queries
    "final_error": str                 # Final error message if all attempts fail
}
```

### Node Steps

> Notes for AI: Carefully decide whether to use Batch/Async Node/Flow.

1. **GetSchema Node**
   - *Purpose*: Retrieve database schema information for LLM context
   - *Type*: Regular Node
   - *Steps*:
     - *prep*: Read "db_path" from shared store
     - *exec*: Connect to database, query schema tables and columns
     - *post*: Write "schema" to shared store, display schema info

2. **GenerateSQL Node**
   - *Purpose*: Convert natural language query to SQL using LLM
   - *Type*: Regular Node
   - *Steps*:
     - *prep*: Read "natural_query" and "schema" from shared store
     - *exec*: Call LLM with schema context to generate SQL
     - *post*: Write "generated_sql" to shared store, reset debug attempts

3. **ExecuteSQL Node**
   - *Purpose*: Execute SQL query against database with error handling
   - *Type*: Regular Node
   - *Steps*:
     - *prep*: Read "db_path" and "generated_sql" from shared store
     - *exec*: Execute SQL query, handle both SELECT and DML queries
     - *post*: Store results or error, decide next action based on success/failure

4. **DebugSQL Node**
   - *Purpose*: Analyze SQL errors and generate corrected queries
   - *Type*: Regular Node
   - *Steps*:
     - *prep*: Read query, schema, failed SQL, and error message from shared store
     - *exec*: Call LLM to analyze error and generate corrected SQL
     - *post*: Write corrected "generated_sql" to shared store, clear error state

## Implementation Considerations

### Error Handling Strategy
- Use Node's built-in retry mechanism for LLM API failures
- Implement graceful fallbacks for database connection issues
- Provide clear error messages for different failure scenarios

### Security Considerations
- Validate SQL queries before execution to prevent injection attacks
- Limit database operations to read-only for production use
- Sanitize user inputs in natural language queries

### Performance Optimizations
- Cache database schema for repeated queries
- Implement query result pagination for large datasets
- Add query execution timeout limits

### Extensibility Points
- Support for multiple database types (PostgreSQL, MySQL)
- Integration with vector databases for semantic query understanding
- Support for complex analytical queries with aggregations
