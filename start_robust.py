#!/usr/bin/env python3
"""
Startup script for SQL Agent Robust Application
Checks environment and starts the web server.
"""

import os
import sys
import subprocess

def check_python_version():
    """Check if Python version is 3.8 or higher."""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Error: Python 3.8 or higher is required")
        print(f"   Current version: {version.major}.{version.minor}.{version.micro}")
        return False
    print(f"✅ Python version: {version.major}.{version.minor}.{version.micro}")
    return True

def check_dependencies():
    """Check if required dependencies are installed."""
    required_packages = {
        'flask': 'Flask',
        'pandas': 'pandas',
        'openai': 'openai',
        'werkzeug': 'werkzeug',
        'yaml': 'PyYAML',
        'openpyxl': 'openpyxl'
    }
    
    missing = []
    for module, package in required_packages.items():
        try:
            __import__(module)
            print(f"✅ {package} installed")
        except ImportError:
            missing.append(package)
            print(f"❌ {package} not found")
    
    if missing:
        print("\n❌ Missing dependencies. Install with:")
        print(f"   pip install {' '.join(missing)}")
        return False
    
    return True

def check_directories():
    """Create necessary directories if they don't exist."""
    directories = ['uploads', 'templates']
    for directory in directories:
        if not os.path.exists(directory):
            try:
                os.makedirs(directory)
                print(f"✅ Created directory: {directory}")
            except Exception as e:
                print(f"❌ Failed to create directory {directory}: {e}")
                return False
        else:
            print(f"✅ Directory exists: {directory}")
    return True

def check_files():
    """Check if required files exist."""
    required_files = {
        'web_app.py': 'Main application file',
        'utils.py': 'Utility functions',
        'templates/index.html': 'Web interface'
    }
    
    for file_path, description in required_files.items():
        if not os.path.exists(file_path):
            print(f"❌ Missing file: {file_path} ({description})")
            return False
        print(f"✅ Found: {file_path}")
    
    return True

def check_api_key():
    """Check if OpenAI API key is set."""
    api_key = os.getenv('OPENAI_API_KEY')
    if api_key:
        print(f"✅ OpenAI API key is set (length: {len(api_key)})")
        return True
    else:
        print("⚠️  Warning: OPENAI_API_KEY environment variable not set")
        print("   You can set it in the web interface, or export it:")
        print("   export OPENAI_API_KEY='your-api-key-here'")
        return True  # Not critical, can be set in UI

def start_application():
    """Start the Flask application."""
    print("\n" + "="*60)
    print("🚀 Starting SQL Agent Robust Application")
    print("="*60)
    
    # Run all checks
    checks = [
        ("Python Version", check_python_version),
        ("Dependencies", check_dependencies),
        ("Directories", check_directories),
        ("Required Files", check_files),
        ("API Key", check_api_key)
    ]
    
    print("\n📋 Pre-flight Checks:\n")
    
    all_passed = True
    for check_name, check_func in checks:
        print(f"\n{check_name}:")
        if not check_func():
            all_passed = False
    
    if not all_passed:
        print("\n" + "="*60)
        print("❌ Pre-flight checks failed. Please fix the errors above.")
        print("="*60)
        return 1
    
    print("\n" + "="*60)
    print("✅ All pre-flight checks passed!")
    print("="*60)
    
    print("\n🌐 Starting web server...")
    print("📊 Open your browser and navigate to:")
    print("   → http://localhost:5000")
    print("\n💡 To stop the server, press Ctrl+C")
    print("="*60 + "\n")
    
    try:
        # Start the Flask application
        import web_app
        web_app.app.run(debug=True, host='0.0.0.0', port=5000)
    except KeyboardInterrupt:
        print("\n\n" + "="*60)
        print("👋 Server stopped by user")
        print("="*60)
        return 0
    except Exception as e:
        print(f"\n❌ Error starting server: {e}")
        return 1

def main():
    """Main entry point."""
    return start_application()

if __name__ == "__main__":
    sys.exit(main())

