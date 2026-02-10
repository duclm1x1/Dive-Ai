# -*- coding: utf-8 -*-
"""Simple V98 Connection Test"""

import sys
import os
sys.path.insert(0, r'D:\Antigravity\Dive-AI-v29 structle\Dive-AI-v29\src')

# Set API key
os.environ["V98_API_KEY"] = "YOUR_V98_API_KEY_HERE"

print("="*70)
print("V98 Connection Test - ConnectionV98Algorithm")
print("="*70)

# Import
print("\n[1] Importing algorithm...")
from core.algorithms.tactical.connection_v98 import get_v98_connection
print("OK - Import successful")

# Test connection
print("\n[2] Testing connection to V98 API...")
result = get_v98_connection(model="claude-opus-4-6-thinking", verify=True)

if result.status == "success":
    print(f"OK - Connection successful!")
    print(f"   Model: {result.data['selected_model']}")
    print(f"   Latency: {result.data['latency_ms']:.0f}ms")
    
    # Test actual call
    print("\n[3] Testing LLM call...")
    client = result.data["client"]
    response = client.chat_completion([
        {"role": "user", "content": "Reply: 'Dive V29.2 works!'"}
    ])
    print(f"OK - Response: {response[:100]}")
    
    print("\n"+"="*70)
    print("SUCCESS - All tests passed!")
    print("="*70)
else:
    error = result.data.get("error", "Unknown")
    print(f"FAILED - {error}")
    sys.exit(1)
