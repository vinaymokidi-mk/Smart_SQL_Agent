# 📚 SQL Agent - Complete User Guide

## Table of Contents
1. [Getting Started](#getting-started)
2. [Setting Up API Key](#setting-up-api-key)
3. [Uploading Data](#uploading-data)
4. [Asking Questions](#asking-questions)
5. [Understanding Results](#understanding-results)
6. [Best Practices](#best-practices)
7. [Common Issues](#common-issues)

---

## Getting Started

### What is SQL Agent?

SQL Agent is an AI-powered tool that lets you analyze your Excel/CSV data using natural language. Instead of writing complex SQL queries, just ask questions in plain English!

**Example:**
- ❌ Old way: `SELECT category, COUNT(*) FROM products GROUP BY category ORDER BY COUNT(*) DESC`
- ✅ New way: "Show me how many products are in each category"

### Prerequisites

Before you start, make sure you have:
- ✅ Python 3.8+ installed
- ✅ An OpenAI API key ([Get one here](https://platform.openai.com/api-keys))
- ✅ Your data in Excel (.xlsx, .xls) or CSV format

---

## Setting Up API Key

### Step 1: Get Your OpenAI API Key

1. Go to https://platform.openai.com/api-keys
2. Sign up or log in
3. Click "Create new secret key"
4. Copy your API key (it starts with `sk-`)
5. **Important**: Keep it secure! Don't share it with anyone

### Step 2: Configure in SQL Agent

1. Open the SQL Agent web interface (http://localhost:5000)
2. Find the "OpenAI API Key" section on the left
3. Paste your API key
4. Click "Validate & Set API Key"
5. Wait for the green checkmark ✅

**What happens during validation?**
- SQL Agent tests your API key by making a small request to OpenAI
- It checks if the key is valid and has available credits
- If successful, you'll see a green badge "Connected"

**Troubleshooting API Key Issues:**

| Error Message | Solution |
|--------------|----------|
| "Invalid API key" | Double-check your key, ensure it starts with `sk-` |
| "Rate limit exceeded" | Your key is valid but hitting rate limits. Wait a few minutes |
| "Insufficient quota" | Add credits to your OpenAI account |
| "Connection failed" | Check your internet connection |

---

## Uploading Data

### Supported File Formats

- ✅ Excel 2007+ (.xlsx)
- ✅ Excel 97-2003 (.xls)
- ✅ CSV (.csv)
- ⚠️ Max file size: 16MB

### How to Upload

**Method 1: Click to Upload**
1. Click on the upload area
2. Select your file
3. Wait for processing

**Method 2: Drag & Drop**
1. Drag your file from File Explorer
2. Drop it on the upload area
3. Wait for processing

### What Happens During Upload?

1. **File Reading**: SQL Agent reads your Excel/CSV file
2. **Column Cleaning**: Column names are cleaned for SQL compatibility
   - Spaces become underscores
   - Special characters are removed
   - Numbers at the start get a prefix
3. **Database Creation**: A temporary SQLite database is created
4. **Schema Detection**: The structure is analyzed and displayed

### Understanding the Schema

After upload, you'll see something like:

```
Table: data
  - product_name (TEXT, NULL)
  - price (REAL, NULL)
  - quantity (INTEGER, NULL)
  - category (TEXT, NULL)
  Sample data (first 3 rows):
    ('Laptop', 999.99, 5, 'Electronics')
    ('Mouse', 29.99, 50, 'Accessories')
    ('Keyboard', 79.99, 30, 'Accessories')
```

This shows:
- **Table name**: Always "data"
- **Columns**: Name, type, and if NULL is allowed
- **Sample data**: First 3 rows to understand your data

---

## Asking Questions

### Query Examples by Category

#### **Basic Data Exploration**
```
"Show me all the data"
"Display the first 10 rows"
"How many rows are in the dataset?"
"What columns are available?"
```

#### **Filtering**
```
"Show me products with price greater than 100"
"Find all orders from 2024"
"Show me customers from New York"
"Get records where status is 'completed'"
```

#### **Aggregations**
```
"What is the average price?"
"Count how many products in each category"
"Sum the total sales by month"
"Find the minimum and maximum prices"
```

#### **Sorting**
```
"Show me the top 5 most expensive products"
"List customers ordered by registration date"
"Show products sorted by stock quantity descending"
```

#### **Grouping**
```
"Group sales by region and show totals"
"Count customers by city"
"Average order value by product category"
```

#### **Advanced**
```
"Show me products with above-average prices"
"Find the second highest price"
"List categories with more than 10 products"
"Show running total of sales"
```

### Tips for Better Results

**✅ DO:**
- Be specific about what you want
- Mention column names explicitly
- Use simple, clear language
- Ask one thing at a time

**❌ DON'T:**
- Use vague terms like "stuff" or "things"
- Ask multiple unrelated questions in one query
- Use column names that don't exist (check schema!)
- Ask for modifications (UPDATE, DELETE) - not supported

### Query Examples with Your Data

If your data has these columns: `customer_name`, `order_date`, `total_amount`, `status`

**Good queries:**
```
"Show me all orders where status is 'pending'"
"What is the total amount of all completed orders?"
"List the top 10 customers by total amount"
"Count orders by status"
```

**Bad queries:**
```
"Show me stuff" ❌ (too vague)
"Get orders and calculate taxes and shipping" ❌ (too complex)
"Update the status to completed" ❌ (not supported)
```

---

## Understanding Results

### Result Display

After asking a question, you'll see:

1. **Generated SQL Query**
   ```sql
   SELECT category, COUNT(*) as count
   FROM data
   GROUP BY category
   ORDER BY count DESC
   ```

2. **Results Table**
   | category | count |
   |----------|-------|
   | Electronics | 25 |
   | Accessories | 18 |
   | Furniture | 12 |

3. **Row Count**
   "Showing 3 rows"

### Interpreting SQL

Understanding the generated SQL helps you learn:

- `SELECT`: What columns to show
- `FROM data`: Your table (always called "data")
- `WHERE`: Filters applied
- `GROUP BY`: How data is grouped
- `ORDER BY`: How results are sorted
- `LIMIT`: Maximum number of rows

### Empty Results

If you get "No results found", it might mean:
- Your filter is too strict
- There's no data matching your criteria
- Column name is incorrect

**Try:**
- Simplify your question
- Check the schema for correct column names
- Remove some filters

---

## Best Practices

### 1. Data Preparation

**Before uploading:**
- Remove unnecessary columns
- Ensure column names are descriptive
- Check for data quality issues
- Remove very large files (sample if needed)

### 2. Efficient Querying

**Start simple:**
```
1. "Show me the first 10 rows" (understand your data)
2. "What columns are available?" (confirm schema)
3. "Count total rows" (understand size)
4. Then ask specific questions
```

### 3. Column Names

If your original column has spaces like "Total Sales", it becomes `total_sales` in SQL.

**Check the schema** to see the actual column names used in the database.

### 4. Performance

For large datasets:
- Use `LIMIT` in your questions: "Show me top 100 rows"
- Be specific with filters
- Avoid asking for "all data" repeatedly

### 5. Cost Management

Each query uses OpenAI API credits:
- Start with simpler questions
- Review the generated SQL before executing
- Monitor your OpenAI usage dashboard

---

## Common Issues

### Issue: "Please set a valid OpenAI API key first"

**Solution:**
1. Make sure you've entered your API key
2. Click "Validate & Set API Key"
3. Wait for green checkmark

### Issue: "Please upload a file first"

**Solution:**
1. Upload an Excel or CSV file
2. Wait for "File uploaded successfully" message
3. Check that schema is displayed

### Issue: Query returns wrong results

**Solution:**
1. Check the generated SQL query
2. Verify column names match your question
3. Look at the schema for actual column names
4. Try rephrasing your question

### Issue: "SQL execution error: no such column"

**Solution:**
1. Check the schema for correct column names
2. Remember: column names are cleaned (spaces→underscores)
3. Use exact column names from schema

### Issue: Slow responses

**Possible causes:**
- Large dataset (use LIMIT)
- Complex query
- OpenAI API delays

**Solutions:**
- Ask for fewer rows: "Show me top 100..."
- Simplify your question
- Check OpenAI status page

### Issue: File upload fails

**Solutions:**
- Check file size (must be < 16MB)
- Ensure file format is .xlsx, .xls, or .csv
- Try opening file in Excel to verify it's not corrupted
- Check file permissions

---

## Advanced Tips

### 1. Using LIKE for Text Search

Ask: "Show me products where name contains 'laptop'"

Generated SQL:
```sql
SELECT * FROM data WHERE product_name LIKE '%laptop%'
```

### 2. Date Filtering

Ask: "Show orders from January 2024"

Make sure your date column is recognized by SQL Agent.

### 3. Multiple Conditions

Ask: "Show products with price > 100 AND category is 'Electronics'"

### 4. Calculations

Ask: "Show me the total value (price * quantity) for each product"

### 5. Distinct Values

Ask: "Show me unique categories"

Generated SQL:
```sql
SELECT DISTINCT category FROM data
```

---

## Security & Privacy

### What Data is Sent to OpenAI?

- ✅ Your natural language question
- ✅ Database schema (structure)
- ✅ Sample data (3 rows) for context
- ❌ Your full dataset
- ❌ Query results

### What Stays Local?

- ✅ Your uploaded file
- ✅ The SQLite database
- ✅ Query results
- ✅ Session data

### API Key Security

- Stored in your browser session only
- Never saved to disk
- Cleared when you close the browser
- Not shared or transmitted anywhere except OpenAI

---

## Getting Help

### Quick Checklist

Before asking for help, check:
- [ ] Python 3.8+ installed
- [ ] All packages installed (`pip install -r requirements_fixed.txt`)
- [ ] API key is valid and has credits
- [ ] File is in supported format
- [ ] File size is under 16MB
- [ ] Internet connection is working

### Useful Commands

**Check Python version:**
```bash
python --version
```

**Test setup:**
```bash
python test_setup.py
```

**View server logs:**
Check the console where you ran the startup script

---

## Example Workflow

Let's walk through a complete example:

### Scenario: Sales Data Analysis

**1. Start the application**
```bash
start_sql_agent.bat
```

**2. Set API Key**
- Enter: `sk-your-actual-key-here`
- Click "Validate & Set API Key"
- ✅ See green checkmark

**3. Upload sales_data.xlsx**
File contains:
- order_id
- customer_name
- product
- quantity
- price
- order_date

**4. Ask questions progressively**

```
Q1: "Show me the first 5 orders"
→ See sample data

Q2: "What is the total revenue?"
→ Get: SELECT SUM(quantity * price) as total_revenue FROM data

Q3: "Show me top 5 products by revenue"
→ See: Product rankings with revenue

Q4: "Count orders by customer"
→ See: Customer order frequency

Q5: "Show orders from this month where price > 100"
→ Get: Filtered results
```

**5. Explore further based on results**

---

## Keyboard Shortcuts

- `Enter`: Send query
- `Ctrl+C`: Stop server (in console)
- `F5`: Refresh page (clears session)

---

## Tips from Power Users

1. **Start with "Show me all data"** to understand structure
2. **Keep the schema visible** while asking questions
3. **Use example queries** as templates
4. **Save interesting SQL queries** for later reference
5. **Export results** by copying from the table

---

## Next Steps

Now that you know how to use SQL Agent:

1. ✅ Try it with your own data
2. ✅ Experiment with different questions
3. ✅ Learn SQL by observing generated queries
4. ✅ Share insights with your team

---

**Happy Querying! 🎉**

For more help, check:
- README_FIXED.md
- Test your setup: `python test_setup.py`
- Check Flask logs in console
