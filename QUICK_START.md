# 🚀 Quick Start Guide - SQL Agent

Get up and running in 3 simple steps!

## Step 1: Install Dependencies

```bash
pip install -r requirements_robust.txt
```

## Step 2: Start the Application

### Windows:
```bash
python start_robust.py
```

### Mac/Linux:
```bash
python3 start_robust.py
```

## Step 3: Use the Application

1. Open your browser to: **http://localhost:5000**

2. **Set API Key** (left panel)
   - Enter your OpenAI API key
   - Click "Set API Key"
   - Wait for confirmation

3. **Upload File** (left panel)
   - Click or drag & drop your Excel/CSV file
   - System will automatically extract schema
   - See schema displayed below

4. **Ask Questions** (right panel)
   - Type your question in natural language
   - Example: "Show me total sales by region"
   - Press Enter or click Send
   - See SQL query and results

## Example Questions

Once your file is uploaded, try asking:

- "How many rows are in the data?"
- "What are the top 10 items?"
- "Show me the average values grouped by category"
- "List all records from last month"
- "What is the sum of sales by region?"

## Supported File Formats

- Excel: `.xlsx`, `.xls`
- CSV: `.csv`
- Max size: 16MB

## Troubleshooting

**Can't connect to server?**
- Make sure port 5000 is not in use
- Try: `python web_app.py` directly

**API Key errors?**
- Verify your OpenAI API key is correct
- Check you have credits in your account

**File upload fails?**
- Check file size is under 16MB
- Verify file format is supported
- Make sure file has actual data

**Query returns no results?**
- Check your question is clear
- Verify data matches your question
- Look at the generated SQL query

## Need Help?

- See: `README_ROBUST.md` for full documentation
- See: `IMPLEMENTATION_SUMMARY.md` for technical details

---

**That's it! You're ready to query your data with natural language! 🎉**

