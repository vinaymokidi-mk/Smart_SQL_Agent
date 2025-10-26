# 🤖 SQL Agent - Natural Language to SQL Query System

A powerful web-based SQL agent that converts natural language questions into SQL queries and executes them against your Excel/CSV data files.

## ✨ Features

- **🔑 Dynamic API Key Configuration**: Set and validate your OpenAI API key directly from the web interface
- **📊 File Upload & Analysis**: Upload Excel (.xlsx, .xls) or CSV files with automatic schema detection
- **🗣️ Natural Language Queries**: Ask questions in plain English and get SQL queries + results
- **🔒 Secure**: Built-in SQL injection protection and query validation
- **💻 Local Processing**: All data processing happens locally on your machine
- **🎨 Modern UI**: Beautiful, responsive interface with real-time status indicators

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- OpenAI API key ([Get one here](https://platform.openai.com/api-keys))

### Installation & Running

#### Windows:
```bash
# Simply double-click or run:
start_sql_agent.bat
```

#### Linux/Mac:
```bash
# Make the script executable:
chmod +x start_sql_agent.sh

# Run the script:
./start_sql_agent.sh
```

The script will:
1. ✅ Check Python installation
2. ✅ Create virtual environment (if needed)
3. ✅ Install all dependencies
4. ✅ Start the web server at http://localhost:5000

## 📖 How to Use

### Step 1: Set Your API Key
1. Open http://localhost:5000 in your browser
2. Enter your OpenAI API key in the "OpenAI API Key" section
3. Click "Validate & Set API Key"
4. Wait for the green checkmark ✅ indicating successful validation

### Step 2: Upload Your Data
1. Click the upload area or drag & drop your Excel/CSV file
2. Wait for the file to be processed
3. The schema will be automatically displayed

### Step 3: Ask Questions
1. Type your question in natural language in the chat box
2. Press Enter or click Send
3. View the generated SQL query and results

## 💡 Example Questions

Try these example queries with your data:

- "Show me all the data"
- "What are the top 10 rows?"
- "Count the total number of rows"
- "Show me unique values in [column_name]"
- "What is the average of [column_name]?"
- "Group by [column_name] and count"
- "Show me records where [column_name] is greater than 100"

## 🔧 Manual Setup (Alternative)

If you prefer to set up manually:

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install requirements
pip install -r requirements_fixed.txt

# Run the application
python web_app_fixed.py
```

## 📦 Dependencies

- **Flask**: Web framework
- **OpenAI**: AI model for SQL generation
- **Pandas**: Data processing
- **openpyxl**: Excel file support
- **PyYAML**: YAML parsing

## 🏗️ Architecture

```
┌─────────────────┐
│   Web Browser   │
│   (Frontend)    │
└────────┬────────┘
         │ HTTP
         ▼
┌─────────────────┐
│  Flask Server   │
│  web_app_fixed  │
└────────┬────────┘
         │
    ┌────┴────┐
    ▼         ▼
┌────────┐ ┌──────────┐
│ OpenAI │ │  SQLite  │
│  API   │ │ Database │
└────────┘ └──────────┘
```

## 🔒 Security Features

- ✅ SQL injection prevention
- ✅ Query validation (only SELECT statements allowed)
- ✅ API key validation before use
- ✅ File size limits (16MB max)
- ✅ Secure file handling
- ✅ Session-based data isolation

## 🐛 Troubleshooting

### API Key Issues
- **Error: "Invalid API key"**
  - Verify your API key is correct
  - Check if key starts with "sk-"
  - Ensure you have credits in your OpenAI account

### File Upload Issues
- **Error: "File too large"**
  - File must be under 16MB
  - Try compressing or sampling your data

- **Error: "Invalid file type"**
  - Only .xlsx, .xls, and .csv files are supported
  - Make sure file extension is correct

### Query Issues
- **Error: "Query failed"**
  - Check if column names are correct (view schema)
  - Simplify your question
  - Try more specific queries

### Port Already in Use
```bash
# Kill the process using port 5000
# Windows:
netstat -ano | findstr :5000
taskkill /PID <PID> /F

# Linux/Mac:
lsof -ti:5000 | xargs kill -9
```

## 📁 Project Structure

```
PocketFlow/
├── web_app_fixed.py          # Main Flask application (FIXED VERSION)
├── templates/
│   └── index_fixed.html      # Web interface (FIXED VERSION)
├── uploads/                  # Uploaded files storage
├── requirements_fixed.txt    # Python dependencies (FIXED VERSION)
├── start_sql_agent.bat       # Windows startup script
├── start_sql_agent.sh        # Linux/Mac startup script
└── README_FIXED.md           # This file
```

## 🔄 Key Improvements in Fixed Version

### 1. Dynamic API Key Configuration ✅
- Real-time API key validation with OpenAI
- Connection testing before accepting key
- Visual status indicators
- No need for environment variables

### 2. Enhanced File Processing ✅
- Better error handling
- Automatic schema detection with sample data
- Support for multiple file formats
- Column name sanitization for SQL compatibility

### 3. Improved SQL Generation ✅
- Better prompt engineering
- Multiple SQL parsing strategies
- Enhanced validation and security
- Clearer error messages

### 4. Better User Experience ✅
- Step-by-step guided interface
- Real-time status updates
- Chat-style interaction
- Example queries
- Detailed error messages
- Loading indicators

## 🛠️ Advanced Usage

### Custom Port
```python
# Edit web_app_fixed.py, change the last line:
app.run(debug=True, host='0.0.0.0', port=8080)  # Change 5000 to your port
```

### Environment Variables (Optional)
You can also set the API key via environment variable:
```bash
# Windows:
set OPENAI_API_KEY=sk-your-key-here

# Linux/Mac:
export OPENAI_API_KEY=sk-your-key-here
```

## 🤝 Contributing

This is a fixed and improved version of the PocketFlow SQL Agent. Feel free to:
- Report bugs
- Suggest features
- Submit improvements

## 📝 Notes

- **Data Privacy**: All processing happens locally. Your data never leaves your machine (except for OpenAI API calls for SQL generation).
- **API Costs**: Each query makes a call to OpenAI API, which has associated costs. Monitor your usage at https://platform.openai.com/usage
- **Session Management**: Each browser session maintains its own database. Clear browser data to reset.

## 🎯 Use Cases

- **Data Analysis**: Quickly explore your Excel data without writing SQL
- **Business Intelligence**: Ask questions about sales, customers, products, etc.
- **Data Validation**: Verify data quality and consistency
- **Report Generation**: Extract specific data subsets
- **Learning SQL**: See how natural language translates to SQL

## 🔮 Future Enhancements

- [ ] Support for multiple tables and JOINs
- [ ] Data visualization (charts and graphs)
- [ ] Export results to Excel/CSV
- [ ] Query history and favorites
- [ ] Multi-user support
- [ ] Database connection (PostgreSQL, MySQL)
- [ ] Advanced aggregations and analytics

## 📞 Support

For issues or questions:
1. Check the troubleshooting section above
2. Review the error messages in the chat interface
3. Check Flask server logs in the console

## ⚖️ License

See LICENSE file for details.

---

**Made with ❤️ using PocketFlow Framework & OpenAI**

🌟 **Happy Querying!** 🌟
