#!/usr/bin/env python3
"""
Startup script for SQL Agent Web UI
"""

import os
import sys
import webbrowser
import time
from web_app import app

def main():
    print("🚀 Starting SQL Agent Web UI...")
    print("=" * 50)
    print("📊 Features:")
    print("  ✅ Upload Excel files")
    print("  ✅ Set OpenAI API key")
    print("  ✅ Natural language queries")
    print("  ✅ Real-time SQL generation")
    print("  ✅ Beautiful results display")
    print("=" * 50)
    
    # Wait a moment for the server to start
    time.sleep(2)
    
    # Open browser
    try:
        webbrowser.open('http://localhost:5000')
        print("🌐 Opening browser at: http://localhost:5000")
    except:
        print("🌐 Please open your browser and go to: http://localhost:5000")
    
    print("\n💡 Instructions:")
    print("  1. Set your OpenAI API key")
    print("  2. Upload an Excel file")
    print("  3. Start asking questions!")
    print("\n🛑 Press Ctrl+C to stop the server")
    print("=" * 50)
    
    # Start the Flask app
    app.run(debug=True, host='0.0.0.0', port=5000)

if __name__ == "__main__":
    main()
