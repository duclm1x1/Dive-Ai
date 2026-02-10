"""
🧪 SIMPLE API CONNECTION TESTS
Direct tests for V98 and AICoding APIs based on official documentation
"""

import os
import requests

print("=" * 70)
print("🧪 DIRECT API CONNECTION TESTS")
print("=" * 70)

# Test 1: V98 Connection
print("\n[1] Testing V98Store API...")
print("    URL: https://v98store.com/v1")

v98_headers = {
    "Authorization": f"Bearer YOUR_V98_API_KEY_HERE",
    "Content-Type": "application/json"
}

try:
    response = requests.get(
        "https://v98store.com/v1/models",
        headers=v98_headers,
        timeout=10
    )
    if response.status_code == 200:
        models = response.json().get("data", [])
        print(f"    ✅ Connected! Found {len(models)} models")
        
        # Find specific models
        model_ids = [m.get("id", "") for m in models]
        claude = [m for m in model_ids if "claude-opus-4-6" in m]
        gpt_codex = [m for m in model_ids if "gpt-5.1-codex" in m]
        glm = [m for m in model_ids if "glm-4.6" in m]
        
        print(f"    📊 Claude Opus 4-6: {claude[:3] if claude else 'Not found'}")
        print(f"    📊 GPT-5.1-Codex: {gpt_codex[:3] if gpt_codex else 'Not found'}")
        print(f"    📊 GLM-4.6: {glm[:3] if glm else 'Not found'}")
    else:
        print(f"    ❌ Failed: HTTP {response.status_code}")
except Exception as e:
    print(f"    ❌ Error: {e}")

# Test 2: V98 Chat Completion
print("\n[2] Testing V98 Chat Completion...")

try:
    response = requests.post(
        "https://v98store.com/v1/chat/completions",
        headers=v98_headers,
        json={
            "model": "gpt-4o",
            "messages": [
                {"role": "user", "content": "Say 'Hello V98' and nothing else."}
            ],
            "max_tokens": 20
        },
        timeout=30
    )
    
    if response.status_code == 200:
        data = response.json()
        content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
        print(f"    ✅ Response: {content}")
    else:
        print(f"    ❌ Failed: HTTP {response.status_code}")
        print(f"       {response.text[:200]}")
except Exception as e:
    print(f"    ❌ Error: {e}")

# Test 3: AICoding Connection
print("\n[3] Testing AICoding API...")
print("    URL: https://aicoding.io.vn")

aicoding_headers = {
    "Authorization": f"Bearer YOUR_AICODING_API_KEY_HERECJCk",
    "Content-Type": "application/json",
    "anthropic-version": "2023-06-01"
}

# Try health endpoint
try:
    response = requests.get(
        "https://aicoding.io.vn/health",
        headers=aicoding_headers,
        timeout=10
    )
    if response.status_code == 200:
        print(f"    ✅ Health check passed")
    else:
        print(f"    ⚠️  Health: HTTP {response.status_code}")
except Exception as e:
    print(f"    ⚠️  Health check error: {e}")

# Test 4: AICoding Anthropic Messages
print("\n[4] Testing AICoding Anthropic Format...")

try:
    response = requests.post(
        "https://aicoding.io.vn/v1/messages",
        headers=aicoding_headers,
        json={
            "model": "claude-sonnet-4-5-20250929",
            "max_tokens": 20,
            "messages": [
                {"role": "user", "content": "Say 'Hello AICoding' and nothing else."}
            ]
        },
        timeout=30
    )
    
    if response.status_code == 200:
        data = response.json()
        content = data.get("content", [{}])[0].get("text", "")
        print(f"    ✅ Response: {content}")
    else:
        print(f"    ❌ Failed: HTTP {response.status_code}")
        print(f"       {response.text[:200]}")
except Exception as e:
    print(f"    ❌ Error: {e}")

print("\n" + "=" * 70)
print("✅ Tests Complete!")
print("=" * 70)
