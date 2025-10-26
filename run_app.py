#!/usr/bin/env python3
"""
Simple startup script for SQL Agent
Automatically uses configured API key from config.py
"""

import sys
import os

def main():
    """Start the application."""
    print("="*70)
    print(" 🚀 SQL AGENT - Natural Language to SQL")
    print("="*70)
    
    # Check if config.py exists
    if not os.path.exists('config.py'):
        print("\n❌ Error: config.py not found!")
        print("   Please ensure config.py exists in the current directory.")
        return 1
    
    # Import config and check API key
    try:
        import config
        api_key = config.get_openai_api_key()
        
        if not api_key or api_key == "your-api-key-here":
            print("\n⚠️  Warning: API key not configured in config.py")
            print("   The application will start, but you'll need to:")
            print("   1. Get your OpenAI API key from: https://platform.openai.com/api-keys")
            print("   2. Enter it in the web interface, OR")
            print("   3. Edit config.py and add your key")
            print("\n   See HOW_TO_ADD_API_KEY.md for detailed instructions")
        else:
            # Mask the key for display
            masked = api_key[:10] + "..." + api_key[-4:]
            print(f"\n✅ API Key configured: {masked}")
            print(f"✅ Model: {config.OPENAI_MODEL}")
    except Exception as e:
        print(f"\n⚠️  Warning: Could not load config: {e}")
    
    print("\n" + "="*70)
    print(" 📊 Starting Web Server...")
    print("="*70)
    print("\n 🌐 Open your browser and go to:")
    print("    👉 http://localhost:5000")
    print("\n 💡 How to use:")
    print("    1. Upload your Excel or CSV file")
    print("    2. Ask questions about your data")
    print("    3. See SQL queries and results")
    print("\n 🛑 To stop the server, press Ctrl+C")
    print("="*70 + "\n")
    
    try:
        # Start the Flask application
        import web_app
        web_app.app.run(debug=False, host='0.0.0.0', port=5000)
    except KeyboardInterrupt:
        print("\n\n" + "="*70)
        print(" 👋 Server stopped. Thank you for using SQL Agent!")
        print("="*70)
        return 0
    except Exception as e:
        print(f"\n❌ Error starting server: {e}")
        print("\nTroubleshooting:")
        print("  • Make sure port 5000 is not in use")
        print("  • Check that all dependencies are installed")
        print("  • Run: pip install -r requirements_robust.txt")
        return 1

if __name__ == "__main__":
    sys.exit(main())

