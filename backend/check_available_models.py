#!/usr/bin/env python3
"""Check which Gemini models are available with the current API key"""

import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv('GEMINI_API_KEY')

if not api_key:
    print("❌ No GEMINI_API_KEY found in .env")
    exit(1)

print(f"🔑 Using API Key: {api_key[:20]}...")
print("\n" + "="*60)
print("Available Gemini Models:")
print("="*60)

try:
    genai.configure(api_key=api_key)
    
    models = genai.list_models()
    
    gemini_models = []
    for model in models:
        if 'generateContent' in model.supported_generation_methods:
            gemini_models.append(model.name)
            print(f"✅ {model.name}")
            print(f"   Display Name: {model.display_name}")
            print(f"   Description: {model.description[:100]}...")
            print()
    
    if not gemini_models:
        print("❌ No models found that support generateContent")
    else:
        print("="*60)
        print(f"\n✅ Found {len(gemini_models)} available model(s)")
        print("\nRecommended model to use in .env:")
        print(f"GEMINI_MODEL={gemini_models[0].replace('models/', '')}")
        
except Exception as e:
    print(f"❌ Error: {e}")
    print("\nThis might mean:")
    print("1. API key is invalid")
    print("2. Generative Language API is not enabled")
    print("3. API key doesn't have proper permissions")
    print("\nTry:")
    print("- Go to https://makersuite.google.com/app/apikey")
    print("- Create a NEW API key")
    print("- Make sure 'Generative Language API' is enabled")
