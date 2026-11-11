#!/usr/bin/env python3
"""Test OpenRouter API directly"""
import requests

import os
# Set OPENROUTER_API_KEY_1 and OPENROUTER_API_KEY_2 in your .env file
API_KEY_1 = os.environ.get("OPENROUTER_API_KEY_1", "your-openrouter-api-key-1-here")
API_KEY_2 = os.environ.get("OPENROUTER_API_KEY_2", "your-openrouter-api-key-2-here")

headers_1 = {
    "Authorization": f"Bearer {API_KEY_1}",
    "Content-Type": "application/json",
    "HTTP-Referer": "http://localhost",
    "X-Title": "DevOps Agent"
}

headers_2 = {
    "Authorization": f"Bearer {API_KEY_2}",
    "Content-Type": "application/json",
    "HTTP-Referer": "http://localhost",
    "X-Title": "DevOps Agent"
}

payload = {
    "model": "x-ai/grok-beta",  # Try grok-beta instead
    "messages": [{"role": "user", "content": "Say hi in 3 words"}],
    "max_tokens": 20
}

print("Testing OpenRouter API Key #1...")
try:
    r = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers_1, json=payload, timeout=10)
    print(f"Status: {r.status_code}")
    print(f"Response: {r.text[:500]}")
except Exception as e:
    print(f"Error: {e}")

print("\nTesting OpenRouter API Key #2...")
try:
    r = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers_2, json=payload, timeout=10)
    print(f"Status: {r.status_code}")
    print(f"Response: {r.text[:500]}")
except Exception as e:
    print(f"Error: {e}")
