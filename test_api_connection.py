#!/usr/bin/env python3
"""
Test script to verify API key connection
Tests the configured API key from config.py
"""

import sys
from utils import call_llm
import config

def test_api_connection():
    """Test the API connection with the configured key."""
    print("="*60)
    print("Testing API Connection")
    print("="*60)
    
    # Get API key from config
    api_key = config.get_gemini_api_key()
    
    if not api_key:
        print("❌ Error: No API key configured in config.py")
        return False
    
    # Mask the API key for display
    masked_key = api_key[:15] + "..." + api_key[-4:]
    print(f"\n✓ API Key loaded: {masked_key}")
    print(f"✓ Model: {config.GEMINI_MODEL}")
    
    # Test the connection
    print(f"\n🔄 Testing connection to Google Gemini API...")
    print(f"   Provider: Google AI Studio (Free Tier)")
    
    try:
        response = call_llm("Say 'Hello! API connection successful.'")
        
        print(f"\n✅ SUCCESS! API is working!")
        print(f"Response: {response}")
        print("\n" + "="*60)
        print("Your API key is properly configured!")
        print("You can now run the application:")
        print("  python web_app.py")
        print("="*60)
        return True
        
    except Exception as e:
        import traceback
        error_msg = str(e)
        print(f"\n❌ FAILED! Error: {error_msg}")
        print(f"\nFull error details:")
        traceback.print_exc()
        
        if 'invalid' in error_msg.lower() or '400' in error_msg:
            print("\n💡 Possible issues:")
            print("   1. The API key might be invalid or expired")
            print("   2. Get a new key from: https://aistudio.google.com/app/apikey")
            print("   3. Make sure the key is correctly copied")
            print("   4. Check if API access is enabled in your Google account")
        elif 'rate limit' in error_msg.lower():
            print("\n💡 Rate limit exceeded.")
            print("   Please wait a moment and try again.")
        elif 'quota' in error_msg.lower():
            print("\n💡 API quota exceeded.")
            print("   Check your usage at: https://aistudio.google.com/")
        
        print("\n" + "="*60)
        return False

def main():
    """Main entry point."""
    success = test_api_connection()
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())

