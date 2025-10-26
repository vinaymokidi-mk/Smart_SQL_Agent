# 🚀 Getting Started with SQL Agent

**Welcome! This guide will get you up and running in 5 minutes.**

---

## ⚡ Quick Start (3 Commands)

### Windows
```bash
# 1. Open Command Prompt in this folder
# 2. Run:
start_sql_agent.bat
# 3. Browser opens automatically at http://localhost:5000
```

### Linux/Mac
```bash
# 1. Open Terminal in this folder
# 2. Run:
chmod +x start_sql_agent.sh
./start_sql_agent.sh
# 3. Open http://localhost:5000 in your browser
```

**That's it! The script handles everything else.**

---

## 📋 What You Need

✅ **Python 3.8+** ([Download here](https://www.python.org/downloads/))  
✅ **OpenAI API Key** ([Get one here](https://platform.openai.com/api-keys))  
✅ **Your data file** (.xlsx, .xls, or .csv)

---

## 🎯 First Time Setup

### Step 1: Check Python
```bash
python --version
```
Should show Python 3.8 or higher.

### Step 2: Test Your Setup
```bash
python test_setup.py
```
All checks should pass ✅

### Step 3: Start the Agent
```bash
# Windows
start_sql_agent.bat

# Linux/Mac
./start_sql_agent.sh
```

---

## 🖥️ Using the Web Interface

### 1. Set Your API Key (30 seconds)
- Open http://localhost:5000
- Find "OpenAI API Key" box on the left
- Paste your API key (starts with `sk-`)
- Click "Validate & Set API Key"
- Wait for green ✅ checkmark

### 2. Upload Your Data (30 seconds)
- Click the upload area or drag & drop your file
- Wait for "File uploaded successfully!"
- Check the schema display

### 3. Ask Questions! (Interactive)
- Type your question in plain English
- Examples:
  - "Show me the first 10 rows"
  - "What is the average price?"
  - "Count products by category"
- Press Enter or click Send
- View SQL + Results

---

## 💡 Example Session

```
1. Start: start_sql_agent.bat
   ✅ Virtual environment created
   ✅ Dependencies installed
   ✅ Server started at localhost:5000

2. Browser: http://localhost:5000
   ✅ Enter API key: sk-...
   ✅ Upload file: sales_data.xlsx
   ✅ See schema displayed

3. Ask: "Show me top 5 products by revenue"
   ✅ See generated SQL
   ✅ See results table
   ✅ 5 rows displayed

4. Continue asking questions!
```

---

## 🆘 Troubleshooting

### "Command not found: python"
**Fix:** Install Python from python.org

### "Port 5000 already in use"
**Fix:**
```bash
# Windows
netstat -ano | findstr :5000
taskkill /PID <number> /F

# Linux/Mac
lsof -ti:5000 | xargs kill -9
```

### "Invalid API key"
**Fix:** 
- Double-check your key from platform.openai.com/api-keys
- Make sure it starts with `sk-`
- Verify you have credits available

### "File upload failed"
**Fix:**
- Check file size (must be < 16MB)
- Verify format (.xlsx, .xls, .csv only)
- Try opening file in Excel first

---

## 📚 Learn More

After you're up and running:

- 📖 **Full Documentation**: README_FIXED.md
- 📘 **User Guide**: USER_GUIDE.md  
- 📄 **Quick Reference**: CHEAT_SHEET.md
- 🔧 **Technical Details**: FIX_SUMMARY.md

---

## 🎯 Quick Reference

### Common Questions You Can Ask

| Question Type | Example |
|--------------|---------|
| **View data** | "Show me all the data" |
| **Filter** | "Find products with price > 100" |
| **Count** | "How many rows are there?" |
| **Average** | "What's the average price?" |
| **Group** | "Count orders by status" |
| **Sort** | "Top 10 products by sales" |

### File Formats Supported
- ✅ Excel 2007+ (.xlsx)
- ✅ Excel 97-2003 (.xls)
- ✅ CSV (.csv)
- ⚠️ Max 16MB

### Status Indicators
- 🟢 **Green badge** = Connected/Ready
- 🔴 **Red badge** = Not Set/Missing

---

## 🔒 Privacy & Security

✅ **Your data stays local** (only schema sent to OpenAI)  
✅ **API key stored in session only** (cleared on browser close)  
✅ **No data saved to disk** (except temporary database)  
✅ **Only SELECT queries allowed** (no modifications)

---

## 💰 Cost Info

Each query costs approximately:
- Simple query: ~$0.001 (less than 1 cent)
- Complex query: ~$0.002-0.005

**Tip:** Monitor your usage at platform.openai.com/usage

---

## ✅ Success Checklist

After setup, you should see:

- [x] Python 3.8+ installed
- [x] Virtual environment created (venv/ folder)
- [x] Dependencies installed
- [x] Server running on port 5000
- [x] Browser opened to http://localhost:5000
- [x] API key validated ✅
- [x] File uploaded ✅
- [x] Schema displayed
- [x] First query executed successfully

---

## 🎉 You're Ready!

**Congratulations!** You now have a working SQL Agent.

### What to do next:
1. ✅ Try example queries
2. ✅ Upload your own data
3. ✅ Explore different question types
4. ✅ Learn SQL by observing generated queries
5. ✅ Share insights with your team

---

## 🆘 Need Help?

1. **Check the logs** in your terminal/command prompt
2. **Run test:** `python test_setup.py`
3. **Read docs:** USER_GUIDE.md has detailed troubleshooting
4. **Verify setup:** All status badges should be green

---

## 🎊 Happy Analyzing!

You're all set to explore your data with natural language!

**Pro Tip:** Start with simple queries like "Show me the first 10 rows" to understand your data structure, then get more specific.

---

**Quick Links:**
- 🏠 Home: http://localhost:5000
- 🔑 Get API Key: https://platform.openai.com/api-keys
- 💳 Check Usage: https://platform.openai.com/usage
- 📚 Full Docs: README_FIXED.md

---

**Made with ❤️ using OpenAI & Flask**
