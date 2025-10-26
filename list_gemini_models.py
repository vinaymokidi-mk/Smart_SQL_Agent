#!/usr/bin/env python3
"""
List available Gemini models
"""

import google.generativeai as genai
import config

# Configure API key
genai.configure(api_key=config.get_gemini_api_key())

print("="*60)
print("Available Gemini Models:")
print("="*60)

for model in genai.list_models():
    if 'generateContent' in model.supported_generation_methods:
        print(f"\n✓ {model.name}")
        print(f"  Display Name: {model.display_name}")
        print(f"  Description: {model.description}")

