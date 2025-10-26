# 🚀 SQL Agent - Quick Reference Cheat Sheet

## Quick Start Commands

### Windows
```bash
start_sql_agent.bat
```

### Linux/Mac
```bash
chmod +x start_sql_agent.sh
./start_sql_agent.sh
```

### Test Setup
```bash
python test_setup.py
```

---

## Setup Checklist

- [ ] Python 3.8+ installed
- [ ] Run startup script
- [ ] Open http://localhost:5000
- [ ] Enter OpenAI API key
- [ ] Upload data file
- [ ] Start querying!

---

## Common Query Patterns

### Basic Queries
| What you want | Ask this |
|---------------|----------|
| See all data | "Show me all the data" |
| First N rows | "Show me the first 10 rows" |
| Count rows | "How many rows are there?" |
| Column list | "What columns are available?" |

### Filtering
| What you want | Ask this |
|---------------|----------|
| Exact match | "Show me rows where status is 'active'" |
| Greater than | "Show me products with price > 100" |
| Less than | "Find orders with quantity < 5" |
| Date range | "Show me orders from 2024" |
| Text search | "Find products containing 'laptop'" |

### Aggregations
| What you want | Ask this |
|---------------|----------|
| Count | "Count total rows" |
| Sum | "What is the total of all sales?" |
| Average | "What is the average price?" |
| Min/Max | "What is the minimum and maximum price?" |
| Group count | "Count orders by status" |

### Sorting
| What you want | Ask this |
|---------------|----------|
| Top N | "Show me top 5 products by sales" |
| Bottom N | "Show me 5 products with lowest stock" |
| Sort ascending | "List customers ordered by name" |
| Sort descending | "Show products sorted by price descending" |

### Grouping
| What you want | Ask this |
|---------------|----------|
| Count by group | "Count products by category" |
| Sum by group | "Total sales by region" |
| Average by group | "Average price by category" |

---

## File Formats Supported

✅ Excel 2007+ (.xlsx)  
✅ Excel 97-2003 (.xls)  
✅ CSV (.csv)  
⚠️ Max size: 16MB

---

## Status Indicators

| Indicator | Meaning |
|-----------|---------|
| 🟢 Connected | API key validated |
| 🔴 Not Set | API key not configured |
| 🟢 Loaded | File uploaded successfully |
| 🔴 No File | No file uploaded yet |

---

## Keyboard Shortcuts

| Key | Action |
|-----|--------|
| Enter | Send query |
| Ctrl+C | Stop server (console) |
| F5 | Refresh page |

---

## Troubleshooting Quick Fixes

### API Key Not Working
```bash
1. Check it starts with "sk-"
2. Verify credits at platform.openai.com
3. Test with simple query first
```

### File Won't Upload
```bash
1. Check file size < 16MB
2. Verify file format (.xlsx, .xls, .csv)
3. Try opening in Excel first
```

### Query Fails
```bash
1. Check schema for column names
2. Use exact column names (case-sensitive)
3. Simplify your question
```

### Server Won't Start
```bash
# Windows
netstat -ano | findstr :5000
taskkill /PID <PID> /F

# Linux/Mac
lsof -ti:5000 | xargs kill -9
```

---

## Column Name Rules

Original → SQL Name
- `Total Sales` → `total_sales`
- `Customer Name` → `customer_name`
- `2024 Revenue` → `col_2024_revenue`
- `Price ($)` → `price___`

**Always check the schema** after upload!

---

## SQL Keywords to Know

| Keyword | What it does | Example |
|---------|--------------|---------|
| SELECT | Choose columns | SELECT name, price |
| WHERE | Filter rows | WHERE price > 100 |
| GROUP BY | Group data | GROUP BY category |
| ORDER BY | Sort results | ORDER BY price DESC |
| LIMIT | Limit rows | LIMIT 10 |
| COUNT | Count rows | COUNT(*) |
| SUM | Add values | SUM(price) |
| AVG | Average | AVG(quantity) |
| MAX/MIN | Max/Min | MAX(price) |

---

## Example Session

```
1. Start: start_sql_agent.bat
2. Set API: sk-your-key-here
3. Upload: sales_data.xlsx
4. Query: "Show me top 10 customers by total sales"
5. View: SQL + Results table
6. Iterate: Ask more questions
```

---

## Cost Estimation

Typical costs per query:
- Simple query: ~$0.001-0.002
- Complex query: ~$0.002-0.005

Based on GPT-4o-mini pricing ($0.15/1M input tokens)

---

## Security Notes

✅ Data stays local (except schema sent to OpenAI)  
✅ API key stored in session only  
✅ No data saved to disk  
✅ Only SELECT queries allowed  
❌ No UPDATE/DELETE/DROP allowed

---

## Links

📖 Full Guide: USER_GUIDE.md  
📚 Detailed README: README_FIXED.md  
🔗 OpenAI Keys: https://platform.openai.com/api-keys  
🔗 OpenAI Usage: https://platform.openai.com/usage

---

## Quick Tips

💡 Start simple, then get specific  
💡 Check schema before complex queries  
💡 Use LIMIT for large datasets  
💡 Monitor your OpenAI usage  
💡 Copy SQL queries for learning

---

## Support

🐛 Bug? Check Flask console logs  
❓ Question? Read USER_GUIDE.md  
🧪 Test? Run `python test_setup.py`

---

**Version: Fixed 2024**  
**Updated: October 2024**

---

## Print This!

Save this file or print it for quick reference while using SQL Agent.

**Happy Querying! 🎉**
