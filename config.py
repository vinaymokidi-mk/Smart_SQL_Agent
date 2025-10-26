"""
Configuration file for SQL Agent
Stores API keys and application settings
"""

import os

# Gemini AI Studio API Configuration
GEMINI_API_KEY = "AIzaSyBfGENEwl3RI9kccCLredeR5bTL8_Q97kU"
GEMINI_MODEL = "models/gemini-2.5-flash"  # Fast, powerful, and free!
# Note: Gemini uses google-generativeai library, not OpenAI client

# Flask Configuration
SECRET_KEY = "your-secret-key-change-this-in-production"

# Upload Configuration
UPLOAD_FOLDER = "uploads"
MAX_FILE_SIZE = 16 * 1024 * 1024  # 16MB in bytes
ALLOWED_EXTENSIONS = {'xlsx', 'xls', 'csv'}

# Database Configuration
DATABASE_TIMEOUT = 30  # seconds

# LLM Configuration
LLM_TEMPERATURE = 0.1  # Low temperature for consistent SQL generation
LLM_MAX_TOKENS = 2000

def get_gemini_api_key():
    """
    Get Gemini API key from config or environment variable.
    Priority: Environment variable > Config file
    """
    return os.getenv('GEMINI_API_KEY', GEMINI_API_KEY)

def get_config():
    """Get all configuration as a dictionary."""
    return {
        'gemini_api_key': get_gemini_api_key(),
        'gemini_model': GEMINI_MODEL,
        'secret_key': SECRET_KEY,
        'upload_folder': UPLOAD_FOLDER,
        'max_file_size': MAX_FILE_SIZE,
        'allowed_extensions': ALLOWED_EXTENSIONS,
        'database_timeout': DATABASE_TIMEOUT,
        'llm_temperature': LLM_TEMPERATURE,
        'llm_max_tokens': LLM_MAX_TOKENS
    }

