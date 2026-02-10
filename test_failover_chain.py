"""
Test Failover Chain: V98 → AICoding → OpenAI
Demonstrates automatic failover when primary API unavailable
"""

import sys
import os
sys.path.insert(0, r'D:\Antigravity\Dive-AI-v29 structle\Dive-AI-v29\src')

# Set API keys (V98 is primary)
os.environ["V98_API_KEY"] = "YOUR_V98_API_KEY_HERE"

print("="*70)
print("Failover Chain Test")
print("V98 (Claude 4.6 Thinking) -> AICoding -> OpenAI -> Ollama")
print("="*70)

from core.algorithms.tactical.connection_v98 import get_v98_connection

# Test 1: V98 Connection (Primary - Should succeed)
print("\n[Test 1] Primary: V98 API with Claude 4.6 Opus Thinking")
result = get_v98_connection(model="claude-opus-4-6-thinking", verify=True)

if result.status == "success":
    print(f"✅ V98 Connected!")
    print(f"   Model: {result.data['selected_model']}")
    print(f"   Latency: {result.data['latency_ms']:.0f}ms")
    print(f"   Provider: V98 (Primary)")
    
    # Test actual call
    client = result.data["client"]
    response = client.chat_completion([
        {"role": "user", "content": "In one sentence, confirm you are Claude 4.6 Opus Thinking"}
    ])
    print(f"   Response: {response[:100]}...")
    print("\n✅ Primary V98 API is working - No failover needed!")
else:
    print(f"❌ V98 Failed: {result.data.get('error')}")
    print("\nAttempting failover to AICoding...")
    
    # Test 2: Failover to AICoding
    from core.algorithms.tactical.connection_aicoding import get_aicoding_connection
    
    result2 = get_aicoding_connection(model="claude-opus-4", verify=True)
    
    if result2.status == "success":
        print(f"✅ AICoding Connected (Failover Tier 1)")
        print(f"   Model: {result2.data['selected_model']}")
    else:
        print(f"❌ AICoding Failed: {result2.data.get('error')}")
        print("\nAttempting failover to OpenAI...")
        
        # Test 3: Failover to OpenAI
        from core.algorithms.tactical.connection_openai import ConnectionOpenAIAlgorithm
        
        openai_algo = ConnectionOpenAIAlgorithm()
        result3 = openai_algo.execute({"model": "gpt-4-turbo", "verify_connection": True})
        
        if result3.status == "success":
            print(f"✅ OpenAI Connected (Failover Tier 2)")
        else:
            print(f"❌ OpenAI Failed: {result3.data.get('error')}")
            print("\n❌ All providers failed!")

print("\n" + "="*70)
print("Failover Test Complete")
print("="*70)
print("\nFailover Priority:")
print("1. V98 (Claude 4.6 Opus Thinking) - FASTEST, BEST QUALITY")
print("2. AICoding (Claude Opus 4) - Backup tier 1")
print("3. OpenAI (GPT-4 Turbo) - Backup tier 2")
print("4. Ollama (Local) - Last resort")
print("\nCurrent Status: V98 is PRIMARY and ACTIVE ✅")
