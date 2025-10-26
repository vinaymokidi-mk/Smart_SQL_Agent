# How to Add Your OpenAI API Key

## ⚠️ Important Notice

The API key you provided (`sk-9a76a120efaa4a5d9ab2110308babf0d`) appears to be invalid or inactive.

## 🔑 How to Get a Valid API Key

1. Go to: https://platform.openai.com/api-keys
2. Sign in to your OpenAI account
3. Click "Create new secret key"
4. Copy the key (starts with `sk-...`)

## 📝 How to Configure Your API Key

### Method 1: Edit config.py (Recommended)

Open `config.py` and replace the API key:

```python
# Change this line:
OPENAI_API_KEY = "sk-9a76a120efaa4a5d9ab2110308babf0d"

# To your actual key:
OPENAI_API_KEY = "sk-proj-your-actual-key-here"
```

### Method 2: Set Environment Variable

**Windows (PowerShell):**
```powershell
$env:OPENAI_API_KEY="sk-proj-your-actual-key-here"
python web_app.py
```

**Windows (Command Prompt):**
```cmd
set OPENAI_API_KEY=sk-proj-your-actual-key-here
python web_app.py
```

**Mac/Linux:**
```bash
export OPENAI_API_KEY="sk-proj-your-actual-key-here"
python web_app.py
```

### Method 3: Use Web Interface

1. Start the application: `python web_app.py`
2. Open browser: http://localhost:5000
3. Enter your API key in the left panel
4. Click "Set API Key"

## ✅ Verify Your API Key Works

After adding your key, test it:

```bash
python test_api_connection.py
```

You should see:
```
✅ SUCCESS! API is working!
Response: Hello! API connection successful.
```

## 🔒 Security Notes

- Never share your API key publicly
- Never commit config.py to public repositories
- Keep your API key secret
- The key in config.py is for local development only

## 💡 Troubleshooting

### "Invalid API key"
- Verify you copied the complete key
- Check for extra spaces
- Make sure the key is active in your OpenAI account

### "Rate limit exceeded"
- You're making too many requests
- Wait a moment and try again
- Consider upgrading your OpenAI plan

### "Quota exceeded"
- Your OpenAI account is out of credits
- Add billing information at: https://platform.openai.com/account/billing

## 🚀 Once Your Key Works

Run the application:

```bash
python web_app.py
```

Then open: **http://localhost:5000**

---

**Need a valid API key?** Visit https://platform.openai.com/api-keys

