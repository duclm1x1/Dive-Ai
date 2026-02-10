# -*- coding: utf-8 -*-
"""Quick test - Ask Claude 4.6 Opus Thinking via V98"""

import sys
import os
sys.path.insert(0, r'D:\Antigravity\Dive-AI-v29 structle\Dive-AI-v29\src')

# Set API key
os.environ["V98_API_KEY"] = "YOUR_V98_API_KEY_HERE"

print("Connecting to V98 API (Claude 4.6 Opus Thinking)...")
from core.algorithms.tactical.connection_v98 import get_v98_connection

# Get connection
result = get_v98_connection(model="claude-opus-4-6-thinking", verify=False)

if result.status == "success":
    client = result.data["client"]
    print(f"Connected! Model: {result.data['selected_model']}\n")
    
    # Ask user's question
    print("Asking: 'Hello, state your version'\n")
    response = client.chat_completion([
        {"role": "user", "content": "Hello, state your version"}
    ])
    
    print("="*70)
    print("RESPONSE:")
    print("="*70)
    print(response)
    print("="*70)
else:
    print(f"Connection failed: {result.data.get('error')}")
